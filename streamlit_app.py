import streamlit as st
import yt_dlp
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
st.markdown('<div class="subtitle">No ffmpeg required</div>', unsafe_allow_html=True)

url = st.text_input("🔗 YouTube URL", placeholder="https://www.youtube.com/watch?v=...")

if url:
    with st.spinner("Fetching video info..."):
        try:
            ydl_opts = {'quiet': True, 'no_warnings': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'video')
                formats = info.get('formats', [])
            st.success(f"✅ **{title}**")
        except Exception as e:
            st.error(f"Could not fetch video info:\n\n{e}")
            st.stop()

    # Build list of single-stream formats (progressive)
    single_streams = []
    for f in formats:
        # Progressive: both video and audio in one stream
        if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
            resolution = f.get('resolution', 'unknown')
            ext = f.get('ext', 'unknown')
            format_id = f.get('format_id')
            single_streams.append({
                'format_id': format_id,
                'description': f"{resolution} ({ext})",
                'filesize': f.get('filesize', 0)
            })

    # Also add audio-only streams
    audio_streams = []
    for f in formats:
        if f.get('acodec') != 'none' and f.get('vcodec') == 'none':
            abr = f.get('abr', '?')
            ext = f.get('ext', 'unknown')
            format_id = f.get('format_id')
            audio_streams.append({
                'format_id': format_id,
                'description': f"Audio only ({abr} kbps) - {ext}",
                'filesize': f.get('filesize', 0)
            })

    all_streams = single_streams + audio_streams

    if not all_streams:
        st.error("No downloadable formats found.")
        st.stop()

    # Let user choose
    options = {s['description']: s for s in all_streams}
    selected_desc = st.selectbox("📥 Choose format", list(options.keys()))
    selected = options[selected_desc]
    format_id = selected['format_id']

    if selected['filesize']:
        size_mb = selected['filesize'] / (1024*1024)
        st.info(f"📁 File size: {size_mb:.1f} MB")

    if st.button("🚀 Download Now", use_container_width=True):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_template = os.path.join(tmpdir, '%(title)s.%(ext)s')
            ydl_opts = {
                'format': format_id,
                'outtmpl': output_template,
                'quiet': False,   # show details in logs
                'no_warnings': False,
                'verbose': True,  # will help debugging
            }

            with st.status("Downloading...", expanded=True) as status:
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        filename = ydl.prepare_filename(info)

                    if os.path.exists(filename):
                        status.update(label="✅ Download complete!", state="complete", expanded=False)
                        with open(filename, "rb") as f:
                            file_bytes = f.read()
                        st.download_button(
                            label="💾 Save file",
                            data=file_bytes,
                            file_name=os.path.basename(filename),
                            use_container_width=True
                        )
                    else:
                        status.update(label="❌ Download failed – file not found", state="error")
                except Exception as e:
                    status.update(label="❌ Download failed", state="error")
                    st.error(f"**Error:**\n\n```\n{e}\n```")
                    # Also show the full traceback (for debugging)
                    import traceback
                    st.code(traceback.format_exc())

st.markdown("---")
st.caption("⚠️ Only download videos you have permission to.")
