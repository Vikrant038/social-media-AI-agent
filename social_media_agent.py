# --------------------------------------------------------------
# social_media_agent.py
# --------------------------------------------------------------
import os
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    RequestBlocked,
    IpBlocked,
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
    InvalidVideoId,
)
from youtube_transcript_api.proxies import WebshareProxyConfig, GenericProxyConfig
import google.generativeai as genai
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import List, Dict, Optional
import json
import re


class TranscriptError(Exception):
    """User-facing transcript error with a clear, actionable message."""


# --------------------------------------------------------------
# Load API key (Streamlit secrets first, then environment / .env)
# --------------------------------------------------------------
load_dotenv()


def _load_api_key() -> str:
    """Resolve the Gemini API key from st.secrets or the environment."""
    try:
        import streamlit as st  # optional: only available when run via Streamlit
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    return os.getenv("GEMINI_API_KEY", "")


GEMINI_API_KEY = _load_api_key()
# True when the deployment ships its own key (users need not bring their own).
HAS_SERVER_KEY = bool(GEMINI_API_KEY)
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


def _secret(name: str) -> str:
    """Read a config value from st.secrets first, then the environment."""
    try:
        import streamlit as st
        if name in st.secrets:
            return str(st.secrets[name])
    except Exception:
        pass
    return os.getenv(name, "")


def _build_proxy_config():
    """
    Build a proxy config to work around YouTube IP bans, if configured.

    Supports either Webshare (recommended) or a generic HTTP/HTTPS proxy via
    st.secrets or environment variables:
      - WEBSHARE_PROXY_USERNAME / WEBSHARE_PROXY_PASSWORD
      - HTTP_PROXY_URL / HTTPS_PROXY_URL
    Returns None when nothing is configured (direct connection).
    """
    ws_user = _secret("WEBSHARE_PROXY_USERNAME")
    ws_pass = _secret("WEBSHARE_PROXY_PASSWORD")
    if ws_user and ws_pass:
        return WebshareProxyConfig(proxy_username=ws_user, proxy_password=ws_pass)

    http_url = _secret("HTTP_PROXY_URL")
    https_url = _secret("HTTPS_PROXY_URL")
    if http_url or https_url:
        return GenericProxyConfig(
            http_url=http_url or https_url,
            https_url=https_url or http_url,
        )
    return None


# --------------------------------------------------------------
# Data Classes
# --------------------------------------------------------------
@dataclass
class Post:
    platform: str
    content: str


@dataclass
class AgentResult:
    posts: List[Post]
    raw_response: str


# --------------------------------------------------------------
# Model selection
# --------------------------------------------------------------
# Preferred models, best first. We pick the first one the account can actually
# use so a retired model id (e.g. the old gemini-2.0-flash-exp) never 404s.
PREFERRED_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-flash-latest",
    "gemini-1.5-flash",
]


def select_model_name() -> str:
    """Return an available model that supports generateContent."""
    try:
        available = [
            m.name.split("/")[-1]
            for m in genai.list_models()
            if "generateContent" in getattr(m, "supported_generation_methods", [])
        ]
    except Exception:
        # If listing fails, fall back to the top preferred id and let the call surface errors.
        return PREFERRED_MODELS[0]

    for preferred in PREFERRED_MODELS:
        if preferred in available:
            return preferred
    # Otherwise prefer any "flash" model, else the first available one.
    for name in available:
        if "flash" in name and "exp" not in name:
            return name
    return available[0] if available else PREFERRED_MODELS[0]


