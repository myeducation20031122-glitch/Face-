import streamlit as st
import yt_dlp
import os
import tempfile
import shutil

# --- පේජ් එකේ පෙනුම (Hacker Style) ---
st.set_page_config(page_title="YT Downloader Pro", page_icon="🎬")

st.markdown("""
<style>
    .main { background-color: #0e1117; color: #00ff41; }
    .stTextInput>div>div>input { background-color: #1a1c24; color: #00ff41; border: 1px solid #00ff41; }
    .stButton>button { background-color: #00ff41; color: black; font-weight: bold; width: 100%; border-radius: 10px; }
    .stButton>button:hover { background-color: #ff0000; color: white; }
    h1 { text-align: center; font-family: 'Courier New', monospace; color: #00ff41; text-shadow: 2px 2px #000; }
</style>
""", unsafe_allow_html=True)

st.title("🎬 YT VIDEO HARVESTER")

# FFmpeg තියෙනවාද බලමු
ffmpeg_exists = shutil.which("ffmpeg")

if not ffmpeg_exists:
    st.sidebar.warning("⚠️ FFmpeg හමුවුණේ නැහැ. High Quality වීඩියෝ වලට මේක අත්‍යවශ්‍යයි.")
else:
    st.sidebar.success("✅ FFmpeg සක්‍රීයයි!")

# --- UI එක ---
url = st.text_input("🔗 YouTube Link එක මෙතනට පේස්ට් කරන්න:", placeholder="https://www.youtube.com/watch?v=...")

if url:
    try:
        with st.spinner("🔍 වීඩියෝ එක පරීක්ෂා කරමින්..."):
            ydl_opts = {'quiet': True, 'noplaylist': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                st.image(info.get('thumbnail'), width=400)
                st.write(f"🎯 **Target:** {info.get('title')}")

        option = st.selectbox("📥 Format එක තෝරන්න:", ["Video (MP4)", "Audio (MP3)"])

        if st.button("🚀 DOWNLOAD NOW"):
            with tempfile.TemporaryDirectory() as tmpdir:
                status = st.empty()
                status.info("⏳ වැඩේ පටන් ගත්තා... පොඩ්ඩක් ඉන්න බොසා.")

                # Download Options
                if option == "Audio (MP3)":
                    opts = {
                        'format': 'bestaudio/best',
                        'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }] if ffmpeg_exists else [],
                    }
                else:
                    opts = {
                        'format': 'bestvideo+bestaudio/best' if ffmpeg_exists else 'best',
                        'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
                        'merge_output_format': 'mp4' if ffmpeg_exists else None,
                    }

                with yt_dlp.YoutubeDL(opts) as ydl:
                    info_dict = ydl.extract_info(url, download=True)
                    file_path = ydl.prepare_filename(info_dict)
                    
                    # MP3 එකක් නම් extension එක මාරු වෙන්න පුළුවන්
                    if option == "Audio (MP3)" and ffmpeg_exists:
                        file_path = os.path.splitext(file_path)[0] + ".mp3"

                    if os.path.exists(file_path):
                        with open(file_path, "rb") as f:
                            st.download_button(
                                label="💾 Save to Device",
                                data=f.read(),
                                file_name=os.path.basename(file_path),
                                mime="application/octet-stream"
                            )
                        st.balloons()
                        status.success("✅ වැඩේ ගොඩ! පහල Button එකෙන් Save කරගන්න.")
                    else:
                        status.error("❌ ෆයිල් එක හදාගන්න බැරි වුණා. FFmpeg අවුලක් වෙන්න ඇති.")

    except Exception as e:
        st.error(f"💀 අවුලක් වුණා: {str(e)}")
