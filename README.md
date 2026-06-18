# AI Social Media Content Generator

Turn any YouTube video into engaging, platform-tailored social media posts. Paste a
video ID, pick your platforms, and a Google **Gemini** model writes optimized posts
for **LinkedIn, Instagram, Twitter/X, and Facebook** from the video's transcript.

Built with **Streamlit**.

---

## Features

- **Transcript-powered** — fetches the YouTube transcript automatically (no manual copy/paste).
- **Generates only what you select** — posts are produced strictly for the platforms you check.
- **Custom instructions** — steer tone, focus, and formatting.
- **Professional UI** — Material Symbols icons, a clean design system, loading and error states.
- **One-click copy & download** — real clipboard copy plus `.txt` / `.json` downloads.
- **Results persist** — copying or downloading no longer wipes the generated content.
- **Cached transcripts** — repeated runs on the same video skip the refetch.

---

## How it works

```
app.py (Streamlit UI)
  └─ Runner.run(video_id, platforms, custom_query)        social_media_agent.py
       ├─ get_transcript(video_id)        → youtube-transcript-api  (cached)
       ├─ truncate transcript to ~4000 chars
       └─ generate_social_content(...)    → google-generativeai (Gemini)
            └─ parse JSON, keep only selected platforms → posts
```

The prompt instructs Gemini to return a JSON array containing **exactly** the selected
platforms, and the response is filtered to those platforms as a defensive guard.

---

## Prerequisites

- Python 3.9+
- A **Gemini API key** — create one at <https://aistudio.google.com/app/apikey>

---

## Setup

```bash
# 1. Clone and enter the project
git clone <your-repo-url>
cd social-media-AI-agent

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Configure your API key

Choose **one** of the following:

**Option A — Streamlit secrets (recommended)**
```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# then edit .streamlit/secrets.toml and paste your key
```

**Option B — environment file**
```bash
cp .env.example .env
# then edit .env and paste your key
```

Both `.env` and `.streamlit/secrets.toml` are git-ignored and never committed.

---

## Run

```bash
streamlit run app.py
```

Then open <http://localhost:8501>.

### Usage

1. Copy the **video ID** — the part after `v=` in a YouTube URL
   (`youtube.com/watch?v=`**`OZ5OZZZ2cvk`**).
2. (Optional) Add **custom instructions**.
3. Select one or more **platforms**.
4. Click **Generate content**, then copy or download the posts.

---

## Project structure

```
social-media-AI-agent/
├── app.py                       # Streamlit UI
├── social_media_agent.py        # Transcript fetch + Gemini generation logic
├── requirements.txt             # Pinned dependencies
├── .env.example                 # Env-var config template
├── .streamlit/
│   └── secrets.toml.example     # Streamlit secrets template
├── PLAN.md                      # Improvement plan / project map
└── README.md
```

---

## Troubleshooting

| Problem | Fix |
| --- | --- |
| *"Gemini API key not configured"* | Add your key to `.streamlit/secrets.toml` or `.env`. |
| Transcript error / empty result | The video may have transcripts disabled or no English captions. Try another video. |
| Wrong/extra platforms generated | Already fixed — only selected platforms are returned. Re-pull the latest code. |
| Copy button does nothing | Clipboard access requires a secure context (localhost is fine); otherwise use `Ctrl+C`. |

---

## Notes

- The transcript is truncated to ~4000 characters before generation to stay efficient.
- `gemini-2.0-flash-exp` is used by default; change the model id in
  `social_media_agent.py` if needed.
- Your data is processed in-session and not stored.
