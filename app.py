# --------------------------------------------------------------
# app.py - AI Social Media Content Generator (Streamlit)
# --------------------------------------------------------------
import json

import streamlit as st
import streamlit.components.v1 as components
from streamlit_local_storage import LocalStorage

from social_media_agent import Runner, ItemHelpers, HAS_SERVER_KEY


# --------------------------------------------------------------
# Page Configuration
# --------------------------------------------------------------
# Note: page_icon (browser tab) must be an emoji or image URL per Streamlit;
# it is not part of the in-app UI, where all icons are Material Symbols.
st.set_page_config(
    page_title="AI Social Media Content Generator",
    page_icon="https://img.icons8.com/material-rounded/96/share.png",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------------------
# Icon helper (Google Material Symbols)
# --------------------------------------------------------------
def icon(name: str) -> str:
    """Return an inline Material Symbols icon span."""
    return f'<span class="material-symbols-outlined">{name}</span>'


PLATFORM_ICONS = {
    "LinkedIn": "work",
    "Instagram": "photo_camera",
    "Twitter": "tag",
    "Facebook": "groups",
}


# --------------------------------------------------------------
# Design system: fonts, icon library and custom CSS
# --------------------------------------------------------------
# IMPORTANT: this block must be left-aligned (column 0) with NO blank lines.
# Markdown treats 4-space-indented lines as code, and a blank line ends an
# HTML block, either of which makes Streamlit print the CSS as literal text.
st.markdown(
"""<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0&display=swap" />
<style>
:root {
--primary: #4F46E5;
--primary-dark: #4338CA;
--accent: #10B981;
--danger: #EF4444;
--bg: #F8FAFC;
--surface: #FFFFFF;
--surface-secondary: #F1F5F9;
--border: #CBD5E1;
--text: #0F172A;
--text-secondary: #334155;
--muted: #64748B;
--pill-bg: #F1F5F9;
--pill-text: #334155;
--pill-success-bg: #ECFDF5;
--pill-success-border: #A7F3D0;
--pill-success-text: #065F46;
--pill-error-bg: #FEF2F2;
--pill-error-border: #FECACA;
--pill-error-text: #991B1B;
--alert-error-bg: #FEF2F2;
--alert-error-border: #FECACA;
--alert-error-text: #991B1B;
--alert-success-bg: #ECFDF5;
--alert-success-border: #A7F3D0;
--alert-success-text: #065F46;
--radius: 12px;
--shadow: 0 1px 3px rgba(15, 23, 42, 0.08), 0 1px 2px rgba(15, 23, 42, 0.04);
}
@media (prefers-color-scheme: dark) {
:root {
--primary: #818CF8;
--primary-dark: #6366F1;
--accent: #34D399;
--danger: #F87171;
--bg: #0B0F19;
--surface: #1E293B;
--surface-secondary: #0F172A;
--border: #334155;
--text: #F8FAFC;
--text-secondary: #E2E8F0;
--muted: #94A3B8;
--pill-bg: #0F172A;
--pill-text: #E2E8F0;
--pill-success-bg: rgba(16, 185, 129, 0.18);
--pill-success-border: rgba(16, 185, 129, 0.4);
--pill-success-text: #6EE7B7;
--pill-error-bg: rgba(239, 68, 68, 0.18);
--pill-error-border: rgba(239, 68, 68, 0.4);
--pill-error-text: #FCA5A5;
--alert-error-bg: rgba(239, 68, 68, 0.18);
--alert-error-border: rgba(239, 68, 68, 0.4);
--alert-error-text: #FCA5A5;
--alert-success-bg: rgba(16, 185, 129, 0.18);
--alert-success-border: rgba(16, 185, 129, 0.4);
--alert-success-text: #6EE7B7;
--shadow: 0 1px 3px rgba(0, 0, 0, 0.4), 0 1px 2px rgba(0, 0, 0, 0.3);
}
}
[data-theme="dark"], .stApp[data-theme="dark"], [data-testid="stAppViewContainer"][data-theme="dark"] {
--primary: #818CF8;
--primary-dark: #6366F1;
--accent: #34D399;
--danger: #F87171;
--bg: #0B0F19;
--surface: #1E293B;
--surface-secondary: #0F172A;
--border: #334155;
--text: #F8FAFC;
--text-secondary: #E2E8F0;
--muted: #94A3B8;
--pill-bg: #0F172A;
--pill-text: #E2E8F0;
--pill-success-bg: rgba(16, 185, 129, 0.18);
--pill-success-border: rgba(16, 185, 129, 0.4);
--pill-success-text: #6EE7B7;
--pill-error-bg: rgba(239, 68, 68, 0.18);
--pill-error-border: rgba(239, 68, 68, 0.4);
--pill-error-text: #FCA5A5;
--alert-error-bg: rgba(239, 68, 68, 0.18);
--alert-error-border: rgba(239, 68, 68, 0.4);
--alert-error-text: #FCA5A5;
--alert-success-bg: rgba(16, 185, 129, 0.18);
--alert-success-border: rgba(16, 185, 129, 0.4);
--alert-success-text: #6EE7B7;
--shadow: 0 1px 3px rgba(0, 0, 0, 0.4), 0 1px 2px rgba(0, 0, 0, 0.3);
}
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: var(--bg); color: var(--text); }
.material-symbols-outlined { vertical-align: middle; font-size: 1.2rem; line-height: 1; position: relative; top: -1px; margin-right: 0.4rem; color: var(--primary); }
.hero { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 2rem 2.5rem; margin-bottom: 1.75rem; box-shadow: var(--shadow); display: flex; align-items: center; gap: 1.25rem; }
.hero-badge { flex: 0 0 auto; width: 56px; height: 56px; border-radius: 14px; background: linear-gradient(135deg, var(--primary), var(--primary-dark)); display: flex; align-items: center; justify-content: center; }
.hero-badge .material-symbols-outlined { color: #fff !important; font-size: 1.9rem; margin: 0; top: 0; }
.hero h1 { font-size: 1.7rem; font-weight: 700; color: var(--text) !important; margin: 0; }
.hero p { color: var(--muted) !important; margin: 0.25rem 0 0; font-size: 0.97rem; }
.section-title { font-size: 1.05rem; font-weight: 600; color: var(--text) !important; margin: 0.5rem 0 0.75rem; display: flex; align-items: center; }
div[data-testid="stVerticalBlockBorderWrapper"] { background: var(--surface); border-radius: var(--radius) !important; box-shadow: var(--shadow); border: 1px solid var(--border) !important; }
div[data-testid="stMarkdownContainer"] p, div[data-testid="stMarkdownContainer"] span, div[data-testid="stMarkdownContainer"] li { color: var(--text); }
label[data-testid="stWidgetLabel"] p, label[data-testid="stWidgetLabel"] span { color: var(--text) !important; font-weight: 500; }
[data-testid="stCaptionContainer"] p, [data-testid="stCaptionContainer"] span { color: var(--muted) !important; }
[data-testid="stMetricLabel"] p, [data-testid="stMetricLabel"] span { color: var(--muted) !important; }
[data-testid="stMetricValue"] div { color: var(--text) !important; }
.stButton > button { background: linear-gradient(135deg, var(--primary), var(--primary-dark)); color: #fff !important; border: none; padding: 0.65rem 1.5rem; font-size: 1rem; font-weight: 600; border-radius: 10px; width: 100%; transition: all 0.2s ease; }
.stButton > button:hover:enabled { transform: translateY(-1px); box-shadow: 0 6px 16px rgba(79, 70, 229, 0.35); }
.stButton > button:disabled { opacity: 0.5; }
.stDownloadButton > button { background: var(--surface); color: var(--text) !important; border: 1px solid var(--border); padding: 0.55rem 1rem; border-radius: 9px; font-weight: 600; width: 100%; }
.stDownloadButton > button:hover { border-color: var(--primary); color: var(--primary) !important; }
.stTextArea textarea, .stTextInput input { background: var(--surface) !important; color: var(--text) !important; border-radius: 10px; border: 1.5px solid var(--border) !important; }
.stTextArea textarea:focus, .stTextInput input:focus { border-color: var(--primary) !important; box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15); }
.pill { display: inline-flex; align-items: center; background: var(--pill-bg); border: 1px solid var(--border); color: var(--pill-text) !important; border-radius: 999px; padding: 0.3rem 0.7rem; font-size: 0.8rem; font-weight: 600; white-space: nowrap; }
.pill .material-symbols-outlined { font-size: 1rem; color: var(--muted); }
.pill.pill-success { background: var(--pill-success-bg) !important; border-color: var(--pill-success-border) !important; color: var(--pill-success-text) !important; }
.pill.pill-success .material-symbols-outlined { color: var(--pill-success-text) !important; }
.pill.pill-error { background: var(--pill-error-bg) !important; border-color: var(--pill-error-border) !important; color: var(--pill-error-text) !important; }
.pill.pill-error .material-symbols-outlined { color: var(--pill-error-text) !important; }
.alert { border-radius: 10px; padding: 0.85rem 1rem; font-weight: 500; margin-bottom: 1rem; display: flex; align-items: center; }
.alert-error { background: var(--alert-error-bg); border: 1px solid var(--alert-error-border); color: var(--alert-error-text); }
.alert-error .material-symbols-outlined { color: var(--danger); }
.alert-success { background: var(--alert-success-bg); border: 1px solid var(--alert-success-border); color: var(--alert-success-text); }
.alert-success .material-symbols-outlined { color: var(--accent); }
section[data-testid="stSidebar"] { background: var(--surface); border-right: 1px solid var(--border); }
.footer { text-align: center; padding: 1.5rem; color: var(--muted); border-top: 1px solid var(--border); margin-top: 2.5rem; font-size: 0.85rem; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
</style>""",
    unsafe_allow_html=True,
)


# --------------------------------------------------------------
# Session state
# --------------------------------------------------------------
if "result" not in st.session_state:
    st.session_state.result = None          # AgentResult of last successful run
if "result_video_id" not in st.session_state:
    st.session_state.result_video_id = None
if "error" not in st.session_state:
    st.session_state.error = None


def alert(kind: str, icon_name: str, message: str):
    st.markdown(
        f'<div class="alert alert-{kind}">{icon(icon_name)}{message}</div>',
        unsafe_allow_html=True,
    )


def copy_button(text: str, key: str):
    """A real clipboard-copy button using navigator.clipboard with adaptive light/dark theme."""
    safe = json.dumps(text)  # safely escape for embedding in JS
    components.html(
        f"""
        <style>
        :root {{
            --btn-bg: #FFFFFF;
            --btn-border: #CBD5E1;
            --btn-text: #0F172A;
            --btn-hover-border: #4F46E5;
            --btn-hover-text: #4F46E5;
        }}
        @media (prefers-color-scheme: dark) {{
            :root {{
                --btn-bg: #1E293B;
                --btn-border: #334155;
                --btn-text: #F8FAFC;
                --btn-hover-border: #818CF8;
                --btn-hover-text: #818CF8;
            }}
        }}
        body {{ margin: 0; background: transparent; font-family: 'Inter', -apple-system, sans-serif; }}
        .copy-btn {{
            width: 100%;
            padding: 0.55rem 1rem;
            border-radius: 9px;
            cursor: pointer;
            border: 1px solid var(--btn-border);
            background: var(--btn-bg);
            color: var(--btn-text);
            font-weight: 600;
            font-size: 0.9rem;
            transition: all 0.2s ease;
            box-sizing: border-box;
        }}
        .copy-btn:hover {{
            border-color: var(--btn-hover-border);
            color: var(--btn-hover-text);
        }}
        </style>
        <button id="btn_{key}" class="copy-btn">
            Copy
        </button>
        <script>
        const b = document.getElementById("btn_{key}");
        b.addEventListener("click", async () => {{
            try {{
                await navigator.clipboard.writeText({safe});
                b.textContent = "Copied!";
                setTimeout(() => b.textContent = "Copy", 1500);
            }} catch (e) {{ b.textContent = "Press Ctrl+C"; }}
        }});
        </script>
        """,
        height=48,
    )


# --------------------------------------------------------------
# Hero
# --------------------------------------------------------------
st.markdown(
f"""<div class="hero">
<div class="hero-badge">{icon('rocket_launch')}</div>
<div>
<h1>AI Social Media Content Generator</h1>
<p>Transform YouTube videos into engaging, platform-tailored social posts in seconds.</p>
</div>
</div>""",
    unsafe_allow_html=True,
)


# --------------------------------------------------------------
# Sidebar
# --------------------------------------------------------------
with st.sidebar:
    st.markdown(f"## {icon('share')}Content Generator", unsafe_allow_html=True)

    # ----- Bring your own Gemini key (BYOK), persisted in browser localStorage -----
    st.markdown(f"#### {icon('key')}Gemini API key", unsafe_allow_html=True)

    local_storage = LocalStorage()
    # getItem returns None on the first render (the component loads async), then
    # the real value on the follow-up rerun. Seed session_state once it arrives so
    # the field repopulates after a refresh. value= can't be used here because
    # Streamlit ignores it once the widget already has state.
    stored_key = local_storage.getItem("gemini_api_key")
    if stored_key and not st.session_state.get("_byok_seeded"):
        st.session_state["api_key_field"] = stored_key
        st.session_state["_byok_seeded"] = True

    typed_key = st.text_input(
        "Your Gemini API key",
        key="api_key_field",
        type="password",
        placeholder="AIza...",
        help="Stored only in your own browser (localStorage) and sent directly "
             "to Google. Get one at aistudio.google.com/app/apikey",
        label_visibility="collapsed",
    ).strip()

    # Persist a newly entered key so it survives page refreshes.
    if typed_key and typed_key != (stored_key or ""):
        local_storage.setItem("gemini_api_key", typed_key, key="ls_set_key")

    user_api_key = typed_key

    def _clear_api_key():
        local_storage.deleteItem("gemini_api_key")
        st.session_state["api_key_field"] = ""
        st.session_state["_byok_seeded"] = True

    if user_api_key:
        st.markdown(
            f'<span class="pill pill-success">{icon("check_circle")}Key saved in this browser</span>',
            unsafe_allow_html=True,
        )
        st.button(
            "Clear saved key",
            use_container_width=True,
            key="clear_key",
            on_click=_clear_api_key,
        )
    elif HAS_SERVER_KEY:
        st.caption("Optional — leave blank to use the app's shared key.")
    else:
        st.markdown(
            f'<span class="pill pill-error">{icon("error")}Key required to generate</span>',
            unsafe_allow_html=True,
        )
    st.markdown(
        "[Get a free key &#8599;](https://aistudio.google.com/app/apikey)",
    )
    st.markdown("---")

    st.markdown(f"#### {icon('menu_book')}How to use", unsafe_allow_html=True)
    st.markdown(
        """
1. **Get the video ID** — the part after `v=` in a YouTube URL
   (e.g. `youtube.com/watch?v=`**`OZ5OZZZ2cvk`**).
2. **Select platforms** — each gets optimized content.
3. **Generate** — review, copy or download the posts.
        """
    )
    st.markdown("---")
    st.markdown(f"#### {icon('lightbulb')}Tips", unsafe_allow_html=True)
    st.markdown(
        "- Add custom instructions for tone & focus\n"
        "- Try different platform combinations\n"
        "- Edit the generated text before posting"
    )
    st.markdown("---")
    st.markdown(
        f'<span class="pill">{icon("lock")}Data is processed securely and not stored</span>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"{icon('smart_toy')}Powered by **Google Gemini**", unsafe_allow_html=True)
    st.markdown(f"{icon('smart_display')}**YouTube Transcript API**", unsafe_allow_html=True)


# --------------------------------------------------------------
# Input card
# --------------------------------------------------------------
with st.container(border=True):
    st.markdown(
        f'<div class="section-title">{icon("edit_note")}Input settings</div>',
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns([1, 1])
    with c1:
        video_id = st.text_input(
            "YouTube Video ID",
            placeholder="e.g., OZ5OZZZ2cvk",
            help="The part after 'v=' in the YouTube URL.",
            key="video_id_input",
        ).strip()
    with c2:
        query = st.text_area(
            "Custom instructions (optional)",
            placeholder="e.g., Focus on key takeaways, professional tone, include hashtags...",
            height=92,
            help="Customize tone, focus or formatting of the generated content.",
        )

    st.markdown(
        f'<div class="section-title">{icon("ads_click")}Target platforms</div>',
        unsafe_allow_html=True,
    )
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        st.markdown(icon("work"), unsafe_allow_html=True)
        linkedin = st.checkbox("LinkedIn", value=True, help="Professional networking")
    with p2:
        st.markdown(icon("photo_camera"), unsafe_allow_html=True)
        instagram = st.checkbox("Instagram", value=True, help="Visual storytelling")
    with p3:
        st.markdown(icon("tag"), unsafe_allow_html=True)
        twitter = st.checkbox("Twitter/X", help="Concise micro-blogging")
    with p4:
        st.markdown(icon("groups"), unsafe_allow_html=True)
        facebook = st.checkbox("Facebook", help="Conversational social networking")

    selected_platforms = [
        name for name, chosen in (
            ("LinkedIn", linkedin), ("Instagram", instagram),
            ("Twitter", twitter), ("Facebook", facebook),
        ) if chosen
    ]

    has_key = HAS_SERVER_KEY or bool(user_api_key)

    st.markdown("<br>", unsafe_allow_html=True)
    bcol1, bcol2, bcol3 = st.columns([1, 2, 1])
    with bcol2:
        generate_clicked = st.button(
            "Generate content",
            disabled=not (video_id and selected_platforms and has_key),
            use_container_width=True,
            key="generate_button",
        )

    if not has_key:
        st.caption("Add your Gemini API key in the sidebar to enable generation.")
    elif not video_id:
        st.caption("Enter a video ID to enable generation.")
    elif not selected_platforms:
        st.caption("Select at least one platform to enable generation.")


# --------------------------------------------------------------
# Generation (runs once, result persisted in session_state)
# --------------------------------------------------------------
if generate_clicked:
    st.session_state.error = None
    st.session_state.result = None
    with st.spinner("Crafting your content... this may take a minute."):
        try:
            st.session_state.result = Runner.run(
                video_id=video_id,
                platforms=selected_platforms,
                custom_query=query if query.strip() else None,
                api_key=user_api_key or None,
            )
            st.session_state.result_video_id = video_id
            st.toast("Content generated successfully", icon="✅")
        except Exception as e:  # noqa: BLE001 - surfaced to user below
            st.session_state.error = str(e)
            st.toast("Generation failed", icon="⚠️")


# --------------------------------------------------------------
# Results (rendered from session_state so reruns don't wipe them)
# --------------------------------------------------------------
if st.session_state.error:
    alert("error", "error", f"Something went wrong: {st.session_state.error}")
    with st.expander("View technical details"):
        st.code(st.session_state.error)

result = st.session_state.result
if result:
    rvid = st.session_state.result_video_id
    alert("success", "check_circle", "Content generated successfully.")

    st.markdown(
        f'<div class="section-title">{icon("bar_chart")}Summary</div>',
        unsafe_allow_html=True,
    )
    summary_cols = st.columns(len(result.posts))
    for idx, post in enumerate(result.posts):
        with summary_cols[idx]:
            st.metric(label=post.platform, value="Ready")

    st.markdown(
        f'<div class="section-title">{icon("devices")}Generated content</div>',
        unsafe_allow_html=True,
    )
    for post in result.posts:
        ic = PLATFORM_ICONS.get(post.platform, "devices")
        with st.container(border=True):
            wc = len(post.content.split())
            head, pill = st.columns([4, 1])
            with head:
                st.markdown(
                    f'<div class="section-title">{icon(ic)}{post.platform}</div>',
                    unsafe_allow_html=True,
                )
            with pill:
                st.markdown(
                    f'<span class="pill">{icon("description")}{wc} words</span>',
                    unsafe_allow_html=True,
                )
            st.text_area(
                "Content",
                post.content,
                height=220,
                key=f"content_{post.platform}",
                label_visibility="collapsed",
            )
            a1, a2 = st.columns([1, 1])
            with a1:
                st.download_button(
                    label="Download",
                    data=post.content,
                    file_name=f"{post.platform.lower()}_post_{rvid}.txt",
                    mime="text/plain",
                    key=f"download_{post.platform}",
                    use_container_width=True,
                )
            with a2:
                copy_button(post.content, key=post.platform)

    with st.expander("View raw JSON output (for developers)"):
        json_output = ItemHelpers.format_posts_as_json(result.posts)
        st.code(json_output, language="json")
        st.download_button(
            label="Download JSON",
            data=json_output,
            file_name=f"social_content_{rvid}.json",
            mime="application/json",
        )


# --------------------------------------------------------------
# Footer
# --------------------------------------------------------------
st.markdown(
"""<div class="footer">Built with Streamlit · Powered by Google Gemini &amp; the YouTube Transcript API<br><span style="opacity:0.8">Your data is processed securely and not stored.</span></div>""",
    unsafe_allow_html=True,
)
