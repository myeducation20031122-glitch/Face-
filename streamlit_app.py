import streamlit as st
import yt_dlp
import os
import tempfile
import subprocess

# ---------- Check ffmpeg ----------
def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

ffmpeg_available = check_ffmpeg()

# ---------- Page config ----------
st.set_page_config(page_title="YouTube Downloader", page_icon="🎬", layout="centered")
st.markdown("""
<style>
    .title { text-align: center; color: #FF4B4B; font-size: 3rem; font-weight: bold; margin-bottom: 1rem; }
    .subtitle { text-align: center; color: #666; margin-bottom: 2rem; }
    .stButton button { background-color: #FF4B4B; color: white; font-weight: bold; border-radius: 8px; width: 100%; }
    .info-box { background-color: #f0f2f6; padding: 1rem; border-radius: 10px; margin-top: 1rem; text-align: center; }
    footer { text-align: center; margin-top: 3rem; color: #aaa; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🎬 YouTube Downloader</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Download any YouTube video in high quality</div>', unsafe_allow_html=True)

if not ffmpeg_available:
    st.warning("⚠️ **ffmpeg not found!** For 'Best quality' downloads, please install ffmpeg. Audio-only and specific formats may still work.")

url = st.text_input("🔗 **Video URL**", placeholder="https://www.youtube.com/watch?v=...")

if url:
    with st.spinner("Fetching video info..."):
        try:
            ydl_opts = {'quiet': True, 'no_warnings': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'video')
                formats = info.get('formats', [])
            st.success(f"✅ Found: **{title}**")
        except Exception as e:
            st.error(f"Could not fetch video info: {e}")
            st.stop()

    download_type = st.radio(
        "📥 **Select download type**",
        ["Best quality (video + audio)", "Audio only (MP3)", "Choose specific quality"]
    )

    format_spec = None
    if download_type == "Best quality (video + audio)":
        if ffmpeg_available:
            format_spec = "bestvideo+bestaudio/best"
            st.info("🎧 Will merge video and audio using ffmpeg.")
        else:
            st.error("❌ Cannot use 'Best quality' without ffmpeg. Please install ffmpeg or choose another option.")
            format_spec = None
    elif download_type == "Audio only (MP3)":
        format_spec = "bestaudio/best"
        st.info("🎵 Will download as audio (requires ffmpeg for conversion).")
    else:  # Choose specific quality
        format_options = {}
        for f in formats:
            if f.get('vcodec') != 'none' or f.get('acodec') != 'none':
                resolution = f.get('resolution', 'audio only')
                if resolution == 'audio only':
                    desc = f"Audio only ({f.get('abr', '?')} kbps)"
                else:
                    desc = f"{resolution} ({f.get('fps', '?')} fps) – {f.get('ext', '?')}"
                format_options[desc] = f['format_id']
        if format_options:
            selected_desc = st.selectbox("Choose a format", list(format_options.keys()))
            format_spec = format_options[selected_desc]
        else:
            st.error("No suitable formats found.")
            st.stop()

    if format_spec and st.button("🚀 Download Now", use_container_width=True):
        progress_placeholder = st.empty()
        with st.status("Downloading...", expanded=True) as status:
            try:
                with tempfile.TemporaryDirectory() as tmpdir:
                    output_template = os.path.join(tmpdir, '%(title)s.%(ext)s')
                    ydl_opts = {
                        'format': format_spec,
                        'outtmpl': output_template,
                        'quiet': True,
                        'no_warnings': True,
                        'progress_hooks': [lambda d: update_progress(d, progress_placeholder)],
                    }
                    # If merging fails and format_spec includes '+', fallback to 'best'
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        filename = ydl.prepare_filename(info)
                        # If the file doesn't exist (e.g., because merging failed), try with 'best'
                        if not os.path.exists(filename):
                            st.warning("Merging failed. Trying with 'best' format...")
                            ydl_opts['format'] = 'best'
                            with yt_dlp.YoutubeDL(ydl_opts) as ydl2:
                                info2 = ydl2.extract_info(url, download=True)
                                filename = ydl2.prepare_filename(info2)
                    if os.path.exists(filename):
                        status.update(label="Download complete!", state="complete", expanded=False)
                        with open(filename, "rb") as f:
                            file_bytes = f.read()
                        st.download_button(
                            label="💾 Save file",
                            data=file_bytes,
                            file_name=os.path.basename(filename),
                            use_container_width=True
                        )
                    else:
                        status.update(label="Download failed – file not created", state="error")
            except Exception as e:
                status.update(label=f"Error: {e}", state="error")

def update_progress(d, placeholder):
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '0%').strip()
        speed = d.get('_speed_str', 'N/A').strip()
        eta = d.get('_eta_str', 'N/A').strip()
        placeholder.markdown(f"**Downloading...** {percent} at {speed} – ETA: {eta}")
    elif d['status'] == 'finished':
        placeholder.markdown("✅ **Download finished! Processing...**")

st.markdown('<footer>⚠️ Respect YouTube’s terms of service. Download only content you have permission to.</footer>', unsafe_allow_html=True)
