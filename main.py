
# --------------------------------------------------------------
# Step 0: Import packages and modules
# --------------------------------------------------------------
import asyncio
import os
from youtube_transcript_api import YouTubeTranscriptApi
from agents import Agent, Runner, function_tool, ItemHelpers, trace
import google.generativeai as genai
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import List

# --------------------------------------------------------------
# Step 1: Get Gemini API key
# --------------------------------------------------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Gemini client
genai.configure(api_key=GEMINI_API_KEY)


# --------------------------------------------------------------
# Step 2: Define tools for agent
# --------------------------------------------------------------

# Tool: Generate social media content from transcript
@function_tool
@function_tool
def generate_content(video_transcript: str, social_media_platform: str):
    print(f"Generating social media content for {social_media_platform}...")
    
    prompt = f"""You are a talented social media content writer.

Here is a video transcript:
{video_transcript}

Generate an engaging {social_media_platform} post based on this transcript. 
Make it catchy, shareable, and appropriate for the platform."""
    
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    response = model.generate_content(prompt)
    
    return response.text


# --------------------------------------------------------------
# Step 3: Define agent (content writer agent)
# --------------------------------------------------------------

@dataclass
class Post:
    platform: str
    content: str

content_writer_agent = Agent(
    name="Content Writer Agent",
    instructions="""You are a talented content writer who writes engaging, humorous, informative and 
                    highly readable social media posts. 
                    You will be given a video transcript and social media platforms. 
                    You will generate a social media post based on the video transcript 
                    and the social media platforms.
                    
                    Format your response clearly with:
                    Platform: [name]
                    Content: [post]""",
    model="gemini-2.0-flash-exp",  # FREE Gemini model
    tools=[generate_content],
    # Removed output_type to avoid compatibility issues
)

# --------------------------------------------------------------
# Step 4: Define helper functions
# --------------------------------------------------------------

# Fetch transcript from a youtube video using the video id
def get_transcript(video_id: str, languages: list = None) -> str:
    """
    Retrieves the transcript for a YouTube video.
    """
    if languages is None:
        languages = ["en"]
    
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
        transcript_text = " ".join([item['text'] for item in transcript_list])
        return transcript_text
    
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        raise

# --------------------------------------------------------------
# Step 5: Run the agent
# --------------------------------------------------------------
async def main():
    video_id = "OZ5OZZZ2cvk"
    transcript = get_transcript(video_id)
    
    # Truncate transcript for better results
    transcript_short = transcript[:4000] if len(transcript) > 4000 else transcript
    
    msg = f"Generate a LinkedIn post and an Instagram caption based on this video transcript: {transcript_short}"
    
    # Package input for the agent
    input_items = [{"content": msg, "role": "user"}]
    
    # Run content writer agent
    with trace("Writing content"):
        result = await Runner.run(content_writer_agent, input_items)
