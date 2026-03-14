import streamlit as st
from PIL import Image, ImageDraw
import cloudinary
import cloudinary.uploader
import io
import mediapipe as mp
from datetime import datetime
import numpy as np

# Cloudinary Config (ඔයාගේ Keys)
cloudinary.config( 
  cloud_name = "dpmlwaai1", 
  api_key = "595869732658717", 
  api_secret = "l9UkpC2cniUZVNJf0nW_wOMU0gI",
  secure = True
)

# MediaPipe Face Mesh Setup (ලයිට් වර්ෂන් එක)
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1)

st.set_page_config(page_title="BIO-SHIELD FORENSIC", layout="wide")
st.title("🛡️ BIO-SHIELD v3.5 (Forensic Edition)")

menu = st.sidebar.selectbox("Menu", ["👤 Register Identity", "🔍 Intelligence Logs"])

def draw_mesh(image):
    """මුහුණේ ලක්ෂණ හඳුනාගෙන ඉරි/තිත් ඇඳීම"""
    img_array = np.array(image)
    results = face_mesh.process(img_array)
    draw = ImageDraw.Draw(image)
    
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            for landmark in face_landmarks.landmark:
                # තිත් ඇඳීම
                x = landmark.x * image.width
                y = landmark.y * image.height
                draw.ellipse([x-1, y-1, x+1, y+1], fill="#00FF00") # කොළ පාට තිත්
        return image, True
    return image, False

if menu == "👤 Register Identity":
    name = st.text_input("Target Name:")
    img_file = st.camera_input("Biometric Scan")
    
    if img_file and name:
        raw_image = Image.open(img_file)
        
        with st.spinner("Analyzing Biomatrix..."):
            # මූණේ ලක්ෂණ අඳිනවා
            processed_img, face_found = draw_mesh(raw_image)
            
            # Bytes වලට හරවනවා
            img_byte_arr = io.BytesIO()
            processed_img.save(img_byte_arr, format='JPEG')
            final_bytes = img_byte_arr.getvalue()
            
            # Upload කිරීම
            res = cloudinary.uploader.upload(
                final_bytes,
                folder="bioshield_forensic",
                context={"name": name, "face_detected": str(face_found), "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            )
            
            st.success(f"Archived: {name}")
            st.image(processed_img, caption="Forensic Mesh Applied", width=500)

elif menu == "🔍 Intelligence Logs":
    st.header("Global Database Logs")
    try:
        import cloudinary.api
        results = cloudinary.api.resources(type="upload", prefix="bioshield_forensic", context=True)
        cols = st.columns(3)
        for i, res in enumerate(results.get('resources', [])):
            with cols[i % 3]:
                st.image(res['secure_url'], use_container_width=True)
                ctx = res.get('context', {}).get('custom', {})
                st.write(f"👤 **{ctx.get('name')}**")
                st.caption(f"📅 {ctx.get('time')}")
    except:
        st.info("Searching for records...")
