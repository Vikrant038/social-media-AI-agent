# AI Social Media Content Generator

Turn any YouTube video into engaging, platform-tailored social media posts. Paste a
video ID, pick your platforms, and a Google **Gemini** model writes optimized posts
for **LinkedIn, Instagram, Twitter/X, and Facebook** from the video's transcript.

Built with **Streamlit**.

> 📐 Curious how this was built — the bugs I hunted, the trade-offs, and the
> system design? See **[docs/DESIGN.md](docs/DESIGN.md)**.

---

## The problem I'm solving

Creators and small teams publish one piece of long-form content — usually a
YouTube video — and then have to manually rewrite it over and over for every
social platform. That's slow, repetitive, and each platform has its own rules
(LinkedIn wants a professional hook, Twitter has 280 characters, Instagram lives
on emoji and hashtags). Most "AI post generators" either ignore those rules or
spit out the same generic blob everywhere.

**The goal:** paste a video, pick the platforms you actually care about, and get
back posts that are *ready to publish* and *shaped for each network* — nothing
more, nothing less.

## How I thought about it

I treated this less like "write a script that calls an AI" and more like
"design a small product." The reasoning, step by step, so anyone can reuse it:

1. **Start from the user's job, not the API.** The user wants publish-ready posts
   for *specific* platforms. So "respect the selection exactly" and "match each
   platform's conventions" became the two non-negotiable requirements — everything
   else serves those.

2. **Separate the UI from the brain.** The Streamlit page ([app.py](app.py)) only
   collects input and shows results. All the real work — fetching the transcript,
   choosing a model, prompting Gemini, validating the output — lives in
   [social_media_agent.py](social_media_agent.py). This keeps each side simple and
   testable, and means you could swap the UI (or the AI provider) without rewriting
   the other half.

3. **Don't trust the model blindly — constrain *and* verify.** I tell Gemini
   "generate exactly these platforms and no others," *and* I filter its response
   down to the selected platforms afterwards. Asking nicely isn't enough; the code
   enforces the contract. (This is what fixed the original bug where unselected
   platforms still got posts.)

4. **Make failure boring.** A missing API key, a retired model, a video with no
   captions, or malformed JSON should each produce a clear message — never a crash
   or a blank screen. Picking the model at runtime from `list_models()` instead of
   hardcoding one is part of this: the app adapts instead of breaking.

5. **Respect the user's time and money.** Transcripts are cached so re-runs are
   instant. And because API calls cost money, anyone can bring their own key
   (BYOK), stored in their own browser so they never have to re-enter it.

6. **Verify by watching it work.** I didn't trust "it returned HTTP 200." I drove
   a real browser to screenshot the UI and even simulated typing a key + reloading
   to prove the key persists. If I claim something works, I watched it work.

You can apply this same checklist to almost any small AI tool: *anchor on the
user's job → split UI from logic → constrain and validate the model → fail
gracefully → cache and respect cost → verify by observation.*

---

## Features

- **Transcript-powered** — fetches the YouTube transcript automatically (no manual copy/paste).
- **Generates only what you select** — posts are produced strictly for the platforms you check.
- **Custom instructions** — steer tone, focus, and formatting.
- **Professional UI** — Material Symbols icons, a clean design system, loading and error states.
- **One-click copy & download** — real clipboard copy plus `.txt` / `.json` downloads.
- **Results persist** — copying or downloading no longer wipes the generated content.
- **Cached transcripts** — repeated runs on the same video skip the refetch.
- **Platform-tuned output** — each post follows that network's conventions
  (Twitter's 280-char cap, LinkedIn hook + CTA + hashtags, Instagram emoji +
  hashtag block, Facebook conversational tone), generated via Gemini's reliable
  JSON mode.
- **Bring your own key (BYOK)** — users can paste their own Gemini key in the sidebar;
  it's used only for their session and never stored, so a public deployment doesn't
  have to pay for everyone's generations.

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

You have three options:

- **In the app (BYOK)** — just run the app and paste a Gemini key into the sidebar.
  Nothing to configure ahead of time. The key lives only in that browser session.
- **Streamlit secrets** or **environment file** — set a shared server key so users
  don't need to bring their own (below).

For a shared server key, choose **one** of the following:

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
├── docs/
│   └── DESIGN.md                # Engineering journey: problems, decisions, design
└── README.md
```

---

## Troubleshooting

| Problem | Fix |
| --- | --- |
| *"Gemini API key not configured"* | Add your key to `.streamlit/secrets.toml` or `.env`. |
| *"YouTube is blocking transcript requests"* | YouTube rate-limited your IP (common on cloud/shared IPs or after many requests). Wait a few minutes, or configure a proxy — see **[Working around YouTube IP bans](#working-around-youtube-ip-bans)**. |
| Transcript error / empty result | The video may have transcripts disabled or no captions in the requested language. Try another video. |
| Wrong/extra platforms generated | Already fixed — only selected platforms are returned. Re-pull the latest code. |
| Copy button does nothing | Clipboard access requires a secure context (localhost is fine); otherwise use `Ctrl+C`. |

---

## Working around YouTube IP bans

YouTube blocks transcript requests from IPs that make too many requests or that
belong to cloud providers (AWS, GCP, Azure, etc.). If you see *"YouTube is
blocking transcript requests"*:

- **Quick fix:** wait a few minutes and retry from a normal home/office network.
- **Robust fix:** route transcript fetches through a proxy. Set **one** of these
  in `.streamlit/secrets.toml` or `.env`:

  ```toml
  # Recommended — Webshare residential proxies (https://www.webshare.io/)
  WEBSHARE_PROXY_USERNAME = "..."
  WEBSHARE_PROXY_PASSWORD = "..."

  # …or any generic HTTP/HTTPS proxy
  HTTP_PROXY_URL  = "http://user:pass@host:port"
  HTTPS_PROXY_URL = "http://user:pass@host:port"
  ```

  When set, the app fetches transcripts through the proxy automatically; when
  unset, it connects directly. No code changes needed.

---

## Notes

- The transcript is truncated to ~4000 characters before generation to stay efficient.
- The Gemini model is selected automatically from those your key can access
  (preferring `gemini-2.5-flash` / `gemini-2.0-flash`), so a retired model id
  never breaks the app. Adjust `PREFERRED_MODELS` in `social_media_agent.py`.
- A user-supplied key (BYOK) is saved in your browser's `localStorage` so it
  persists across refreshes; clear it anytime with the sidebar button.
