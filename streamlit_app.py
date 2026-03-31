import streamlit as st
import yt_dlp
import os
import tempfile
import time
from pathlib import Path

# ---------- Page configuration ----------
st.set_page_config(
    page_title="YouTube Downloader",
    page_icon="🎬",
    layout="centered"
)

# ---------- Custom CSS for better appearance ----------
st.markdown("""
<style>
    /* Main container */
    .main {
        padding: 2rem;
    }
    /* Title */
    .title {
        text-align: center;
        color: #FF4B4B;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    /* Subtitle */
    .subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    /* Download button */
    .stButton button {
        background-color: #FF4B4B;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        width: 100%;
        transition: 0.3s;
    }
    .stButton button:hover {
        background-color: #ff1e1e;
        transform: scale(1.02);
    }
    /* Custom info box */
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin-top: 1rem;
        text-align: center;
    }
    footer {
        text-align: center;
        margin-top: 3rem;
        color: #aaa;
    }
</style>
""", unsafe_allow_html=True)

# ---------- Helper functions ----------
def get_video_info(url):
    """Fetch video title and available formats."""
    ydl_opts = {'quiet': True, 'no_warnings': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        title = info.get('title', 'video')
        formats = info.get('formats', [])
        return title, formats

def download_video(url, format_spec, progress_placeholder):
    """Download video with given format spec and update progress."""
    # Create a temporary directory to store the file
    with tempfile.TemporaryDirectory() as tmpdir:
        output_template = os.path.join(tmpdir, '%(title)s.%(ext)s')
        ydl_opts = {
            'format': format_spec,
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [lambda d: update_progress(d, progress_placeholder)],
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                # If the downloaded file is a webm/mkv and we want mp4, yt-dlp may have merged it
                # We just return the actual file path
                return filename
        except Exception as e:
            st.error(f"Download failed: {e}")
            return None

def update_progress(d, placeholder):
    """Callback to update download progress."""
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '0%').strip()
        speed = d.get('_speed_str', 'N/A').strip()
        eta = d.get('_eta_str', 'N/A').strip()
        placeholder.markdown(f"**Downloading...** {percent} at {speed} – ETA: {eta}")
    elif d['status'] == 'finished':
        placeholder.markdown("✅ **Download finished! Processing...**")

# ---------- App layout ----------
st.markdown('<div class="title">🎬 YouTube Downloader</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Download any YouTube video in high quality</div>', unsafe_allow_html=True)

# URL input
url = st.text_input("🔗 **Video URL**", placeholder="https://www.youtube.com/watch?v=...")

if url:
    with st.spinner("Fetching video information..."):
        try:
            title, formats = get_video_info(url)
            st.success(f"✅ Found: **{title}**")
        except Exception as e:
            st.error(f"Could not fetch video info. Please check the URL.\n\nError: {e}")
            st.stop()

    # Choose download type
    download_type = st.radio(
        "📥 **Select download type**",
        ["Best quality (video + audio)", "Audio only (MP3)", "Choose specific quality"]
    )

    format_spec = None
    if download_type == "Best quality (video + audio)":
        format_spec = "bestvideo+bestaudio/best"
        st.info("🎧 Requires ffmpeg to merge video and audio streams.")
    elif download_type == "Audio only (MP3)":
        format_spec = "bestaudio/best"
        st.info("🎵 Will download as MP3 (requires ffmpeg).")
    else:  # Choose specific quality
        # Build a list of readable format descriptions
        format_options = {}
        for f in formats:
            # Skip non-video formats if we want video+audio
            if f.get('vcodec') != 'none' or f.get('acodec') != 'none':
                resolution = f.get('resolution', 'audio only')
                if resolution == 'audio only':
                    desc = f"Audio only ({f.get('abr', '?')} kbps)"
                else:
                    desc = f"{resolution} ({f.get('fps', '?')} fps) – {f.get('ext', '?')}"
                # Use format id as value
                format_options[desc] = f['format_id']
        if format_options:
            selected_desc = st.selectbox("Choose a format", list(format_options.keys()))
            format_spec = format_options[selected_desc]
        else:
            st.error("No suitable formats found.")
            st.stop()

    # Download button
    if st.button("🚀 Download Now", use_container_width=True):
        # Create a placeholder for progress
        progress_placeholder = st.empty()

        with st.status("Downloading...", expanded=True) as status:
            file_path = download_video(url, format_spec, progress_placeholder)
            if file_path and os.path.exists(file_path):
                status.update(label="Download complete!", state="complete", expanded=False)
                # Provide download button
                with open(file_path, "rb") as f:
                    file_bytes = f.read()
                file_name = os.path.basename(file_path)
                st.download_button(
                    label="💾 Click here to save the file",
                    data=file_bytes,
                    file_name=file_name,
                    mime="video/mp4" if file_name.endswith(('.mp4', '.mkv')) else "audio/mpeg",
                    use_container_width=True
                )
            else:
                status.update(label="Download failed", state="error")

# Footer
st.markdown('<footer>⚠️ Respect YouTube’s terms of service. Download only content you have permission to.</footer>', unsafe_allow_html=True)
