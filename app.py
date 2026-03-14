import streamlit as st
import cv2
import face_recognition
import numpy as np
import pickle
import os

# දත්ත ගබඩා කරන ගොනුව
DATA_FILE = "encoded_faces.pkl"

# පවතින දත්ත Load කරගැනීම
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "rb") as f:
        known_data = pickle.load(f)
else:
    known_data = {"encodings": [], "names": []}

st.title("Biometric ID System")

# 1. සජීවීව දත්ත ලබා ගැනීම (Live Enrollment)
st.header("1. Live Enrollment")
img_file = st.camera_input("Take a photo to register")

if img_file:
    bytes_data = img_file.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    rgb_img = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    
    # Encoding ලබා ගැනීම
    boxes = face_recognition.face_locations(rgb_img)
    encodings = face_recognition.face_encodings(rgb_img, boxes)
    
    if encodings:
        known_data["encodings"].append(encodings[0])
        known_data["names"].append(f"Person {len(known_data['names'])+1}")
        
        with open(DATA_FILE, "wb") as f:
            pickle.dump(known_data, f)
        st.success("biometric data saved successfully!")

---

# 2. වීඩියෝවක් මගින් හඳුනාගැනීම (Recognition)
st.header("2. Identify from Video")
video_file = st.file_uploader("Upload a video", type=["mp4", "mov"])

if video_file and known_data["encodings"]:
    st.write("Processing video...")
    # මෙහිදී වීඩියෝවේ Frames කියවා compare_faces() මගින් හඳුනාගැනීම සිදු කරයි
    # (සරල බව සඳහා මෙහි කෙටි කර දක්වා ඇත)
    st.info("Matching faces with saved biometric database...")
