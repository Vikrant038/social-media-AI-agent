# Improvement Plan — social-media-AI-agent

This plan is ordered. Each phase is a git branch, verified before merge.

---

## 1. Bug Fixes (Phase 2 — branch `fix/post-generation-selection`)

**1.1 Generation respects only selected platforms** — `social_media_agent.py`
- Build the JSON example/instructions **dynamically** from the `platforms` list instead of the hardcoded `LinkedIn/Instagram/Twitter` example.
- Add an explicit constraint: *"Generate posts for EXACTLY these platforms and no others: {platforms_str}. Return one object per platform."*
- After parsing, **filter** the model output to only the requested platforms (defensive guard against the model adding extras), and warn if any requested platform is missing.

**1.2 Broken markdown-fence stripping** — `social_media_agent.py:113`
- Replace the buggy `replace("``````", "")` with a robust strip that removes leading ` ```json ` / ` ``` ` and trailing ` ``` ` fences (regex-based).

**1.3 Edge cases (UI)** — `app.py`
- No platform selected → already errors; keep and verify.
- No video ID → button disabled + guard; keep and verify.
- Transcript fetch failure → friendly error message instead of raw traceback (traceback hidden behind an expander).

---

## 2. UI Professionalization (Phase 3 — branch `ui/replace-emojis-with-icons`)

**2.1 Icon system:** Google **Material Symbols** via CDN, loaded once in a header `st.markdown`.
- Helper `icon(name)` returning `<span class="material-symbols-outlined">name</span>`.
- Replace **every** emoji (full list in Project Map §6) with a mapped Material Symbol:
  - 🚀 → `rocket_launch` / brand title
  - 💼 LinkedIn → `work`, 📸 Instagram → `photo_camera`, 🐦 Twitter/X → `tag`, 👥 Facebook → `groups`
  - 📝 → `edit_note`, 🎯 → `ads_click`, ✨ Generate → `auto_awesome`, 📊 → `bar_chart`
  - 📱 → `devices`, 📥 → `download`, 📋 → `content_copy`, 🔍 → `code`, ✅ → `check_circle`, ⚠️/❌ → `error`
  - sidebar 📚→`menu_book`, 💡→`lightbulb`, 🔒→`lock`, 🤖→`smart_toy`, 📹→`smart_display`
- `page_icon` (browser tab) stays a single neutral emoji (Streamlit requires emoji/URL; not part of in-app UI). Will note this exception.
- **Zero emoji characters in rendered app body.**

---

## 3. Layout Enhancements (Phase 4 — branch `ui/professional-polish`)

- **Design tokens (CSS `:root` variables):** palette below, 8-pt spacing grid, type scale.
  - Primary `#4F46E5`, Primary-dark `#4338CA`, Accent `#10B981`, Surface `#FFFFFF`, BG `#F8FAFC`, Border `#E2E8F0`, Text `#0F172A`, Muted `#64748B`.
- Replace gradient header with a clean, restrained **hero** (title + one-line description, icon).
- Group inputs into a single bordered **card** (`st.container(border=True)`); platforms as a clear selector row.
- Results rendered as consistent **cards** (use the already-defined-but-unused `.platform-card`).
- Clean sidebar: brand/title, concise steps, "Powered by" footer.
- Remove unused CSS; keep only classes actually used.

**Micro-interactions & feedback**
- Spinner during generation; `st.toast` success/error.
- Generate button shows disabled/working state; disabled when no video ID.
- Word/char count per post.

**Functional gaps (approved):**
- **Persist results in `st.session_state`** so copy/download/rerun no longer wipes generated content.
- **Real clipboard copy** via a small JS `navigator.clipboard` component (`st.components.v1.html`) replacing the fake "Copied!" button.

---

## 4. Performance (within Phase 5 — branch `polish/security-perf`)

- `@st.cache_data` on `get_transcript` (keyed by video_id) to avoid refetching.
- Avoid regenerating when inputs unchanged (guard via session_state).

---

## 5. Security & Configuration (Phase 5 — branch `polish/security-perf`)

- Support **`st.secrets`** first, fall back to env var: `GEMINI_API_KEY = st.secrets.get(...) or os.getenv(...)`.
- Add `.streamlit/secrets.toml.example` and `.env.example`; document setup.
- Add `.gitignore` (`.env`, `.streamlit/secrets.toml`, `__pycache__/`, `.venv/`, `*.pyc`).
- Remove `print()` statements that leak transcript/responses; use safe messaging.
- Missing API key → clear in-app error, not a crash.

---

## 6. Docs (Phase 5)

- Rewrite **README.md** accurately: Gemini (not OpenAI), real setup steps, env/secrets config, run command, features, troubleshooting.
- Pin dependency versions in `requirements.txt`.
- Fix `.devcontainer/devcontainer.json` (`main.py` → `app.py`).

---

## Verification strategy (every phase)
- `streamlit run app.py` starts with no errors.
- Manual matrix: 0 / 1 / multiple platforms; valid & invalid video ID; with & without custom instructions.
- Confirm only selected platforms are produced.
- Visual pass: zero emoji in app body, consistent spacing/colors.
