import streamlit as st
import cv2
import numpy as np
import time
import telebot
from PIL import Image
import threading
import io

# --- 🎯 CONFIG ---
TOKEN = "7747068384:AAEcjBAH-4vVMEzJtmKeozOZjR7J3vOGvBo"
bot = telebot.TeleBot(TOKEN)

if 'latest_frame' not in st.session_state:
    st.session_state.latest_frame = None

# --- 🤖 TELEGRAM BOT (Background) ---
def run_bot():
    try:
        @bot.message_handler(commands=['capture'])
        def send_frame(message):
            if st.session_state.latest_frame is not None:
                img_rgb = cv2.cvtColor(st.session_state.latest_frame, cv2.COLOR_BGR2RGB)
                img_pil = Image.fromarray(img_rgb)
                bio = io.BytesIO()
                img_pil.save(bio, format='JPEG', quality=70) # Quality පොඩ්ඩක් අඩු කළා fast වෙන්න
                bio.seek(0)
                bot.send_photo(message.chat.id, bio, caption="🎯 Frame Captured!")
        bot.polling(none_stop=True)
    except: pass

if 'bot_thread' not in st.session_state:
    threading.Thread(target=run_bot, daemon=True).start()
    st.session_state.bot_thread = True

# --- 🌐 STREAMLIT UI ---
st.set_page_config(page_title="Smooth Math Art", layout="centered") # Layout එක centered කළොත් තවත් smooth
st.title("🛰️ SMOOTH MATHEMATICAL EVOLUTION")

# Sidebar
speed = st.sidebar.slider("Speed", 1.0, 10.0, 4.0)
res = st.sidebar.selectbox("Resolution (Higher = Slower)", [320, 480, 640], index=0) # Resolution එක අඩු කරල බැලුවම පට්ට smooth

# වීඩියෝ එක පෙන්වන තැන
frame_placeholder = st.empty()

# --- 🧬 OPTIMIZED ENGINE ---
width = res
height = int(res * 0.75)
x = np.linspace(-8, 8, width).astype(np.float32)
y = np.linspace(-8, 8, height).astype(np.float32)
X, Y = np.meshgrid(x, y)
R_sq = X**2 + Y**2
R = np.sqrt(R_sq)

start_time = time.time()

# 🚀 මේක තමයි පට්ටම Smooth විදිය
while True:
    t = (time.time() - start_time) * speed
    
    # ගණිතමය සමීකරණය (එක පේළියෙන් සුළු කරනවා Fast වෙන්න)
    Z = np.sin(1.2 * X + t) * np.cos(0.8 * Y - t)
    Z += np.sin(R * 5.0 - t * 3.0) * 0.4 # Ripple Effect
    
    # Normalization
    Z_norm = ((Z - Z.min()) / (Z.max() - Z.min()) * 255).astype(np.uint8)
    img_color = cv2.applyColorMap(Z_norm, cv2.COLORMAP_INFERNO)
    
    # Frame එක Store කරනවා Bot එකට
    st.session_state.latest_frame = img_color

    # පේජ් එක මුළුමනින්ම refresh නොකර image එක විතරක් update කරනවා
    frame_placeholder.image(img_color, channels="BGR", use_container_width=True)
    
    # ⏱️ Frame rate එක stabilize කරන්න ඉතා කුඩා delay එකක්
    time.sleep(0.001) 
