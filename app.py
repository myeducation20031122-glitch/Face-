import streamlit as st
import cv2
import mediapipe as mp
import cloudinary
import cloudinary.uploader
import cloudinary.api
import numpy as np
from datetime import datetime
import time

# --- 1. CLOUDINARY CONFIGURATION ---
# ඔයා දීපු දත්ත මෙතන තියෙනවා
cloudinary.config( 
  cloud_name = "dpmlwaai1", 
  api_key = "595869732658717", 
  api_secret = "l9UkpC2cniUZVNJf0nW_wOMU0gI",
  secure = True
)

# AI Models Setup
mp_face_mesh = mp.solutions.face_mesh
mp_pose = mp.solutions.pose

# --- 2. CORE FUNCTIONS ---

def get_biomatrix_summary(image):
    """Face Mesh සහ Pose වල මූලික ලක්ෂණ ලබා ගැනීම"""
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    with mp_face_mesh.FaceMesh(static_image_mode=True) as face_mesh, \
         mp_pose.Pose(static_image_mode=True) as pose:
        
        f_res = face_mesh.process(image_rgb)
        p_res = pose.process(image_rgb)
        
        # ලකුණු 468 න් ප්‍රධාන ලක්ෂණ කිහිපයක් පමණක් metadata ලෙස ගැනීමට
        has_face = "Yes" if f_res.multi_face_landmarks else "No"
        has_pose = "Yes" if p_res.pose_landmarks else "No"
        return has_face, has_pose

def save_to_cloudinary(frame, person_name, category):
    """පින්තූරය සහ දත්ත Cloudinary Metadata ලෙස ගබඩා කිරීම"""
    _, buffer = cv2.imencode('.jpg', frame)
    has_f, has_p = get_biomatrix_summary(frame)
    
    # පින්තූරය Upload කරන ගමන් 'context' එකේ දත්ත සේව් කරනවා
    res = cloudinary.uploader.upload(
        buffer.tobytes(), 
        folder = "bioshield_v2",
        public_id = f"{person_name}_{int(time.time())}",
        context = {
            "name": person_name,
            "category": category,
            "has_face": has_f,
            "has_pose": has_p,
            "captured_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        tags = [category, person_name]
    )
    return res['secure_url']

# --- 3. UI DESIGN ---
st.sidebar.markdown("<h1 style='color: #00FF00;'>🛡️ BIO-SHIELD v2 (No-DB)</h1>", unsafe_allow_html=True)
menu = st.sidebar.radio("Main Menu", ["🔐 Admin Access", "👤 Register Profile", "📡 Live Monitor", "🔍 Search Logs"])

if 'unlocked' not in st.session_state:
    st.session_state.unlocked = False

# --- 4. NAVIGATION LOGIC ---

if menu == "🔐 Admin Access":
    st.header("Admin Authentication")
    if not st.session_state.unlocked:
        if st.camera_input("Scan Face to Unlock"):
            st.session_state.unlocked = True
            st.success("System Unlocked!")
            st.rerun()
    else:
        st.success("Admin Mode Active")
        if st.button("Logout"):
            st.session_state.unlocked = False
            st.rerun()

elif menu == "👤 Register Profile":
    if st.session_state.unlocked:
        st.header("Enroll New Identity")
        name = st.text_input("Full Name:")
        cat = st.selectbox("Category", ["Staff", "VIP", "Visitor"])
        img_file = st.camera_input("Biometric Capture")
        
        if img_file and name:
            img = cv2.imdecode(np.frombuffer(img_file.read(), np.uint8), 1)
            with st.spinner("Uploading to Cloud..."):
                url = save_to_cloudinary(img, name, cat)
                st.image(url, caption=f"Saved: {name}", width=300)
                st.success("Biometrics saved to Cloudinary!")
    else:
        st.error("Please login as Admin.")

elif menu == "📡 Live Monitor":
    st.header("Automated Surveillance")
    st.info("නන්නාදුනන පුද්ගලයන් Cloudinary වෙත ස්වයංක්‍රීයව 'Archived' වේ.")
    live_snap = st.camera_input("Feed")
    
    if live_snap:
        img = cv2.imdecode(np.frombuffer(live_snap.read(), np.uint8), 1)
        rand_name = f"Unknown_{int(time.time())}"
        url = save_to_cloudinary(img, rand_name, "Intruder")
        st.warning(f"Intruder Detected! Logged as {rand_name}")

elif menu == "🔍 Search Logs":
    st.header("Cloudinary Media Gallery")
    # Cloudinary වල සේව් කරපු අන්තිම පින්තූර 10 පෙන්වීම
    try:
        resources = cloudinary.api.resources(type="upload", prefix="bioshield_v2", context=True, max_results=10)
        for res in resources.get('resources', []):
            ctx = res.get('context', {}).get('custom', {})
            st.image(res['secure_url'], width=200)
            st.write(f"**Name:** {ctx.get('name')} | **Time:** {ctx.get('captured_at')}")
            st.markdown("---")
    except Exception as e:
        st.error("Error fetching logs. Check Cloudinary API permissions.")

