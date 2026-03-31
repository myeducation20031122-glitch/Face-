import streamlit as st
from pytubefix import YouTube
import os
import tempfile

st.set_page_config(page_title="YouTube Downloader", page_icon="🎬", layout="centered")

st.markdown("""
<style>
    .title { text-align: center; color: #FF4B4B; font-size: 3rem; font-weight: bold; }
    .subtitle { text-align: center; color: #666; margin-bottom: 2rem; }
    .stButton button { background-color: #FF4B4B; color: white; width: 100%; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🎬 YouTube Downloader</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">PyTubeFix - ffmpeg අවශ්‍ය නැහැ!</div>', unsafe_allow_html=True)

url = st.text_input("🔗 YouTube URL", placeholder="https://www.youtube.com/watch?v=...")

if url:
    with st.spinner("වීඩියෝ තොරතුරු ලබා ගනිමින්..."):
        try:
            yt = YouTube(url)
            title = yt.title
            st.success(f"✅ **{title}**")
            st.info(f"⏱️ දිග: {yt.length // 60}:{yt.length % 60:02d} | 👁️ Views: {yt.views:,}")
        except Exception as e:
            st.error(f"URL එක හරිද? Error: {e}")
            st.stop()

    # Streams list එක පෙන්වන්න
    st.subheader("📥 පවතින Streams")
    
    streams = []
    stream_options = {}
    
    # Video streams (progressive = video+audio එකට)
    for s in yt.streams.filter(progressive=True):
        desc = f"🎬 {s.resolution} ({s.mime_type.split('/')[-1]})"
        stream_options[desc] = s
        streams.append(desc)
    
    # Audio only streams
    for s in yt.streams.filter(only_audio=True):
        desc = f"🎵 Audio ({s.abr}) - {s.mime_type.split('/')[-1]}"
        stream_options[desc] = s
        streams.append(desc)
    
    if streams:
        selected_desc = st.selectbox("Stream එක තෝරන්න", streams)
        selected_stream = stream_options[selected_desc]
        
        st.info(f"📁 File size: {selected_stream.filesize_mb:.1f} MB")
        
        if st.button("🚀 Download Now", use_container_width=True):
            with tempfile.TemporaryDirectory() as tmpdir:
                with st.status("Downloading...", expanded=True) as status:
                    try:
                        # Progress callback
                        def on_progress(stream, chunk, bytes_remaining):
                            total = stream.filesize
                            bytes_downloaded = total - bytes_remaining
                            percent = (bytes_downloaded / total) * 100
                            status.write(f"Downloading: {percent:.1f}%")
                        
                        # Create YouTube object with progress
                        yt_with_progress = YouTube(url, on_progress_callback=on_progress)
                        
                        if selected_stream.includes_audio and selected_stream.includes_video:
                            stream_to_download = yt_with_progress.streams.get_by_itag(selected_stream.itag)
                        else:
                            stream_to_download = selected_stream
                        
                        file_path = stream_to_download.download(output_path=tmpdir)
                        
                        status.update(label="Complete!", state="complete")
                        
                        with open(file_path, "rb") as f:
                            file_bytes = f.read()
                        
                        st.download_button(
                            label="💾 Save File",
                            data=file_bytes,
                            file_name=os.path.basename(file_path),
                            use_container_width=True
                        )
                    except Exception as e:
                        status.update(label=f"Error: {e}", state="error")
    else:
        st.error("Download කළ හැකි streams නොමැත.")

st.markdown("---")
st.caption("⚠️ අයිතිකරුගේ අවසරය ඇති වීඩියෝ පමණක් download කරන්න.")
