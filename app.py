import streamlit as st
import face_recognition
from PIL import Image, ImageDraw
import cloudinary
import cloudinary.uploader
import io
import numpy as np
from datetime import datetime

# Cloudinary Config
cloudinary.config( 
  cloud_name = "dpmlwaai1", 
  api_key = "595869732658717", 
  api_secret = "l9UkpC2cniUZVNJf0nW_wOMU0gI",
  secure = True
)

st.set_page_config(page_title="BIO-SHIELD ELITE", layout="wide")
st.title("🛡️ BIO-SHIELD v4.0 (The Final Fix)")

menu = st.sidebar.selectbox("Navigation", ["👤 Register Identity", "🔍 Intelligence Logs"])

def apply_forensic_mesh(image_file):
    # පින්තූරය load කරගැනීම
    image = face_recognition.load_image_file(image_file)
    # මුහුණේ ලක්ෂණ සෙවීම (Eyes, Nose, Mouth)
    face_landmarks_list = face_recognition.face_landmarks(image)
    
    pil_image = Image.fromarray(image)
    d = ImageDraw.Draw(pil_image)
    
    face_found = False
    for face_landmarks in face_landmarks_list:
        face_found = True
        # මුහුණේ හැම ලක්ෂණයක්ම ඉරි වලින් ඇඳීම
        for facial_feature in face_landmarks.keys():
            d.line(face_landmarks[facial_feature], fill=(0, 255, 0), width=2)
            
    return pil_image, face_found

if menu == "👤 Register Identity":
    name = st.text_input("Person Name:")
    snap = st.camera_input("Biometric Scan")
    
    if snap and name:
        with st.spinner("Executing AI Forensic Mesh..."):
            processed_img, found = apply_forensic_mesh(snap)
            
            # Bytes වලට හරවා ගැනීම
            buf = io.BytesIO()
            processed_img.save(buf, format='JPEG')
            
            # Cloudinary Upload
            res = cloudinary.uploader.upload(
                buf.getvalue(),
                folder="bioshield_v4",
                context={"name": name, "face": str(found), "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            )
            
            st.success(f"Archived: {name}")
            st.image(processed_img, caption="AI Landmarks Applied", width=500)

elif menu == "🔍 Intelligence Logs":
    st.header("Cloud Security Logs")
    try:
        import cloudinary.api
        res = cloudinary.api.resources(type="upload", prefix="bioshield_v4", context=True)
        cols = st.columns(3)
        for i, item in enumerate(res.get('resources', [])):
            with cols[i % 3]:
                st.image(item['secure_url'], use_container_width=True)
                info = item.get('context', {}).get('custom', {})
                st.write(f"👤 {info.get('name')}")
    except:
        st.info("No logs found.")
