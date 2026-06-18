# --------------------------------------------------------------
# app.py - AI Social Media Content Generator (Streamlit)
# --------------------------------------------------------------
import streamlit as st
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
    initial_sidebar_state="expanded"
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
# Fonts, icon library and custom CSS
# --------------------------------------------------------------
st.markdown("""
    <link rel="stylesheet"
        href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" />
    <style>
    .material-symbols-outlined {
        vertical-align: middle;
        font-size: 1.25rem;
        line-height: 1;
        position: relative;
        top: -1px;
        margin-right: 0.4rem;
    }

    .main { padding: 2rem; }

    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .main-header h1 { font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem; color: white !important; }
    .main-header p { font-size: 1.1rem; opacity: 0.9; margin: 0; }
    .main-header .material-symbols-outlined { font-size: 2.5rem; }

    .input-section {
        background: #f8f9fa; padding: 2rem; border-radius: 15px;
        margin-bottom: 2rem; border: 1px solid #e9ecef;
    }

    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; border: none; padding: 0.75rem 2rem;
        font-size: 1.1rem; font-weight: 600; border-radius: 10px;
        width: 100%; transition: all 0.3s;
    }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4); }

    .stDownloadButton > button {
        background: #28a745; color: white; border: none;
        padding: 0.5rem 1rem; border-radius: 8px; font-weight: 500;
    }
    .stDownloadButton > button:hover { background: #218838; }

    .stTextArea textarea { border-radius: 10px; border: 2px solid #e9ecef; padding: 1rem; }
    .stTextArea textarea:focus { border-color: #667eea; box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25); }

    .success-banner {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white; padding: 1rem; border-radius: 10px;
        text-align: center; margin-bottom: 1rem; font-weight: 600;
    }

    .footer {
        text-align: center; padding: 2rem; color: #6c757d;
        border-top: 1px solid #e9ecef; margin-top: 3rem;
    }

    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)


# --------------------------------------------------------------
# Header Section
# --------------------------------------------------------------
st.markdown(f"""
    <div class="main-header">
        <h1>{icon('rocket_launch')}AI Social Media Content Generator</h1>
        <p>Transform YouTube videos into engaging social media posts in seconds</p>
    </div>
""", unsafe_allow_html=True)


# --------------------------------------------------------------
# Sidebar with Instructions
# --------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/video.png", width=80)
    st.markdown(f"## {icon('menu_book')}How to Use", unsafe_allow_html=True)
    st.markdown("""
    ### Step 1: Get Video ID
    - Open any YouTube video
    - Copy the ID from the URL
    - Example: `youtube.com/watch?v=**OZ5OZZZ2cvk**`

    ### Step 2: Select Platforms
    - Choose one or more platforms
    - Each platform gets optimized content

    ### Step 3: Generate
    - Click the generate button
    - Wait for AI to create content
    - Download and use!
    """)
    st.markdown("---")
    st.markdown(f"### {icon('lightbulb')}Tips", unsafe_allow_html=True)
    st.markdown("""
    - Add custom instructions for better results
    - Try different platform combinations
    - Edit generated content as needed
    """)
    st.markdown("---")
    st.markdown(f"### {icon('lock')}Privacy", unsafe_allow_html=True)
    st.markdown("Your data is processed securely and not stored.")
    st.markdown("---")
    st.markdown("**Powered by:**")
    st.markdown(f"{icon('smart_toy')}Google Gemini AI", unsafe_allow_html=True)
    st.markdown(f"{icon('smart_display')}YouTube Transcript API", unsafe_allow_html=True)


# --------------------------------------------------------------
# Main Content Area
# --------------------------------------------------------------
st.markdown(f"### {icon('edit_note')}Input Settings", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    video_id = st.text_input(
        "YouTube Video ID",
        placeholder="e.g., OZ5OZZZ2cvk",
        help="Enter the YouTube video ID (the part after 'v=' in the URL)",
        key="video_id_input"
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    query = st.text_area(
        "Custom Instructions (Optional)",
        placeholder="e.g., Focus on key takeaways, use a professional tone, include relevant hashtags...",
        height=100,
        help="Add specific instructions to customize the generated content"
    )
    st.markdown('</div>', unsafe_allow_html=True)


# Platform Selection
st.markdown(f"### {icon('ads_click')}Select Target Platforms", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(icon("work"), unsafe_allow_html=True)
    linkedin = st.checkbox("LinkedIn", value=True, help="Professional networking platform")
with col2:
    st.markdown(icon("photo_camera"), unsafe_allow_html=True)
    instagram = st.checkbox("Instagram", value=True, help="Visual storytelling platform")
with col3:
    st.markdown(icon("tag"), unsafe_allow_html=True)
    twitter = st.checkbox("Twitter/X", help="Micro-blogging platform")
with col4:
    st.markdown(icon("groups"), unsafe_allow_html=True)
    facebook = st.checkbox("Facebook", help="Social networking platform")


st.markdown("<br>", unsafe_allow_html=True)


# Generate Button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    generate_clicked = st.button(
        "Generate Content",
        disabled=not video_id,
        use_container_width=True,
        key="generate_button"
    )


# --------------------------------------------------------------
# Content Generation Logic
# --------------------------------------------------------------
if generate_clicked:
    if not video_id:
        st.markdown(f'<div class="success-banner" style="background:#dc3545">{icon("error")}Please enter a YouTube Video ID</div>', unsafe_allow_html=True)
    else:
        selected_platforms = []
        if linkedin:
            selected_platforms.append("LinkedIn")
        if instagram:
            selected_platforms.append("Instagram")
        if twitter:
            selected_platforms.append("Twitter")
        if facebook:
            selected_platforms.append("Facebook")

        if not selected_platforms:
            st.markdown(f'<div class="success-banner" style="background:#dc3545">{icon("error")}Please select at least one social media platform</div>', unsafe_allow_html=True)
        else:
            with st.spinner("Crafting your content... This may take a minute."):
                try:
                    result = Runner.run(
                        video_id=video_id,
                        platforms=selected_platforms,
                        custom_query=query if query.strip() else None
                    )

                    st.markdown(f"""
                        <div class="success-banner">
                            {icon('check_circle')}Content Generated Successfully!
                        </div>
                    """, unsafe_allow_html=True)

                    st.markdown(f"### {icon('bar_chart')}Generation Summary", unsafe_allow_html=True)
                    stat_cols = st.columns(len(result.posts))
                    for idx, post in enumerate(result.posts):
                        with stat_cols[idx]:
                            st.metric(label=post.platform, value="Ready", delta="Generated")

                    st.markdown("<br>", unsafe_allow_html=True)

                    st.markdown(f"### {icon('devices')}Generated Content", unsafe_allow_html=True)

                    for post in result.posts:
                        ic = PLATFORM_ICONS.get(post.platform, "devices")
                        with st.expander(f"{post.platform} Post", expanded=True):
                            st.markdown(f"{icon(ic)}**Platform:** {post.platform}", unsafe_allow_html=True)
                            st.text_area(
                                "Content Preview",
                                post.content,
                                height=250,
                                key=f"content_{post.platform}",
                                help=f"Your generated {post.platform} post"
                            )

                            c1, c2 = st.columns([3, 1])
                            with c1:
                                st.download_button(
                                    label="Download Content",
                                    data=post.content,
                                    file_name=f"{post.platform.lower()}_post_{video_id}.txt",
                                    mime="text/plain",
                                    key=f"download_{post.platform}",
                                    use_container_width=True
                                )
                            with c2:
                                word_count = len(post.content.split())
                                st.markdown(f"{icon('description')}{word_count} words", unsafe_allow_html=True)

                    with st.expander("View Raw JSON Output (for developers)"):
                        json_output = ItemHelpers.format_posts_as_json(result.posts)
                        st.code(json_output, language="json")
                        st.download_button(
                            label="Download JSON",
                            data=json_output,
                            file_name=f"social_content_{video_id}.json",
                            mime="application/json"
                        )

                except Exception as e:
                    st.markdown(f'<div class="success-banner" style="background:#dc3545">{icon("error")}An error occurred: {str(e)}</div>', unsafe_allow_html=True)
                    with st.expander("View Error Details"):
                        st.exception(e)


# --------------------------------------------------------------
# Footer
# --------------------------------------------------------------
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(f"""
    <div class="footer">
        <p style="font-size: 0.9rem;">
            Made with Streamlit | Powered by Google Gemini AI &amp; YouTube Transcript API
        </p>
        <p style="font-size: 0.8rem; margin-top: 0.5rem;">
            {icon('lock')}Your data is processed securely and not stored
        </p>
    </div>
""", unsafe_allow_html=True)
