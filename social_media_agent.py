# --------------------------------------------------------------
# social_media_agent.py
# --------------------------------------------------------------
import os
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import List, Dict
import json
import re


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
    Retrieves the transcript for a YouTube video using the new API interface.
    """
    if languages is None:
        languages = ["en"]
    
    try:
        ytt_api = YouTubeTranscriptApi()
        fetched_transcript = ytt_api.fetch(video_id, languages=languages)
        transcript_data = fetched_transcript.to_raw_data()
        transcript_text = " ".join([item['text'] for item in transcript_data])
        return transcript_text
    except Exception:
        # Re-raise so the UI can surface a friendly message; avoid leaking to stdout.
        raise


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

    # Shared, strict constraint so the model never invents extra platforms.
    constraint = (
        f"Generate one post for EACH of these platforms and NO others: {platforms_str}.\n"
        f"Return a JSON array containing EXACTLY {len(platforms)} object(s), "
        f"one per platform listed above, using the exact platform names given."
    )

    if custom_query:
        prompt = f"""{custom_query}

Video Transcript:
{transcript}

{constraint}

For each platform, provide engaging content optimized for that platform.

Return your response as a JSON array with this exact structure:
{example_structure}

Make the content platform-appropriate, engaging, and shareable. Return ONLY the JSON array."""
    else:
        prompt = f"""You are a talented social media content writer.

Video Transcript:
{transcript}

{constraint}

For each platform, create content that is:
- Platform-appropriate (LinkedIn: professional, Instagram: visual/casual, Twitter: concise, Facebook: conversational)
- Engaging and shareable
- Based on the key insights from the transcript

Return your response as a JSON array with this exact structure:
{example_structure}

Return ONLY the JSON array."""

    model = genai.GenerativeModel(select_model_name())
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
