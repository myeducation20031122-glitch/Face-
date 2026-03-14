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

st.set_page_config(page_title="BIO-SHIELD LITE")
st.title("🛡️ BIO-SHIELD v3.0 (No-CV2)")

menu = st.sidebar.selectbox("Menu", ["👤 Register", "🔍 Logs"])

if menu == "👤 Register":
    name = st.text_input("Name:")
    img_file = st.camera_input("Take Photo")
    
    if img_file and name:
        # OpenCV වෙනුවට PIL පාවිච්චි කිරීම
        image = Image.open(img_file)
        
        # පින්තූරය Bytes වලට හරවා ගැනීම
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()
        
        with st.spinner("Uploading..."):
            res = cloudinary.uploader.upload(
                img_byte_arr,
                folder="bioshield_v3",
                context={"name": name, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            )
            st.success(f"Saved: {name}")
            st.image(image, width=300)

elif menu == "🔍 Logs":
    st.header("Cloud Logs")
    # Cloudinary එකෙන් පින්තූර පෙන්වීම
    try:
        import cloudinary.api
        results = cloudinary.api.resources(type="upload", prefix="bioshield_v3")
        for res in results.get('resources', []):
            st.image(res['secure_url'], width=200)
    except:
        st.write("No logs yet.")
