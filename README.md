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

LLM Models Use:
**1**.What is virtual environment in python, how to implement it
      - A Python virtual environment is an isolated workspace that has its own Python interpreter and site-packages, so each project can use specific dependency versions without affecting other projects or the system Python. This prevents version conflicts, keeps projects reproducible, and makes collaboration and deployment cleaner.

When to use it
Working on multiple projects that require different library versions.
Keeping the system/global Python clean and avoiding permission issues.
Ensuring consistent, reproducible environments across machines.

Create:

Windows:
Command Prompt:
Navigate to project folder
python -m venv .venv

PowerShell:
cd to project folder

**2** 
<img width="1085" height="759" alt="image" src="https://github.com/user-attachments/assets/2ad9b385-d1e4-41c9-b644-648ba3f3f180" />

**3**
<img width="864" height="768" alt="image" src="https://github.com/user-attachments/assets/c2c2c3fc-cc92-4c23-937d-072505bddf58" />

--------------------------------
<img width="851" height="785" alt="image" src="https://github.com/user-attachments/assets/bececd3a-f098-4985-9172-b067b63dbf4d" />

After that I took help from youtube by watching the video and learning the concepts of virtual environment, the libraries that one have to install while building a AI agent.
From there step by step I wrote the code while the understanding the us case of it as well, it was a little new, but I tried to grasp all the things that I could and learn so many things in this project.

1. How to integrate AI in python.
2. Creating virtual environment so that it won't affect ur current python system.
3. AI can be used to automate our most basics task which can improve time management and efficiency.
4. Use case of StreamLit.
5. Learnt about offline LLM models which you can install on your PC and they are free to use once you have download the model you want to use on you rPC locally.
   
 **Challenges**
 In this project, it was my first time integrating AI in python.
 The problems that I face are listed down -:

1. I was trying to fetch the video id from the url,then after some trial and error, using the Video ID directly to the input improved my proccessing time and generating the output more efficiently as it directly uses the ID.
2. 










**Streamlit**
Then provide a better interface Streamlit is used.




