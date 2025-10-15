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


# --------------------------------------------------------------
# Load environment variables
# --------------------------------------------------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
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
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        raise


def generate_social_content(transcript: str, platforms: List[str], custom_query: str = None) -> AgentResult:
    """
    Generate social media content using Gemini for multiple platforms.
    """
    platforms_str = ", ".join(platforms)
    
    if custom_query:
        prompt = f"""{custom_query}

Video Transcript:
{transcript}

Generate engaging social media posts for the following platforms: {platforms_str}

For each platform, provide:
1. Platform name
2. Engaging content optimized for that platform

Return your response as a JSON array with this structure:
[
  {{"platform": "LinkedIn", "content": "your LinkedIn post here"}},
  {{"platform": "Instagram", "content": "your Instagram caption here"}},
  {{"platform": "Twitter", "content": "your tweet here"}}
]

Make the content platform-appropriate, engaging, and shareable."""
    else:
        prompt = f"""You are a talented social media content writer.

Video Transcript:
{transcript}

Generate engaging social media posts for the following platforms: {platforms_str}

For each platform, create content that is:
- Platform-appropriate (LinkedIn: professional, Instagram: visual/casual, Twitter: concise)
- Engaging and shareable
- Based on the key insights from the transcript

Return your response as a JSON array with this structure:
[
  {{"platform": "LinkedIn", "content": "your LinkedIn post here"}},
  {{"platform": "Instagram", "content": "your Instagram caption here"}},
  {{"platform": "Twitter", "content": "your tweet here"}}
]"""
    
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    response = model.generate_content(prompt)
    
    # Parse the response
    try:
        # Extract JSON from response
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text.replace("``````", "").strip()
        elif response_text.startswith("```"):
            response_text = response_text.replace("```", "").strip()
        
        # Parse JSON
        posts_data = json.loads(response_text)
        
        # Convert to Post objects
        posts = [Post(platform=p["platform"], content=p["content"]) for p in posts_data]
        
        return AgentResult(posts=posts, raw_response=response.text)
    
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON response: {e}")
        print(f"Raw response: {response.text}")
        
        # Fallback: return raw text as a single post
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
    def run(video_id: str, platforms: List[str], custom_query: str = None) -> AgentResult:
        """
        Run the content generation process.
        
        Args:
            video_id: YouTube video ID
            platforms: List of platform names
            custom_query: Optional custom query from user
            
        Returns:
            AgentResult with generated posts
        """
        # Get transcript
        transcript = get_transcript(video_id)
        
        # Truncate if too long
        transcript_short = transcript[:4000] if len(transcript) > 4000 else transcript
        
        # Generate content
        result = generate_social_content(transcript_short, platforms, custom_query)
        
        return result


# --------------------------------------------------------------
# Main execution (for testing)
# --------------------------------------------------------------
if __name__ == "__main__":
    video_id = "OZ5OZZZ2cvk"
    platforms = ["LinkedIn", "Instagram", "Twitter"]
    
    print(f"📹 Fetching transcript for video: {video_id}")
    result = Runner.run(video_id, platforms)
    
    print("\n" + "="*70)
    print("GENERATED CONTENT:")
    print("="*70)
    
    for post in result.posts:
        print(f"\n{post.platform}:")
        print("-" * 70)
        print(post.content)
        print("-" * 70)
