# AI Social Media Content Generator

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)]()
[![Framework](https://img.shields.io/badge/framework-Streamlit-FF4B4B.svg)]()
[![Model](https://img.shields.io/badge/model-Gemini%203.6%20Flash-4F46E5.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

Transform any YouTube video into engaging, platform-tailored social media posts. Paste a video ID, select your target platforms, and Google **Gemini (prioritizing `gemini-3.6-flash`)** generates optimized, ready-to-publish posts for **LinkedIn, Instagram, Twitter/X, and Facebook** directly from the video's transcript.

Built with **Streamlit** and engineered from **First Principles of Reasoning**.

> 📐 Deep dive into the architectural decisions, bug investigations, contrast physics, and system design in **[docs/DESIGN.md](docs/DESIGN.md)**.

---

## The Problem

Creators, marketing teams, and developers invest hours producing long-form video content, but redistributing that content across social networks requires manually reformatting it for distinct algorithms, audiences, and constraints:
- **LinkedIn**: Professional hooks, structured whitespace, insights, and strategic hashtags (~150–250 words).
- **Instagram**: Punchy visual caption, line breaks, emojis, strong CTA, and a niche hashtag block.
- **Twitter/X**: High-density single post under a strict **280-character cap** (including hashtags).
- **Facebook**: Conversational, community-focused hook designed to spark discussion.

Most "AI post generators" output generic summaries that ignore platform constraints, hallucinate unselected channels, or fail on dark/light UI themes.

---

## First Principles of Reasoning: How We Built This

Rather than building by analogy ("stitch a prompt to an API wrapper"), we decomposed the problem into fundamental truths and built upward from first principles:

```
                      FIRST PRINCIPLES FRAMEWORK
                      
  ┌─────────────────────────────────────────────────────────────────┐
  │ 1. THE USER JOB                                                 │
  │    • Truth: Users need publish-ready platform assets, not blobs.│
  │    • Solution: Per-platform constraint specs & exact selection. │
  ├─────────────────────────────────────────────────────────────────┤
  │ 2. PROBABILISTIC LLM vs DETERMINISTIC CONTRACTS                 │
  │    • Truth: LLMs imitate prompt examples & code fences break.   │
  │    • Solution: Dynamic prompt schemas + JSON mode + post-filter.│
  ├─────────────────────────────────────────────────────────────────┤
  │ 3. MODEL LIFECYCLE & CAPABILITY DISCOVERY                       │
  │    • Truth: Hardcoded model IDs rot over time.                  │
  │    • Solution: Runtime list_models() prioritized to 3.6 Flash.  │
  ├─────────────────────────────────────────────────────────────────┤
  │ 4. STREAMLIT EXECUTION & STATE PERSISTENCE                      │
  │    • Truth: Top-to-bottom script reruns wipe ephemeral state.   │
  │    • Solution: Runner decoupling + session_state + BYOK storage.│
  ├─────────────────────────────────────────────────────────────────┤
  │ 5. COLOR CONTRAST & DUAL-THEME ACCESSIBILITY                    │
  │    • Truth: Visual perception requires WCAG AA contrast (4.5:1).│
  │    • Solution: Adaptive CSS tokens for Light & Dark backgrounds.│
  └─────────────────────────────────────────────────────────────────┘
```

### 1. The User Job (Product First Principle)
- **Fundamental Truth**: The user's goal is to publish immediately on *selected* platforms with zero manual re-editing.
- **Deduction**: The system must enforce strict platform isolation. Requesting only "Twitter" must never return LinkedIn or Facebook posts, and each post must obey hard platform constraints (e.g., the Twitter 280-character ceiling).

### 2. Probabilistic LLMs vs Deterministic Contracts (Engineering First Principle)
- **Fundamental Truth**: Large Language Models are probabilistic token predictors. Static prompt examples bias outputs toward example keys regardless of instructions, and code fences (````json ... ````) can break standard deserialization.
- **Deduction (Defense-in-Depth)**:
  - **Dynamic Schema Construction**: Prompt examples are built dynamically from user-selected platforms at runtime.
  - **Native JSON Mode**: `response_mime_type="application/json"` guarantees structurally valid JSON.
  - **Post-Generation Filtering**: The backend filters the model's parsed JSON case-insensitively, strictly matching only requested platforms.

### 3. Model Discovery & Fault-Tolerant Fallback (Architecture First Principle)
- **Fundamental Truth**: Model versions change and experimental IDs deprecate (e.g., `gemini-2.5-flash` was non-existent/retired).
- **Deduction**: The backend queries `genai.list_models()` at runtime, verifies `generateContent` support, and selects the highest-tier available model from a preference hierarchy (`gemini-3.6-flash` → `gemini-2.0-flash` → `gemini-flash-latest` → `gemini-1.5-flash`).

### 4. Ephemeral State vs Client-Side Persistence (State First Principle)
- **Fundamental Truth**: Streamlit reruns scripts from top-to-bottom on every user click, wiping unpersisted state. Additionally, public deployments should not subsidize third-party API usage.
- **Deduction**:
  - Results are held in `st.session_state` so downloading or copying does not reset the UI.
  - Bring-Your-Own-Key (BYOK) persists the API key safely in the user's browser `localStorage` using an asynchronous handshake state machine.
  - Transcripts are cached with `st.cache_data` to eliminate redundant network roundtrips.

### 5. Color Theory & Dual-Theme Accessibility (UI/UX First Principle)
- **Fundamental Truth**: Text legibility requires adequate luminance contrast ($L_1/L_2 \ge 4.5:1$ per WCAG AA). Hardcoding light surfaces or dark text colors causes text invisibility when Streamlit or the operating system switches to Dark Mode.
- **Deduction**:
  - We implemented an adaptive CSS variable token system responding to `@media (prefers-color-scheme: dark)` and Streamlit's `[data-theme="dark"]`.
  - **Light Mode**: Deep charcoal slate text (`#0F172A`, `#334155`) on crisp light surfaces (`#F8FAFC`, `#FFFFFF`).
  - **Dark Mode**: High-luminance slate text (`#F8FAFC`, `#E2E8F0`) on deep dark slate surfaces (`#0B0F19`, `#1E293B`).
  - Iframe components (like the custom Copy button) embed independent adaptive color schemes.

---

## Features

- **Transcript-Powered**: Fetches YouTube captions automatically using `youtube-transcript-api`.
- **Gemini 3.6 Flash Optimized**: High-speed, high-fidelity reasoning prioritizing `gemini-3.6-flash` with dynamic fallback.
- **Strict Platform Isolation**: Generates posts exclusively for checked platforms.
- **Platform-Tuned Formats**: Tailored prompts for LinkedIn, Instagram, Twitter/X (<280 chars), and Facebook.
- **Adaptive Light/Dark Theme**: Contrast-safe typography and cards visible in both light and dark environments.
- **Zero-Data-Leak BYOK**: Bring your own Gemini API key; stored strictly in your browser's `localStorage`.
- **One-Click Real Copy**: JavaScript clipboard integration (`navigator.clipboard.writeText`) that survives reruns.
- **Export Options**: Download individual platform `.txt` files or full `.json` payloads.
- **IP Ban & Proxy Resilience**: Built-in support for Webshare residential proxies and generic HTTP/HTTPS proxies.

---

## System Architecture

```
app.py (Streamlit UI)
  │
  ├── Adaptive CSS Tokens (Light/Dark High-Contrast Theme)
  ├── LocalStorage Bridge (BYOK Gemini API Key Persistence)
  └── Runner.run(video_id, platforms, custom_query, api_key)
        │
        ▼
social_media_agent.py (Backend Agent Logic)
  ├── get_transcript(video_id)
  │     └─ Cached via st.cache_data / Optional Proxy Routing
  ├── select_model_name()
  │     └─ list_models() → Prefers gemini-3.6-flash → gemini-2.0-flash → Fallback
  └── generate_social_content(...)
        ├─ Dynamic Prompt Synthesis (PLATFORM_SPECS)
        ├─ Gemini JSON Mode Generation
        └─ Defensive Post-Filtering (Strict Platform Guard)
```

---

## Prerequisites

- **Python 3.9+**
- A **Gemini API key** — obtain one free at [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

---

## Setup & Installation

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd social-media-AI-agent

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. Install pinned dependencies
pip install -r requirements.txt
```

### Configure Your API Key

Choose **one** of the following methods:

1. **In-App (BYOK - Recommended for End Users)**: Run the app and enter your key in the sidebar. It is stored securely in your browser's `localStorage` and sent directly to Google.
2. **Streamlit Secrets (Recommended for Hosted Deployments)**:
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   # Edit .streamlit/secrets.toml with GEMINI_API_KEY = "AIza..."
   ```
3. **Environment File**:
   ```bash
   cp .env.example .env
   # Edit .env with GEMINI_API_KEY=AIza...
   ```

---

## Run the Application

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

### How to Use

1. Enter a **YouTube Video ID** (e.g. `OZ5OZZZ2cvk` from `youtube.com/watch?v=OZ5OZZZ2cvk`).
2. (Optional) Provide **custom instructions** (e.g., "Focus on actionable takeaways for tech founders").
3. Select your **target platforms** (LinkedIn, Instagram, Twitter/X, Facebook).
4. Click **Generate content** to preview, copy, or download.

---

## Project Structure

```
social-media-AI-agent/
├── app.py                       # Streamlit UI with adaptive light/dark theming
├── social_media_agent.py        # Core logic: transcript fetching, Gemini 3.6 Flash runner
├── requirements.txt             # Pinned project dependencies
├── .env.example                 # Environment variable template
├── .streamlit/
│   └── secrets.toml.example     # Streamlit secrets template
├── docs/
│   └── DESIGN.md                # First principles engineering journey & design doc
└── README.md                    # Project overview & documentation
```

---

## Working Around YouTube IP Bans

Cloud host IPs (AWS, GCP, Azure, Streamlit Cloud) or heavy request volumes can occasionally trigger YouTube rate limits (`RequestBlocked` or `IpBlocked`).

To route transcript requests through a proxy, set **one** of the following in `.streamlit/secrets.toml` or `.env`:

```toml
# Option A: Webshare Residential Proxies (https://www.webshare.io/)
WEBSHARE_PROXY_USERNAME = "your_username"
WEBSHARE_PROXY_PASSWORD = "your_password"

# Option B: Generic HTTP/HTTPS Proxy
HTTP_PROXY_URL  = "http://user:pass@proxy-host:port"
HTTPS_PROXY_URL = "http://user:pass@proxy-host:port"
```

When configured, proxy routing activates automatically.

---

## Troubleshooting

| Problem | Cause | Resolution |
|---|---|---|
| *"Gemini API key not configured"* | No key detected in sidebar, secrets, or env. | Enter your key in the sidebar BYOK field or set `GEMINI_API_KEY`. |
| *"YouTube is temporarily blocking transcript requests"* | YouTube IP rate limit on shared network/cloud host. | Wait a few minutes or configure a residential proxy (see above). |
| *"This video has no available transcript/captions"* | Captions are disabled on the video. | Test with a video that has closed captions enabled. |
| Text hard to read in Dark Mode | Theme contrast mismatch. | Resolved — app uses adaptive high-contrast CSS tokens for light and dark modes. |
| Copy button inactive | Insecure browser context (non-HTTPS/non-localhost). | Use HTTPS, `localhost`, or manual selection (`Ctrl+C` / `Cmd+C`). |

---

## License

MIT License. Feel free to use, modify, and distribute.
