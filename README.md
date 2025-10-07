# AI Agent

=================================================================

Use Case: A Streamlit web application that generates social media content based on YouTube video transcripts using OpenAI's GPT models.

=================================================================


**PROMPTS** 
LAYER 1 - **Input Understanding**
User will be asking to generate a social media post based on my provided video transcript.

 '''Here is a new video transcript:video_transcript
    Generate a social media post based on my provided video transcript. '''

LAYER 2 - **Task Planer**
Model used - 'gpt-4o-mini'
Instruction will be given to the model to provide the valuable data.

'''You are a talented content writer who writes engaging, humorous, informative and 
    highly readable social media posts. 
    You will be given a video transcript and social media platforms. 
    You will generate a social media post based on the video transcript 
    and the social media platforms.
    You may search the web for up-to-date information on the topic and 
    fill in some useful details if needed.'''

Thus, we creatd our first tool.

LAYER 3 - **Output Generator**
By applying checks:
1. The youtube id is fetched properly or not.
2. The model is available or not.
3. The API key is present.









**Streamlit**
Then provide a better interface Streamlit is used.




