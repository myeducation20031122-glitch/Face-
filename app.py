import streamlit as st
import cv2
import numpy as np
import pickle
import os

# දත්ත ගොනුව
DATA_FILE = "biometric_data.pkl"

# මූලික දත්ත සකස් කිරීම
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "wb") as f:
        pickle.dump({"encodings": [], "names": []}, f)

st.set_page_config(page_title="Biometric ID System", layout="centered")
st.title("👤 Biometric Identity System")

# දත්ත Load කිරීම
with open(DATA_FILE, "rb") as f:
    known_data = pickle.load(f)

# 1. පියවර: ලියාපදිංචි කිරීම (Enrollment)
st.header("📸 Step 1: Register Person")
name = st.text_input("Enter Name:")
img_file = st.camera_input("Take a Biometric Snap")

if img_file and name:
    # මෙතැනදී Biometric දත්ත ලබා ගැනීමේ logic එක ක්‍රියාත්මක වේ
    st.success(f"Biometric data for {name} saved!")
    # (මෙහිදී encoding එක save කිරීමට ඉහත logic එක භාවිතා කරන්න)

st.markdown("---")

# 2. පියවර: වීඩියෝවෙන් හඳුනාගැනීම (Identification)
st.header("🔍 Step 2: Identify from Video")
video_file = st.file_uploader("Upload Video File", type=['mp4', 'mov', 'avi'])

if video_file:
    st.info("Video received. Analyzing biometric patterns...")
    # වීඩියෝව පරීක්ෂා කරන logic එක මෙතැනට
