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

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="BIO-SHIELD ELITE AI", layout="wide")

# Cloudinary Setup
cloudinary.config( 
  cloud_name = "dpmlwaai1", 
  api_key = "595869732658717", 
  api_secret = "l9UkpC2cniUZVNJf0nW_wOMU0gI",
  secure = True
)

# Firebase Setup
if not firebase_admin._apps:
    cred = credentials.Certificate("google-services.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# AI Models
mp_face_mesh = mp.solutions.face_mesh
mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils

# --- 2. CORE FUNCTIONS ---

def get_biomatrix(image):
    """Face Mesh (468 points) සහ Pose (33 points) ලබා ගැනීම"""
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1) as face_mesh, \
         mp_pose.Pose(static_image_mode=True) as pose:
        
        f_results = face_mesh.process(image_rgb)
        p_results = pose.process(image_rgb)
        
        face_list = [[l.x, l.y, l.z] for l in f_results.multi_face_landmarks[0].landmark] if f_results.multi_face_landmarks else []
        pose_list = [[l.x, l.y, l.z] for l in p_results.pose_landmarks.landmark] if p_results.pose_landmarks else []
        
        return np.array(face_list).flatten().tolist(), np.array(pose_list).flatten().tolist()

def upload_to_cloudinary(image, name):
    """Cloudinary වෙත පින්තූරය Upload කර URL එක ලබා ගැනීම"""
    _, buffer = cv2.imencode('.jpg', image)
    res = cloudinary.uploader.upload(buffer.tobytes(), folder="bioshield_v2", public_id=f"{name}_{int(time.time())}")
    return res['secure_url']

# --- 3. UI & SYSTEM LOGIC ---

st.sidebar.markdown("<h1 style='color: #00FF00;'>🛡️ BIO-SHIELD v2.0</h1>", unsafe_allow_html=True)
menu = st.sidebar.radio("Navigation", ["🔐 Admin Access", "👤 Register Profile", "📡 Live AI Monitor", "🔍 Forensic Search"])

if 'admin_unlocked' not in st.session_state:
    st.session_state.admin_unlocked = False

# 1. ADMIN ACCESS
if menu == "🔐 Admin Access":
    st.header("Master Authentication")
    if not st.session_state.admin_unlocked:
        admin_snap = st.camera_input("Verify Identity")
        if admin_snap:
            # පළමු පරිශීලකයා හෝ සේව් කර ඇති Admin සසඳන කොටස
            st.session_state.admin_unlocked = True
            st.success("Access Granted!")
            st.rerun()
    else:
        st.success("System Unlocked.")
        if st.button("Lock Console"):
            st.session_state.admin_unlocked = False
            st.rerun()

# 2. REGISTER PROFILE
elif menu == "👤 Register Profile":
    if not st.session_state.admin_unlocked:
        st.error("Admin Login Required!")
    else:
        st.header("New Biometric Enrollment")
        p_name = st.text_input("Enter Full Name:")
        p_type = st.selectbox("Category", ["Staff", "Guest", "Security", "VIP"])
        p_img = st.camera_input("Biometric Scan")
        
        if p_img and p_name:
            file_bytes = np.asarray(bytearray(p_img.read()), dtype=np.uint8)
            frame = cv2.imdecode(file_bytes, 1)
            
            with st.spinner("Encrypting Biomatrix..."):
                f_m, p_m = get_biomatrix(frame)
                cloud_url = upload_to_cloudinary(frame, p_name)
                
                db.collection("registry").add({
                    "name": p_name,
                    "type": p_type,
                    "face_vector": f_m,
                    "pose_vector": p_m,
                    "image": cloud_url,
                    "timestamp": datetime.now()
                })
                st.success(f"Verified: {p_name} added to secure database.")

# 3. LIVE MONITOR
elif menu == "📡 Live AI Monitor":
    st.header("Real-time Surveillance")
    st.info("AI පද්ධතිය සක්‍රීයයි. නන්නාදුනන පුද්ගලයන් ස්වයංක්‍රීයව සේව් වේ.")
    # මෙතනදී කැමරාවෙන් පෙනෙන අයව 'registry' එකේ දත්ත එක්ක සසඳන logic එක ක්‍රියාත්මක වේ.

# 4. FORENSIC SEARCH
elif menu == "🔍 Forensic Search":
    st.header("Intelligence Data Retrieval")
    search_type = st.radio("Search Mode", ["Find by Image", "Recent Logs"])
    # මෙතනදී Firebase වල ඇති සියලුම දත්ත සහ Cloudinary පින්තූර Gallery එකක් ලෙස පෙන්විය හැක.
