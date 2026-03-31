import streamlit as st
import yt_dlp
import os
import tempfile
import shutil

# --- පේජ් එකේ පෙනුම (Hacker Interface) ---
st.set_page_config(page_title="YT Harvester V3", page_icon="🕵️‍♂️")

st.markdown("""
<style>
    .stApp { background-color: #0a0a0a; color: #00ff41; }
    .stTextInput>div>div>input { background-color: #111; color: #00ff41; border: 1px solid #00ff41; }
    .stSelectbox>div>div>div { background-color: #111; color: #00ff41; }
    .stButton>button { background-color: #00ff41; color: black; font-weight: bold; width: 100%; border: none; }
    .stButton>button:hover { background-color: #ff0000; color: white; }
    h1 { text-align: center; font-family: 'Courier New', monospace; text-shadow: 3px 3px #000; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>💀 YT HARVESTER v3.0 💀</h1>", unsafe_allow_html=True)

# FFmpeg Status Check
ffmpeg_path = shutil.which("ffmpeg")
if ffmpeg_path:
    st.sidebar.success("✅ SYSTEM READY: FFmpeg detected.")
else:
    st.sidebar.error("⚠️ SYSTEM CRITICAL: FFmpeg missing.")

# --- ⚙️ TARGET ACQUISITION ---
url = st.text_input("🔗 [ENTER TARGET URL] > ", placeholder="Paste YouTube link here...")

if url:
    try:
        # වීඩියෝ එකේ විස්තර ගන්න කලින් පාවිච්චි කරන options
        fetch_opts = {
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'addheader': [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')],
        }

        with st.spinner("🕵️‍♂️ SCANNING TARGET DATA..."):
            with yt_dlp.YoutubeDL(fetch_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                st.image(info.get('thumbnail'), width=450)
                st.write(f"📂 **FILE IDENTIFIED:** {info.get('title')}")

        mode = st.selectbox("📂 SELECT MODE:", ["Video (MP4 High Quality)", "Audio (MP3 High Quality)"])

        if st.button("⚡ INITIATE HARVESTING"):
            with tempfile.TemporaryDirectory() as tmpdir:
                status = st.empty()
                status.warning("📡 ACCESSING YOUTUBE SERVERS... PLEASE WAIT.")

                # ඔයා දුන්නු සුපිරි Options ටික මෙන්න මෙතනට ඇඩ් කළා
                dl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'nocheckcertificate': True,
                    'ignoreerrors': False,
                    'logtostderr': False,
                    'addheader': [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')],
                    'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
                    'noplaylist': True,
                }

                # Mode එක අනුව Options වෙනස් කරනවා
                if mode == "Audio (MP3)":
                    dl_opts['format'] = 'bestaudio/best'
                    if ffmpeg_path:
                        dl_opts['postprocessors'] = [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }]
                else:
                    dl_opts['format'] = 'bestvideo+bestaudio/best' if ffmpeg_path else 'best'
                    dl_opts['merge_output_format'] = 'mp4' if ffmpeg_path else None

                # Download process
                with yt_dlp.YoutubeDL(dl_opts) as ydl:
                    data = ydl.extract_info(url, download=True)
                    final_file = ydl.prepare_filename(data)
                    
                    # MP3 extension fix
                    if mode == "Audio (MP3)" and ffmpeg_path:
                        final_file = os.path.splitext(final_filename)[0] + ".mp3"

                    if os.path.exists(final_file):
                        with open(final_file, "rb") as f:
                            st.download_button(
                                label="💾 DOWNLOAD HARVESTED DATA",
                                data=f.read(),
                                file_name=os.path.basename(final_file),
                                mime="application/octet-stream"
                            )
                        status.success("🏆 MISSION ACCOMPLISHED! DATA SECURED.")
                    else:
                        status.error("❌ EXTRACTION FAILED: Stream check failed.")

    except Exception as e:
        st.error(f"💀 CORE ERROR: {str(e)}")

st.markdown("<br><hr><center>STATUS: ENCRYPTED | BY: Gem AI</center>", unsafe_allow_html=True)
