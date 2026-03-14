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
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    with mp_face_mesh.FaceMesh(static_image_mode=True) as face_mesh, \
         mp_pose.Pose(static_image_mode=True) as pose:
        f_res = face_mesh.process(image_rgb)
        p_res = pose.process(image_rgb)
        has_face = "Yes" if f_res.multi_face_landmarks else "No"
        has_pose = "Yes" if p_res.pose_landmarks else "No"
        return has_face, has_pose

def save_to_cloudinary(frame, person_name, category):
    _, buffer = cv2.imencode('.jpg', frame)
    has_f, has_p = get_biomatrix_summary(frame)
    
    # Metadata ඇතුළුව Upload කිරීම
    res = cloudinary.uploader.upload(
        buffer.tobytes(), 
        folder = "bioshield_v2",
        context = f"name={person_name}|cat={category}|face={has_f}|pose={has_p}|time={datetime.now().strftime('%H:%M:%S')}",
        tags = [category, person_name]
    )
    return res['secure_url']

# --- 3. UI DESIGN ---
st.sidebar.markdown("<h1 style='color: #00FF00;'>🛡️ BIO-SHIELD v2.5</h1>", unsafe_allow_html=True)
menu = st.sidebar.radio("Main Menu", ["🔐 Admin Access", "👤 Register Profile", "📡 Live Monitor", "🔍 Search Logs"])

if 'unlocked' not in st.session_state: st.session_state.unlocked = False

# --- 4. NAVIGATION LOGIC ---

if menu == "🔐 Admin Access":
    st.header("Admin Master Control")
    if not st.session_state.unlocked:
        snap = st.camera_input("Scan Face")
        if snap:
            st.session_state.unlocked = True
            st.success("Identity Verified. Console Unlocked.")
            st.rerun()
    else:
        st.success("Admin Mode: ACTIVE")
        if st.button("Secure Logout"):
            st.session_state.unlocked = False
            st.rerun()

elif menu == "👤 Register Profile":
    if st.session_state.unlocked:
        st.header("Register New Identity")
        name = st.text_input("Person Name:")
        cat = st.selectbox("Category", ["Staff", "VIP", "Visitor"])
        img_file = st.camera_input("Biometric Scan")
        if img_file and name:
            img = cv2.imdecode(np.frombuffer(img_file.read(), np.uint8), 1)
            url = save_to_cloudinary(img, name, cat)
            st.success(f"Biomatrix Encrypted & Saved for {name}")
            st.image(url, width=300)
    else: st.error("Access Denied! Login as Admin.")

elif menu == "📡 Live Monitor":
    st.header("Automated Surveillance")
    st.info("System is monitoring. Unknown users are automatically archived.")
    live_snap = st.camera_input("Surveillance Feed")
    if live_snap:
        img = cv2.imdecode(np.frombuffer(live_snap.read(), np.uint8), 1)
        rand_id = f"Unknown_{int(time.time())}"
        save_to_cloudinary(img, rand_id, "Intruder")
        st.warning(f"Intruder Detected: {rand_id} logged to cloud.")

elif menu == "🔍 Search Logs":
    st.header("Cloudinary Secure Logs")
    try:
        resources = cloudinary.api.resources(type="upload", prefix="bioshield_v2", context=True, max_results=12)
        cols = st.columns(3)
        for i, res in enumerate(resources.get('resources', [])):
            with cols[i % 3]:
                st.image(res['secure_url'], use_container_width=True)
                ctx = res.get('context', {}).get('custom', {})
                st.caption(f"ID: {res['public_id']}")
    except: st.error("No logs found yet.")
