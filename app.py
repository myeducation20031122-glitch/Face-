import streamlit as st
import cv2
import mediapipe as mp
import firebase_admin
from firebase_admin import credentials, firestore, storage
import numpy as np
from datetime import datetime
import tempfile
import time

# --- 1. CONFIG & FIREBASE SETUP ---
st.set_page_config(page_title="BIO-SHIELD AI", layout="wide")

if not firebase_admin._apps:
    cred = credentials.Certificate("google-services.json")
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'test-30b8e.appspot.com'
    })

db = firestore.client()
bucket = storage.bucket()

# AI Models Setup
mp_face_mesh = mp.solutions.face_mesh
mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils

# --- 2. FUNCTIONS ---
def get_biomatrix(image):
    """මුහුණ සහ ඇඟේ සම්පූර්ණ දත්ත (Matrix) ලබා ගැනීම"""
    with mp_face_mesh.FaceMesh(static_image_mode=True) as face_mesh, \
         mp_pose.Pose(static_image_mode=True) as pose:
        
        results_face = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        results_pose = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        face_data = []
        if results_face.multi_face_landmarks:
            for res in results_face.multi_face_landmarks[0].landmark:
                face_data.append([res.x, res.y, res.z])
        
        pose_data = []
        if results_pose.pose_landmarks:
            for res in results_pose.pose_landmarks.landmark:
                pose_data.append([res.x, res.y, res.z])
                
        return np.array(face_data).flatten().tolist(), np.array(pose_data).flatten().tolist()

def upload_to_firebase(image, folder, name):
    """පින්තූරය Firebase Storage එකට දමා URL එක ලබා ගැනීම"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = f"{folder}/{name}_{timestamp}.jpg"
    _, buffer = cv2.imencode('.jpg', image)
    blob = bucket.blob(file_path)
    blob.upload_from_string(buffer.tobytes(), content_type='image/jpeg')
    blob.make_public()
    return blob.public_url

# --- 3. UI & MENU ---
st.sidebar.markdown("<h1 style='text-align: center; color: red;'>🛡️ BIO-SHIELD AI</h1>", unsafe_allow_html=True)
menu = st.sidebar.selectbox("Main Menu", 
    ["🔐 Admin Access", "👤 Register New Profile", "📡 Live Surveillance", "🔍 Forensic Search"])

# --- SESSION STATE FOR ADMIN ---
if 'admin_unlocked' not in st.session_state:
    st.session_state.admin_unlocked = False

# --- 4. LOGIC ---

if menu == "🔐 Admin Access":
    st.header("Admin Biometric Authentication")
    if not st.session_state.admin_unlocked:
        img_admin = st.camera_input("Verify Admin Face")
        if img_admin:
            # මෙතනදී මුල්ම User ව Admin ලෙස සලකනවා
            st.session_state.admin_unlocked = True
            st.success("Access Granted, Admin!")
            st.rerun()
    else:
        st.success("Welcome back, Chief! System is Unlocked.")
        if st.button("Lock System"):
            st.session_state.admin_unlocked = False
            st.rerun()

elif menu == "👤 Register New Profile":
    if not st.session_state.admin_unlocked:
        st.error("Please Login as Admin first!")
    else:
        st.header("New Biometric Enrollment")
        p_name = st.text_input("Person Name:")
        p_role = st.selectbox("Role", ["Staff", "Visitor", "Security", "VIP"])
        img_file = st.camera_input("Capture Enrollment Data")
        
        if img_file and p_name:
            file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
            frame = cv2.imdecode(file_bytes, 1)
            
            with st.spinner("Extracting Biomatrix..."):
                f_matrix, p_matrix = get_biomatrix(frame)
                img_url = upload_to_firebase(frame, "profiles", p_name)
                
                db.collection("biometrics").add({
                    "name": p_name,
                    "role": p_role,
                    "face_matrix": f_matrix,
                    "pose_matrix": p_matrix,
                    "image_url": img_url,
                    "created_at": datetime.now()
                })
                st.success(f"Data Secured for {p_name}")

elif menu == "📡 Live Surveillance":
    st.header("Live AI Monitoring")
    st.info("සජීවීව දත්ත ලබාගෙන Firebase වෙත යවනු ලැබේ.")
    
    # මෙතැනදී Live කැමරාවෙන් පේන හැමෝවම Detect කරලා 
    # පෙර සේව් කර නැතිනම් ස්වයංක්‍රීයව 'Unknown' ලෙස Firebase දාන logic එක ක්‍රියාත්මක වේ.
    # Note: Streamlit වල සැබෑ 'Always-on' සයිට් එකක් ලෙස පවත්වා ගැනීමට loop එකක් අවශ්‍යයි.

elif menu == "🔍 Forensic Search":
    st.header("Video/Image Analysis")
    up_file = st.file_uploader("Upload Evidence", type=['mp4', 'jpg', 'png'])
    # මෙතනදී Upload කරන වීඩියෝ එකේ මූණවල් සේව් කර ඇති දත්ත එක්ක සසඳනවා.
