# Design & Engineering Journey

This document is the "why" behind the code — the problems we hit, what the app
looked like before, the decisions we made, and the system design. It exists so
that anyone reading the repo can see this was *engineered*, not just typed out.

---

## 1. Where we started (the "before")

The original app was a single 447-line `app.py` plus a backend module. It worked
on a happy path but had real defects:

- **Wrong content was generated.** Selecting only "Facebook" could still return
  LinkedIn/Instagram/Twitter posts.
- **A fake "Copy" button** that showed "Copied!" but copied nothing.
- **Results vanished on interaction.** Any button click triggered a Streamlit
  rerun that wiped the generated posts, because nothing was stored in
  `st.session_state`.
- **Emoji used as UI icons** everywhere (📧 🎨 🚀 …) — fine for a hobby app,
  not for a professional tool.
- **A retired model id** (`gemini-2.0-flash-exp`) that later started 404-ing.
- **Brittle JSON parsing** with a broken code-fence stripper
  (`replace("``````", "")` — six backticks, which never matched).
- **An inaccurate README** describing OpenAI/GPT-4o-mini when the code used
  Google Gemini.

## 2. How we worked (process)

We ran the project in explicit phases, each on its own git branch, each verified
before merge:

| Phase | Branch | Outcome |
|---|---|---|
| Bug fix | `fix/post-generation-selection` | Only-selected-platforms + robust parsing |
| Icons | `ui/replace-emojis-with-icons` | Material Symbols, zero emoji in UI body |
| UI overhaul | `ui/professional-polish` | Design system, persistence, real copy |
| Hardening | `polish/security-perf` | Secrets, caching, pinned deps, docs |
| Follow-ups | `main` | BYOK, model auto-select, CSS render fix, quality |

The discipline that mattered most: **verify by observation, not assumption.**
Early on we "verified" with `curl` returning `HTTP 200` — which only proves the
server responded, not that the page is correct. That bit us (see §3.2). After
that we drove a real headless Chrome session over the DevTools Protocol to take
screenshots and even simulate typing + reload.

## 3. The hard problems (and how we solved them)

### 3.1 The real selection bug was in the prompt, not the checkboxes
The UI collected the selected platforms correctly. The bug was that the prompt's
JSON *example* hardcoded `LinkedIn / Instagram / Twitter`, so the model imitated
the example regardless of selection.

**Fix:** build the example and a per-platform instruction list *dynamically* from
the user's selection, add an explicit "EXACTLY these and no others" constraint,
and then **filter the model's output** to the requested platforms
(case-insensitively, order-preserving) as a defensive guard. Defense in depth:
constrain the model *and* validate its output.

### 3.2 CSS rendered as literal text on screen
After the UI overhaul, the page showed raw CSS as text. Root cause: Streamlit
renders `st.markdown` through a Markdown parser. A line indented 4+ spaces is a
*code block*, and a blank line *ends* an HTML block — so our nicely-indented,
blank-line-separated `<style>` block was printed instead of injected.

**Fix:** left-align every raw-HTML block to column 0 and remove internal blank
lines. **Lesson:** Markdown-in-Streamlit is whitespace-sensitive; treat injected
HTML/CSS as one contiguous, unindented block.

### 3.3 The model id rotted
`gemini-2.0-flash-exp` was an experimental alias Google later removed → 404.

**Fix:** don't hardcode. Query `list_models()`, keep models that support
`generateContent`, and pick the best available from a preference list
(`gemini-2.5-flash` → `2.0-flash` → …) with a safe fallback. The app now adapts
to whatever the key can access.

### 3.4 "Bring your own key" that survives a refresh
For a publicly shared app we didn't want to pay for everyone's usage, so users
supply their own Gemini key (BYOK). But a Streamlit `session_state` value is lost
on a full page refresh, forcing re-entry every time.

**Fix:** persist the key in the browser's `localStorage` via
`streamlit-local-storage`. The subtlety: the component returns `None` on first
render (it loads asynchronously) and the real value on a follow-up rerun. A
`text_input(value=...)` default is ignored once the widget has state, so we
**seed `st.session_state` once the stored value arrives**, guarded by a flag, and
provide a "Clear saved key" button. Verified end-to-end: type a key → reload →
key is still there.

### 3.5 Output quality vs. reliability
The generated posts read well, but parsing relied on stripping Markdown fences,
and there was no length/format discipline per platform.

**Fix:** switch to Gemini's **native JSON mode**
(`response_mime_type="application/json"`) so the response is guaranteed valid
JSON, and add **per-platform specs** (`PLATFORM_SPECS`) encoding each network's
conventions — Twitter's 280-char cap, LinkedIn hook+CTA+hashtags, Instagram
emoji + hashtag block, Facebook conversational tone.

## 4. System design

```
┌──────────────────────── app.py (Streamlit UI) ────────────────────────┐
│  • Design-system CSS (single injected block)                           │
│  • Sidebar: BYOK key  ──persist──▶  browser localStorage               │
│  • Inputs: video id, custom instructions, platform checkboxes          │
│  • Results rendered from st.session_state (survive reruns)             │
│  • Real clipboard copy via navigator.clipboard component               │
└───────────────┬───────────────────────────────────────────────────────┘
                │ Runner.run(video_id, platforms, custom_query, api_key)
                ▼
┌──────────────────────── social_media_agent.py ────────────────────────┐
│  get_transcript ── youtube-transcript-api (cached via st.cache_data)   │
│  select_model_name() ── list_models() → best available                 │
│  generate_social_content():                                            │
│     • per-platform guidance + strict platform constraint               │
│     • Gemini JSON mode → parse → FILTER to selected platforms          │
│  → AgentResult(posts=[Post(platform, content)])                        │
└────────────────────────────────────────────────────────────────────────┘
```

**Key design principles**
- **Separation of concerns:** UI (`app.py`) never talks to Gemini directly; all
  generation goes through `Runner`/`social_media_agent`.
- **Defense in depth:** constrain the model, then validate its output.
- **Fail safe, not loud:** missing key, retired model, transcript errors, and
  malformed JSON each degrade gracefully with a user-facing message.
- **Config over hardcoding:** key from `st.secrets`/env/BYOK; model chosen at
  runtime; platform rules in one editable dict.
- **Privacy by default:** transcripts aren't stored; the BYOK key lives only in
  the user's own browser and is sent directly to Google.

## 5. Verification methodology

- **Unit-level:** mocked the Gemini client to prove platform filtering, JSON-mode
  invocation, and fence-stripping without spending API calls.
- **Boot-level:** launched Streamlit headless and confirmed a clean start with
  and without a key, and in a fresh virtualenv.
- **Visual/behavioral:** drove headless Chrome over the DevTools Protocol to
  screenshot the rendered UI and to simulate typing a key + reloading to confirm
  persistence. This is what turned "I think it works" into "I watched it work."

## 6. Known limitations / next steps

- `google-generativeai` is deprecated in favor of `google-genai`; a future change
  should migrate the SDK.
- No rate-limiting on transcript fetches for public deployments.
- A hybrid "free shared quota, then BYOK for unlimited" model would be a natural
  next step.
- Could add `response_schema` (typed) to JSON mode for even stricter outputs.
