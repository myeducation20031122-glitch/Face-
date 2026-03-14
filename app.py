import streamlit as st
from PIL import Image
import cloudinary
import cloudinary.uploader
import cloudinary.api  # මෙතන තමයි කලින් Error එක ආවේ, දැන් ඒක හරි
import io
from datetime import datetime

# --- 1. CLOUDINARY CONFIGURATION ---
cloudinary.config( 
  cloud_name = "dpmlwaai1", 
  api_key = "595869732658717", 
  api_secret = "l9UkpC2cniUZVNJf0nW_wOMU0gI",
  secure = True
)

# --- 2. PAGE SETTINGS ---
st.set_page_config(page_title="BIO-SHIELD ELITE", page_icon="🛡️", layout="wide")

# CSS - පෙනුම ලස්සන කරන්න
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1 { color: #00FF00; font-family: 'Courier New', Courier, monospace; }
    .stTextInput>div>div>input { background-color: #1a1c23; color: white; border: 1px solid #00FF00; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ BIO-SHIELD v5.0 (Final Fix)")

# Side Menu
menu = st.sidebar.radio("Command Center", ["👤 Enrollment", "🔍 Security Logs"])

# --- 3. ENROLLMENT (පින්තූරයක් ගෙන Cloud එකට යැවීම) ---
if menu == "👤 Enrollment":
    st.header("Identity Registration")
    name = st.text_input("Target Name:")
    role = st.selectbox("Category", ["Staff", "Visitor", "VIP", "Suspect"])
    snap = st.camera_input("Biometric Scan")
    
    if snap and name:
        with st.spinner("Encrypting and Uploading..."):
            # Pillow පාවිච්චි කරලා පින්තූරය කියවීම (No OpenCV needed)
            img = Image.open(snap)
            buf = io.BytesIO()
            img.save(buf, format='JPEG')
            byte_im = buf.getvalue()
            
            # Cloudinary Upload
            # මූණ තිබුණොත් ඒක ලස්සනට Detect කරගන්න tags එකතු කරලා තියෙනවා
            res = cloudinary.uploader.upload(
                byte_im,
                folder="bioshield_v5",
                context={"name": name, "role": role, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
                tags=[name, role, "face_id"]
            )
            
            st.success(f"✅ Target Locked: {name}")
            st.image(res['secure_url'], caption="Cloud Archived Image", width=400)

# --- 4. SECURITY LOGS (Cloud එකේ තියෙන පින්තූර පෙන්වීම) ---
elif menu == "🔍 Security Logs":
    st.header("Forensic Database Records")
    
    try:
        # Cloudinary API එකෙන් පින්තූර ලිස්ට් එකක් ගන්නවා
        resources = cloudinary.api.resources(
            type="upload", 
            prefix="bioshield_v5", 
            context=True, 
            max_results=20
        )
        
        if not resources.get('resources'):
            st.info("No logs found in the database.")
        else:
            cols = st.columns(3)
            for i, item in enumerate(resources.get('resources', [])):
                with cols[i % 3]:
                    # මෙතන මම "God Level" Trick එකක් දැම්මා:
                    # Cloudinary එකෙන්ම මූණ විතරක් Crop කරලා (Zoom කරලා) පෙන්වනවා
                    face_url = item['secure_url'].replace("/upload/", "/upload/w_400,h_400,c_thumb,g_face/")
                    
                    st.image(face_url, use_container_width=True)
                    
                    # Metadata (නම සහ වෙලාව) පෙන්වීම
                    ctx = item.get('context', {}).get('custom', {})
                    st.write(f"👤 **{ctx.get('name', 'Unknown')}**")
                    st.caption(f"🕒 {ctx.get('time', 'N/A')}")
                    st.markdown("---")
                    
    except Exception as e:
        st.error(f"Access Denied: Could not connect to Cloudinary API. ({str(e)})")
