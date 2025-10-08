

# AI Agent: YouTube Transcript-Based Social Media Content Generator

***

## Overview

This project is a **Streamlit web application** that creates social media posts using YouTube video transcripts. It leverages OpenAI's GPT models to generate engaging, humorous, and informative posts tailored for various social media platforms.

***

## Project Layers & Workflow

### 1. Input Understanding  
Users provide a YouTube video transcript. The prompt instructs the AI:  
```
Here is a new video transcript: video_transcript
Generate a social media post based on my provided video transcript.
```

### 2. Task Planner  
The model used is **GPT-4o-mini**, guided with instructions:  
```
You are a talented content writer who writes engaging, humorous, and highly readable social media posts.  
You will receive a video transcript and social media platforms.  
Generate social media posts based on the transcript and platform.  
You may also search the web for updated information and add useful details.
```

This functionality is implemented as the first tool in the agent.

### 3. Output Generator  
Before generating output, the agent ensures:  
- The YouTube video ID is correctly fetched.  
- The AI model is accessible.  
- The API key is present and valid.

***

## Learning Insights

### About Python Virtual Environments  
- A virtual environment isolates project dependencies and Python versions to avoid conflicts.  
- Useful when working on multiple projects requiring different packages or versions.  
- Prevents affecting the system's global Python installation.  

**Creating a virtual environment:**  
- Windows Command Prompt:  
  ```
  python -m venv .venv
  ```
- PowerShell:  
  ```
  cd to project directory  
  py -m venv .venv
  ```

### Key Project Learnings  
- How to integrate AI in Python code effectively.  
- Importance of virtual environments for clean, efficient development.  
- Automate basic tasks to save time and improve productivity using AI.  
- Use Streamlit for building interactive web apps running in the browser.  
- Explore offline large language models (LLMs) for local AI processing without token limits.

***

## Challenges Faced

1. **Virtual environment activation syntax differed on Windows vs macOS.**  
   Realized the need to check platform-specific commands for venv activation.

2. **Fetching video ID from URLs was inefficient.**  
   Directly using the video ID improved processing speed and output generation.

3. **YouTube transcript API errors due to missing or outdated installations.**  
   Reinstalling the API package resolved recognition issues.

4. **Insufficient tokens error while running the AI model.**  
   Learned that many LLMs require billing or token purchase for usage.  
   Explored local AI models like Ollama that run offline without ongoing costs.

***

## About Streamlit

Streamlit is a powerful tool for quickly building data and AI-powered web apps with minimal coding. It provides an intuitive browser interface that enhances user experience and simplifies app deployment.

***

## Summary

This project offered hands-on experience in integrating AI with Python, managing project environments, and building user-friendly applications. The challenges strengthened problem-solving skills and introduced modern AI tools and practices that are key to efficient development workflows.

***

Feel free to explore and contribute!








