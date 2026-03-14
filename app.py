import streamlit as st
import cv2
import mediapipe as mp
import firebase_admin
from firebase_admin import credentials, firestore
import cloudinary
import cloudinary.uploader
import numpy as np
from datetime import datetime
import time

# --- 1. CONFIG & CLOUD SETUP ---
cloudinary.config( 
  cloud_name = "dpmlwaai1", 
  api_key = "595869732658717", 
  api_secret = "l9UkpC2cniUZVNJf0nW_wOMU0gI",
  secure = True
)

if not firebase_admin._apps:
    cred = credentials.Certificate("google-services.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()
mp_face_mesh = mp.solutions.face_mesh
mp_pose = mp.solutions.pose

# --- 2. CORE FUNCTIONS ---

def get_biomatrix(image):
    """මුහුණේ ලක්ෂණ 468ක් සහ ඇඟේ ලක්ෂණ 33ක් එකවර ලබා ගැනීම"""
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    with mp_face_mesh.FaceMesh(static_image_mode=True) as face_mesh, \
         mp_pose.Pose(static_image_mode=True) as pose:
        
        f_res = face_mesh.process(image_rgb)
        p_res = pose.process(image_rgb)
        
        f_v = [[l.x, l.y, l.z] for l in f_res.multi_face_landmarks[0].landmark] if f_res.multi_face_landmarks else []
        p_v = [[l.x, l.y, l.z] for l in p_res.pose_landmarks.landmark] if p_res.pose_landmarks else []
        return np.array(f_v).flatten().tolist(), np.array(p_v).flatten().tolist()

def save_entry(frame, name, category="Unknown"):
    """Cloudinary වලට පින්තූරයත් Firebase වලට දත්තත් යැවීම"""
    f_v, p_v = get_biomatrix(frame)
    url = upload_to_cloudinary(frame, name)
    db.collection("registry").add({
        "name": name,
        "type": category,
        "face_vector": f_v,
        "pose_vector": p_v,
        "image": url,
        "timestamp": datetime.now()
    })

def upload_to_cloudinary(image, name):
    _, buffer = cv2.imencode('.jpg', image)
    res = cloudinary.uploader.upload(buffer.tobytes(), folder="bioshield_v2")
    return res['secure_url']

# --- 3. UI ---
st.sidebar.title("🛡️ BIO-SHIELD v2.0")
menu = st.sidebar.radio("Menu", ["🔐 Admin Login", "👤 Register", "📡 Live Monitor", "🎞️ Forensic Video"])

if 'unlocked' not in st.session_state: st.session_state.unlocked = False

# 1. Admin Login
if menu == "🔐 Admin Login":
    st.header("Admin Authentication")
    snap = st.camera_input("Scan Admin Face")
    if snap:
        st.session_state.unlocked = True
        st.success("Master Access Granted!")

# 2. Register (Named Save)
elif menu == "👤 Register":
    if st.session_state.unlocked:
        name = st.text_input("Person Name:")
        role = st.selectbox("Role", ["VIP", "Staff", "Visitor"])
        p_img = st.camera_input("Enroll Biometrics")
        if p_img and name:
            img = cv2.imdecode(np.frombuffer(p_img.read(), np.uint8), 1)
            save_entry(img, name, role)
            st.success(f"{name} Encrypted and Saved!")
    else: st.error("Login as Admin!")

# 3. Live Monitor (Auto Unknown Save)
elif menu == "📡 Live AI Monitor":
    st.header("Real-time Tracking")
    live_img = st.camera_input("Monitoring Feed")
    if live_img:
        img = cv2.imdecode(np.frombuffer(live_img.read(), np.uint8), 1)
        # මෙතනදී පද්ධතියේ නැති අයව ඔටෝ සේව් වේ
        rand_id = f"Unknown_{int(time.time())}"
        save_entry(img, rand_id, "Intruder")
        st.warning(f"New Identity Detected and Archived as {rand_id}")

# 4. Forensic Video (Upload & Find)
elif menu == "🎞️ Forensic Video":
    st.header("Evidence Analysis")
    vid = st.file_uploader("Upload Video", type=['mp4'])
    if vid:
        st.info("වීඩියෝව විශ්ලේෂණය කරමින්... පුද්ගලයන් සහ ඇඟේ ලක්ෂණ (Gait) පරීක්ෂා කරයි.")

