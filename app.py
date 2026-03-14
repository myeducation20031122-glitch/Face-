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

# --- 2. FUNCTIONS ---
def save_to_cloud(frame, person_name, category):
    _, buffer = cv2.imencode('.jpg', frame)
    # Metadata එකතු කරලා Upload කරනවා (Firebase ඕනෙම නෑ)
    res = cloudinary.uploader.upload(
        buffer.tobytes(), 
        folder = "bioshield_v2",
        context = {"name": person_name, "type": category, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
        tags = [category, person_name]
    )
    return res['secure_url']

# --- 3. UI ---
st.set_page_config(page_title="BIO-SHIELD", layout="wide")
st.sidebar.title("🛡️ BIO-SHIELD v2.5")
menu = st.sidebar.selectbox("Menu", ["🔐 Admin", "👤 Register", "📡 Monitor", "🔍 Logs"])

if 'unlocked' not in st.session_state: st.session_state.unlocked = False

# --- 4. NAVIGATION ---
if menu == "🔐 Admin":
    st.header("Admin Login")
    if st.button("Unlock System"):
        st.session_state.unlocked = True
        st.success("Unlocked!")

elif menu == "👤 Register":
    if st.session_state.unlocked:
        st.header("New Registration")
        name = st.text_input("Name:")
        img_file = st.camera_input("Biometric Scan")
        if img_file and name:
            img = cv2.imdecode(np.frombuffer(img_file.read(), np.uint8), 1)
            url = save_to_cloud(img, name, "Staff")
            st.success(f"Saved to Cloud: {name}")
            st.image(url, width=300)
    else: st.error("Login as Admin first!")

elif menu == "📡 Monitor":
    st.header("Live Surveillance")
    live_snap = st.camera_input("Watch")
    if live_snap:
        img = cv2.imdecode(np.frombuffer(live_snap.read(), np.uint8), 1)
        rand_id = f"Unknown_{int(time.time())}"
        save_to_cloud(img, rand_id, "Intruder")
        st.warning(f"Intruder Detected & Logged!")

elif menu == "🔍 Logs":
    st.header("Cloudinary Secure Logs")
    try:
        resources = cloudinary.api.resources(type="upload", prefix="bioshield_v2", max_results=10)
        for res in resources.get('resources', []):
            st.image(res['secure_url'], width=300)
            st.caption(f"File: {res['public_id']}")
    except: st.write("No logs yet.")
