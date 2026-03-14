import streamlit as st
from PIL import Image
import cloudinary
import cloudinary.uploader
import io
from datetime import datetime

# Cloudinary Config
cloudinary.config( 
  cloud_name = "dpmlwaai1", 
  api_key = "595869732658717", 
  api_secret = "l9UkpC2cniUZVNJf0nW_wOMU0gI",
  secure = True
)

st.set_page_config(page_title="BIO-SHIELD ULITE", page_icon="🛡️")

# CSS එකක් දාලා සයිට් එක සුපිරියටම හදමු
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #00FF00; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #00FF00; color: black; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ BIO-SHIELD v5.0 (Extreme Pro)")

menu = st.sidebar.radio("Console", ["👤 Enrollment", "🔍 Security Logs"])

if menu == "👤 Enrollment":
    st.header("New Biometric Entry")
    name = st.text_input("Person Name:")
    role = st.selectbox("Access Level", ["VIP", "Staff", "Visitor"])
    snap = st.camera_input("Scan Identity")
    
    if snap and name:
        with st.spinner("Uploading to Secure Cloud..."):
            # පින්තූරය කියවීම
            img = Image.open(snap)
            buf = io.BytesIO()
            img.save(buf, format='JPEG')
            
            # Cloudinary වෙත යැවීම (මූණ හඳුනාගැනීමේ Feature එකත් එක්ක)
            # 'detection' එකෙන් මූණ තියෙන තැන ස්වයංක්‍රීයව සේව් වෙනවා
            res = cloudinary.uploader.upload(
                buf.getvalue(),
                folder="bioshield_v5",
                context={"name": name, "role": role, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
                detection="adv_face", # Cloudinary AI එකට වැඩේ බාර දෙනවා
                tags=[name, role]
            )
            
            st.success(f"✅ Verified & Archived: {name}")
            # Cloudinary එකෙන් හදපු thumbnail එක පෙන්වීම
            st.image(res['secure_url'], caption=f"ID: {res['public_id']}", use_container_width=True)

elif menu == "🔍 Security Logs":
    st.header("Intelligence Database")
    try:
        import cloudinary.api
        resources = cloudinary.api.resources(type="upload", prefix="bioshield_v5", context=True)
        
        cols = st.columns(3)
        for i, item in enumerate(resources.get('resources', [])):
            with cols[i % 3]:
                # පින්තූරය පෙන්වන කොට මූණ විතරක් Zoom කරලා (Face Crop) පෙන්වනවා
                face_url = item['secure_url'].replace("/upload/", "/upload/w_300,h_300,c_thumb,g_face,r_max/")
                st.image(face_url)
                info = item.get('context', {}).get('custom', {})
                st.write(f"👤 {info.get('name')}")
                st.caption(f"📅 {info.get('time')}")
    except:
        st.info("No records found in the secure vault.")