# --------------------------------------------------------------
# Helper Functions
# --------------------------------------------------------------
def get_transcript(video_id: str, languages: list = None) -> str:
    """
    Retrieve a YouTube transcript, routing through a proxy if configured, and
    translate library errors into clear, user-facing messages.
    """
    if languages is None:
        languages = ["en"]

    proxy_config = _build_proxy_config()
    try:
        ytt_api = YouTubeTranscriptApi(proxy_config=proxy_config)
        fetched_transcript = ytt_api.fetch(video_id, languages=languages)
        transcript_data = fetched_transcript.to_raw_data()
        return " ".join(item["text"] for item in transcript_data)

    except (RequestBlocked, IpBlocked):
        if proxy_config is None:
            raise TranscriptError(
                "YouTube is temporarily blocking transcript requests from this "
                "network (common on cloud/shared IPs or after many requests). "
                "Wait a few minutes and retry, or configure a proxy "
                "(WEBSHARE_PROXY_USERNAME / WEBSHARE_PROXY_PASSWORD) — see the README."
            )
        raise TranscriptError(
            "YouTube blocked the request even through the configured proxy. "
            "The proxy may be exhausted or itself blocked; try different proxy "
            "credentials."
        )
    except (TranscriptsDisabled, NoTranscriptFound):
        raise TranscriptError(
            "This video has no available transcript/captions in the requested "
            "language. Try a different video or one with captions enabled."
        )
    except InvalidVideoId:
        raise TranscriptError(
            "That doesn't look like a valid YouTube video ID. Enter just the ID "
            "(the part after 'v=' in the URL), not the full link."
        )
    except VideoUnavailable:
        raise TranscriptError(
            "This video is unavailable (private, deleted, or region-locked)."
        )


def _cached_get_transcript(video_id: str) -> str:
    """Transcript fetch, cached by Streamlit when available to avoid refetching."""
    try:
        import streamlit as st
        fetch = st.cache_data(show_spinner=False)(get_transcript)
    except Exception:
        fetch = get_transcript  # Streamlit unavailable; fetch directly (uncached).
    return fetch(video_id)


def _strip_code_fences(text: str) -> str:
    """Remove a surrounding Markdown code fence (```json ... ``` or ``` ... ```)."""
    text = text.strip()
    # Drop an opening fence such as ```json or ``` on the first line.
    text = re.sub(r"^```[a-zA-Z0-9]*\s*\n?", "", text)
    # Drop a trailing closing fence.
    text = re.sub(r"\n?```\s*$", "", text)
    return text.strip()


def _build_example_structure(platforms: List[str]) -> str:
    """Build a JSON example that lists ONLY the requested platforms."""
    items = [
        f'  {{"platform": "{p}", "content": "your {p} post here"}}'
        for p in platforms
    ]
    return "[\n" + ",\n".join(items) + "\n]"


# Per-platform writing guidance so each post follows that network's conventions
# (length, tone, hashtags, emoji, CTA) instead of generic "make it engaging" text.
PLATFORM_SPECS = {
    "LinkedIn": (
        "Professional, insight-driven thought-leadership. Open with a strong hook line, "
        "use short paragraphs, end with a question or call-to-action, and add 3-5 relevant "
        "hashtags. ~150-250 words. Minimal or no emoji."
    ),
    "Instagram": (
        "Casual, visual and punchy caption. Start with an attention-grabbing first line, "
        "use tasteful emoji, keep it scannable, end with a CTA, and add 8-12 niche hashtags "
        "on a new line. ~80-150 words."
    ),
    "Twitter": (
        "A single concise tweet UNDER 280 characters total (including hashtags). Punchy, "
        "one clear idea, 1-3 hashtags max. No thread."
    ),
    "Facebook": (
        "Conversational and community-oriented. A relatable hook, 2-4 short sentences, an "
        "inviting question to drive comments, and 0-2 hashtags. ~60-120 words."
    ),
}


def _build_platform_guidance(platforms: List[str]) -> str:
    """Bullet list of per-platform rules for the requested platforms."""
    return "\n".join(
        f"- {p}: {PLATFORM_SPECS.get(p, 'Engaging, platform-appropriate content.')}"
        for p in platforms
    )


