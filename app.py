# --------------------------------------------------------------
# streamlit_app.py - Enhanced Version
# --------------------------------------------------------------
import streamlit as st
from social_media_agent import get_transcript, Runner, ItemHelpers


# --------------------------------------------------------------
# Page Configuration
# --------------------------------------------------------------
st.set_page_config(
    page_title="AI Social Media Content Generator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --------------------------------------------------------------
# Custom CSS Styling
# --------------------------------------------------------------
st.markdown("""
    <style>
    /* Main app styling */
    .main {
        padding: 2rem;
    }
    
    /* Custom header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        color: white !important;
    }
    
    .main-header p {
        font-size: 1.1rem;
        opacity: 0.9;
        margin: 0;
    }
    
    /* Input section styling */
    .input-section {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        border: 1px solid #e9ecef;
    }
    
    /* Platform cards */
    .platform-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s;
    }
    
    .platform-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        border-radius: 10px;
        width: 100%;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Download button styling */
    .stDownloadButton > button {
        background: #28a745;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 500;
    }
    
    .stDownloadButton > button:hover {
        background: #218838;
    }
    
    /* Text area styling */
    .stTextArea textarea {
        border-radius: 10px;
        border: 2px solid #e9ecef;
        padding: 1rem;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
    }
    
    /* Checkbox styling */
    .stCheckbox {
        padding: 0.5rem;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #f8f9fa;
        border-radius: 10px;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    /* Success message */
    .success-banner {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    /* Info boxes */
    .info-box {
        background: #e7f3ff;
        border-left: 4px solid #2196F3;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    
    /* Stats container */
    .stats-container {
        display: flex;
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .stat-box {
        flex: 1;
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
    
    .stat-label {
        color: #6c757d;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #6c757d;
        border-top: 1px solid #e9ecef;
        margin-top: 3rem;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Platform icons */
    .platform-icon {
        font-size: 1.5rem;
        margin-right: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)


# --------------------------------------------------------------
# Header Section
# --------------------------------------------------------------
st.markdown("""
    <div class="main-header">
        <h1>🚀 AI Social Media Content Generator</h1>
        <p>Transform YouTube videos into engaging social media posts in seconds</p>
    </div>
""", unsafe_allow_html=True)


# --------------------------------------------------------------
# Sidebar with Instructions
# --------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/video.png", width=80)
    st.title("📚 How to Use")
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
    
    ---
    
    ### 💡 Tips
    - Add custom instructions for better results
    - Try different platform combinations
    - Edit generated content as needed
    
    ---
    
    ### 🔒 Privacy
    Your data is processed securely and not stored.
    """)
    
    st.markdown("---")
    st.markdown("**Powered by:**")
    st.markdown("🤖 Google Gemini AI")
    st.markdown("📹 YouTube Transcript API")


# --------------------------------------------------------------
# Main Content Area
# --------------------------------------------------------------

# Input Section
st.markdown("### 📝 Input Settings")

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


# Platform Selection with Icons
st.markdown("### 🎯 Select Target Platforms")

col1, col2, col3, col4 = st.columns(4)

with col1:
    linkedin = st.checkbox("💼 LinkedIn", value=True, help="Professional networking platform")
with col2:
    instagram = st.checkbox("📸 Instagram", value=True, help="Visual storytelling platform")
with col3:
    twitter = st.checkbox("🐦 Twitter/X", help="Micro-blogging platform")
with col4:
    facebook = st.checkbox("👥 Facebook", help="Social networking platform")


# Add spacing
st.markdown("<br>", unsafe_allow_html=True)


# Generate Button (centered and styled)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    generate_clicked = st.button(
        "✨ Generate Content",
        disabled=not video_id,
        use_container_width=True,
        key="generate_button"
    )


# --------------------------------------------------------------
# Content Generation Logic
# --------------------------------------------------------------
if generate_clicked:
    if not video_id:
        st.error("⚠️ Please enter a YouTube Video ID")
    else:
        # Collect selected platforms
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
            st.error("⚠️ Please select at least one social media platform")
        else:
            # Progress indicator
            with st.spinner("🎨 Crafting your content... This may take a minute."):
                try:
                    # Run the content generator
                    result = Runner.run(
                        video_id=video_id,
                        platforms=selected_platforms,
                        custom_query=query if query.strip() else None
                    )
                    
                    # Success message
                    st.markdown("""
                        <div class="success-banner">
                            ✅ Content Generated Successfully!
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Stats
                    st.markdown("### 📊 Generation Summary")
                    stat_cols = st.columns(len(selected_platforms))
                    for idx, platform in enumerate(selected_platforms):
                        with stat_cols[idx]:
                            st.metric(
                                label=f"{platform}",
                                value="✓ Ready",
                                delta="Generated"
                            )
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Display results
                    st.markdown("### 📱 Generated Content")
                    
                    # Platform emoji mapping
                    platform_emojis = {
                        "LinkedIn": "💼",
                        "Instagram": "📸",
                        "Twitter": "🐦",
                        "Facebook": "👥"
                    }
                    
                    # Display each post in an attractive card
                    for post in result.posts:
                        emoji = platform_emojis.get(post.platform, "📱")
                        
                        with st.expander(f"{emoji} {post.platform} Post", expanded=True):
                            # Platform header
                            st.markdown(f"**Platform:** {post.platform}")
                            
                            # Content area
                            st.text_area(
                                "Content Preview",
                                post.content,
                                height=250,
                                key=f"content_{post.platform}",
                                help=f"Your generated {post.platform} post"
                            )
                            
                            # Action buttons
                            col1, col2, col3 = st.columns([2, 1, 1])
                            
                            with col1:
                                st.download_button(
                                    label=f"📥 Download {post.platform} Content",
                                    data=post.content,
                                    file_name=f"{post.platform.lower()}_post_{video_id}.txt",
                                    mime="text/plain",
                                    key=f"download_{post.platform}",
                                    use_container_width=True
                                )
                            
                            with col2:
                                if st.button(f"📋 Copy", key=f"copy_{post.platform}", use_container_width=True):
                                    st.success("Copied!")
                            
                            with col3:
                                word_count = len(post.content.split())
                                st.info(f"📝 {word_count} words")
                    
                    # Raw JSON output (collapsible)
                    with st.expander("🔍 View Raw JSON Output (for developers)"):
                        json_output = ItemHelpers.format_posts_as_json(result.posts)
                        st.code(json_output, language="json")
                        st.download_button(
                            label="📥 Download JSON",
                            data=json_output,
                            file_name=f"social_content_{video_id}.json",
                            mime="application/json"
                        )
                
                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")
                    with st.expander("🔍 View Error Details"):
                        st.exception(e)


# --------------------------------------------------------------
# Footer
# --------------------------------------------------------------
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
    <div class="footer">
        <p style="font-size: 0.9rem;">
            Made with ❤️ using Streamlit | Powered by Google Gemini AI & YouTube Transcript API
        </p>
        <p style="font-size: 0.8rem; margin-top: 0.5rem;">
            🔒 Your data is processed securely and not stored | 🌟 Free to use
        </p>
    </div>
""", unsafe_allow_html=True)
