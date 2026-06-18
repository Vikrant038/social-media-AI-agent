# --------------------------------------------------------------
# app.py - AI Social Media Content Generator (Streamlit)
# --------------------------------------------------------------
import json

import streamlit as st
import streamlit.components.v1 as components

from social_media_agent import Runner, ItemHelpers


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
st.markdown(
    """
    <link rel="stylesheet"
        href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0&display=swap" />
    <style>
    :root {
        --primary: #4F46E5;
        --primary-dark: #4338CA;
        --accent: #10B981;
        --danger: #EF4444;
        --bg: #F8FAFC;
        --surface: #FFFFFF;
        --border: #E2E8F0;
        --text: #0F172A;
        --muted: #64748B;
        --radius: 12px;
        --shadow: 0 1px 3px rgba(15, 23, 42, 0.08), 0 1px 2px rgba(15, 23, 42, 0.04);
        --shadow-lg: 0 10px 25px rgba(15, 23, 42, 0.08);
    }

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: var(--bg); }

    .material-symbols-outlined {
        vertical-align: middle;
        font-size: 1.2rem;
        line-height: 1;
        position: relative;
        top: -1px;
        margin-right: 0.4rem;
        color: var(--primary);
    }

    /* Hero */
    .hero {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 2rem 2.5rem;
        margin-bottom: 1.75rem;
        box-shadow: var(--shadow);
        display: flex;
        align-items: center;
        gap: 1.25rem;
    }
    .hero-badge {
        flex: 0 0 auto;
        width: 56px; height: 56px;
        border-radius: 14px;
        background: linear-gradient(135deg, var(--primary), var(--primary-dark));
        display: flex; align-items: center; justify-content: center;
    }
    .hero-badge .material-symbols-outlined { color: #fff; font-size: 1.9rem; margin: 0; top: 0; }
    .hero h1 { font-size: 1.7rem; font-weight: 700; color: var(--text); margin: 0; }
    .hero p { color: var(--muted); margin: 0.25rem 0 0; font-size: 0.97rem; }

    /* Section titles */
    .section-title {
        font-size: 1.05rem; font-weight: 600; color: var(--text);
        margin: 0.5rem 0 0.75rem; display: flex; align-items: center;
    }

    /* Cards via Streamlit bordered containers */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: var(--surface);
        border-radius: var(--radius) !important;
        box-shadow: var(--shadow);
    }

    /* Primary button */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary), var(--primary-dark));
        color: #fff; border: none; padding: 0.65rem 1.5rem;
        font-size: 1rem; font-weight: 600; border-radius: 10px;
        width: 100%; transition: all 0.2s ease;
    }
    .stButton > button:hover:enabled {
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(79, 70, 229, 0.35);
    }
    .stButton > button:disabled { opacity: 0.5; }

    .stDownloadButton > button {
        background: var(--surface); color: var(--text);
        border: 1px solid var(--border); padding: 0.55rem 1rem;
        border-radius: 9px; font-weight: 600; width: 100%;
    }
    .stDownloadButton > button:hover { border-color: var(--primary); color: var(--primary); }

    /* Inputs */
    .stTextArea textarea, .stTextInput input {
        border-radius: 10px; border: 1.5px solid var(--border);
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15);
    }

    /* Pill for word count */
    .pill {
        display: inline-flex; align-items: center;
        background: var(--bg); border: 1px solid var(--border);
        color: var(--muted); border-radius: 999px;
        padding: 0.3rem 0.7rem; font-size: 0.8rem; font-weight: 600;
        white-space: nowrap;
    }
    .pill .material-symbols-outlined { font-size: 1rem; color: var(--muted); }

    /* Alerts */
    .alert { border-radius: 10px; padding: 0.85rem 1rem; font-weight: 500; margin-bottom: 1rem; display: flex; align-items: center; }
    .alert-error { background: #FEF2F2; border: 1px solid #FECACA; color: #991B1B; }
    .alert-error .material-symbols-outlined { color: var(--danger); }
    .alert-success { background: #ECFDF5; border: 1px solid #A7F3D0; color: #065F46; }
    .alert-success .material-symbols-outlined { color: var(--accent); }

    /* Sidebar */
    section[data-testid="stSidebar"] { background: var(--surface); border-right: 1px solid var(--border); }

    /* Footer */
    .footer { text-align: center; padding: 1.5rem; color: var(--muted);
        border-top: 1px solid var(--border); margin-top: 2.5rem; font-size: 0.85rem; }

    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header[data-testid="stHeader"] { background: transparent; }
    </style>
    """,
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
    """A real clipboard-copy button using navigator.clipboard."""
    safe = json.dumps(text)  # safely escape for embedding in JS
    components.html(
        f"""
        <button id="btn_{key}" style="
            width:100%;padding:0.55rem 1rem;border-radius:9px;cursor:pointer;
            border:1px solid #E2E8F0;background:#fff;color:#0F172A;
            font-weight:600;font-family:Inter,sans-serif;font-size:0.9rem;">
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
    f"""
    <div class="hero">
        <div class="hero-badge">{icon('rocket_launch')}</div>
        <div>
            <h1>AI Social Media Content Generator</h1>
            <p>Transform YouTube videos into engaging, platform-tailored social posts in seconds.</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------------------
# Sidebar
# --------------------------------------------------------------
with st.sidebar:
    st.markdown(f"## {icon('share')}Content Generator", unsafe_allow_html=True)
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

    st.markdown("<br>", unsafe_allow_html=True)
    bcol1, bcol2, bcol3 = st.columns([1, 2, 1])
    with bcol2:
        generate_clicked = st.button(
            "Generate content",
            disabled=not (video_id and selected_platforms),
            use_container_width=True,
            key="generate_button",
        )

    if not video_id:
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
    f"""
    <div class="footer">
        Built with Streamlit · Powered by Google Gemini &amp; the YouTube Transcript API<br>
        <span style="opacity:0.8">Your data is processed securely and not stored.</span>
    </div>
    """,
    unsafe_allow_html=True,
)