def generate_social_content(
    transcript: str,
    platforms: List[str],
    custom_query: str = None,
    api_key: str = None,
) -> AgentResult:
    """
    Generate social media content using Gemini for the EXACTLY selected platforms.

    Args:
        api_key: Optional user-supplied Gemini key (bring-your-own-key). When
                 provided it overrides the server's configured key for this call.
    """
    active_key = api_key or GEMINI_API_KEY
    if not active_key:
        raise RuntimeError(
            "Gemini API key not configured. Enter your own key in the sidebar, "
            "or set GEMINI_API_KEY in .streamlit/secrets.toml or the environment."
        )
    # Configure for this call (BYOK keys are never persisted server-side).
    genai.configure(api_key=active_key)

    platforms_str = ", ".join(platforms)
    example_structure = _build_example_structure(platforms)
    guidance = _build_platform_guidance(platforms)

    # Shared, strict constraint so the model never invents extra platforms.
    constraint = (
        f"Generate one post for EACH of these platforms and NO others: {platforms_str}.\n"
        f"Return a JSON array containing EXACTLY {len(platforms)} object(s), "
        f"one per platform listed above, using the exact platform names given."
    )

    extra_instructions = (
        f"\n\nAdditional user instructions (apply these too):\n{custom_query}"
        if custom_query else ""
    )

    prompt = f"""You are an expert social media content strategist. Using the key insights \
from the video transcript below, write ready-to-publish posts.

Video Transcript:
{transcript}

{constraint}

Follow these platform-specific rules precisely:
{guidance}

General rules:
- Base the content on the actual insights in the transcript; do not invent facts.
- Make each post self-contained and ready to publish as-is.
- Respect the length limits above (especially Twitter's 280-character cap).{extra_instructions}

Return your response as a JSON array with this exact structure:
{example_structure}"""

    model = genai.GenerativeModel(select_model_name())
    # Native JSON mode: forces syntactically valid JSON, removing the fragile
    # code-fence stripping that could break parsing.
    try:
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"},
        )
    except Exception:
        # Older models may not support JSON mode; fall back to a plain call.
        response = model.generate_content(prompt)

    # Parse the response
    try:
        response_text = _strip_code_fences(response.text)
        posts_data = json.loads(response_text)

        # Convert to Post objects, keyed by platform for filtering.
        parsed = {
            p["platform"]: p["content"]
            for p in posts_data
            if isinstance(p, dict) and "platform" in p and "content" in p
        }

        # Defensive guard: keep ONLY the platforms the user selected, in order.
        # Match case-insensitively so "twitter" maps to a requested "Twitter".
        lookup = {k.lower(): v for k, v in parsed.items()}
        posts = []
        for platform in platforms:
            content = lookup.get(platform.lower())
            if content:
                posts.append(Post(platform=platform, content=content))

        # If the model returned nothing usable for the selected platforms, fall back.
        if not posts:
            return AgentResult(
                posts=[Post(platform="Generated Content", content=response.text)],
                raw_response=response.text,
            )

        return AgentResult(posts=posts, raw_response=response.text)

    except json.JSONDecodeError:
        # Fallback: return raw text as a single post (no data leaked to stdout).
        return AgentResult(
            posts=[Post(platform="Generated Content", content=response.text)],
            raw_response=response.text
        )


# --------------------------------------------------------------
# ItemHelpers Alternative (for Streamlit compatibility)
# --------------------------------------------------------------
class ItemHelpers:
    """Helper class to mimic OpenAI Agents SDK ItemHelpers functionality."""
    
    @staticmethod
    def format_posts_as_json(posts: List[Post]) -> str:
        """Convert posts to JSON string format."""
        posts_dict = [{"platform": p.platform, "content": p.content} for p in posts]
        return json.dumps({"response": posts_dict}, indent=2)


# --------------------------------------------------------------
# Runner Alternative
# --------------------------------------------------------------
class Runner:
    """Simple runner to replace OpenAI's Runner."""
    
    @staticmethod
    def run(
        video_id: str,
        platforms: List[str],
        custom_query: str = None,
        api_key: str = None,
    ) -> AgentResult:
        """
        Run the content generation process.

        Args:
            video_id: YouTube video ID
            platforms: List of platform names
            custom_query: Optional custom query from user
            api_key: Optional user-supplied Gemini key (bring-your-own-key)

        Returns:
            AgentResult with generated posts
        """
        # Get transcript (cached when running under Streamlit)
        transcript = _cached_get_transcript(video_id)

        # Truncate if too long
        transcript_short = transcript[:4000] if len(transcript) > 4000 else transcript

        # Generate content
        result = generate_social_content(
            transcript_short, platforms, custom_query, api_key=api_key
        )

        return result


# --------------------------------------------------------------
# Main execution (for testing)
# --------------------------------------------------------------
if __name__ == "__main__":
    video_id = "OZ5OZZZ2cvk"
    platforms = ["LinkedIn", "Instagram", "Twitter"]
    
    print(f"Fetching transcript for video: {video_id}")
    result = Runner.run(video_id, platforms)
    
    print("\n" + "="*70)
    print("GENERATED CONTENT:")
    print("="*70)
    
    for post in result.posts:
        print(f"\n{post.platform}:")
        print("-" * 70)
        print(post.content)
        print("-" * 70)
