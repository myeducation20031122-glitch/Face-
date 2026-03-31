import streamlit as st
import yt_dlp
import os
import tempfile
import subprocess

# ---------- Functions (මුලින්ම Define කරන්න ඕනේ) ----------

def update_progress(d, placeholder):
    """Download progress එක පෙන්වන function එක"""
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '0%').strip()
        speed = d.get('_speed_str', 'N/A').strip()
        eta = d.get('_eta_str', 'N/A').strip()
        placeholder.markdown(f"**Downloading...** {percent} | Speed: {speed} | ETA: {eta}")
    elif d['status'] == 'finished':
        placeholder.markdown("✅ **Download finished! Processing...**")

def check_ffmpeg():
    """ffmpeg තියෙනවාද බලන function එක"""
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except:
        return False

ffmpeg_available = check_ffmpeg()

# ---------- Page Config & CSS ----------
st.set_page_config(page_title="YouTube Downloader", page_icon="🎬", layout="centered")

st.markdown("""
<style>
    .title { text-align: center; color: #FF4B4B; font-size: 2.5rem; font-weight: bold; }
    .stButton button { background-color: #FF4B4B; color: white; border-radius: 8px; height: 3em; }
    footer { text-align: center; color: #aaa; font-size: 0.8rem; margin-top: 50px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🎬 YouTube Downloader</div>', unsafe_allow_html=True)

# ---------- UI Logic ----------
if not ffmpeg_available:
    st.warning("⚠️ **ffmpeg not found!** High-quality merge and MP3 conversion might not work perfectly.")

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
            
            download_type = st.radio(
                "📥 **Select download type**",
                ["Best quality (video + audio)", "Audio only (MP3)", "Choose specific quality"]
            )

            format_spec = None
            if download_type == "Best quality (video + audio)":
                format_spec = "bestvideo+bestaudio/best"
            elif download_type == "Audio only (MP3)":
                format_spec = "bestaudio/best"
            else:
                format_options = {f"{f.get('resolution', 'audio')} ({f.get('ext')})": f['format_id'] for f in formats if f.get('format_id')}
                selected_desc = st.selectbox("Choose a format", list(format_options.keys()))
                format_spec = format_options[selected_desc]

            if st.button("🚀 Download Now"):
                progress_placeholder = st.empty()
                with st.status("Downloading...", expanded=True) as status:
                    try:
                        # Temporary directory එකක් පාවිච්චි කිරීම (Streamlit Cloud වලට වැදගත්)
                        with tempfile.TemporaryDirectory() as tmpdir:
                            # yt-dlp options
                            ydl_opts_dl = {
                                'format': format_spec,
                                'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
                                'progress_hooks': [lambda d: update_progress(d, progress_placeholder)],
                                'noplaylist': True,
                            }
                            
                            # Audio only නම් MP3 වලට convert කරන්න ffmpeg ඕනේ
                            if download_type == "Audio only (MP3)":
                                ydl_opts_dl['postprocessors'] = [{
                                    'key': 'FFmpegExtractAudio',
                                    'preferredcodec': 'mp3',
                                    'preferredquality': '192',
                                }]

                            with yt_dlp.YoutubeDL(ydl_opts_dl) as ydl:
                                # ඇත්තටම download කරමු
                                d_info = ydl.extract_info(url, download=True)
                                # හරියටම පස්සේ හැදෙන filename එක හොයාගමු
                                final_filename = ydl.prepare_filename(d_info)
                                
                                # Audio conversion එක නිසා extension එක වෙනස් වෙන්න පුළුවන්
                                if download_type == "Audio only (MP3)":
                                    final_filename = os.path.splitext(final_filename)[0] + ".mp3"

                                if os.path.exists(final_filename):
                                    with open(final_filename, "rb") as f:
                                        st.download_button(
                                            label="💾 Save to Device",
                                            data=f.read(),
                                            file_name=os.path.basename(final_filename),
                                            mime="application/octet-stream"
                                        )
                                    status.update(label="✅ Download Ready!", state="complete")
                                else:
                                    status.update(label="❌ File creation failed.", state="error")
                    except Exception as e:
                        st.error(f"Error: {e}")

        except Exception as e:
            st.error(f"Could not fetch info: {e}")

st.markdown('<footer>⚠️ පෞද්ගලික ප්‍රයෝජනය සඳහා පමණක් භාවිතා කරන්න.</footer>', unsafe_allow_html=True)
