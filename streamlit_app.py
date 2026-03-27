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

# Global variable එකක් ඕනේ frame එක share කරගන්න
if 'latest_frame' not in st.session_state:
    st.session_state.latest_frame = None

# --- 🤖 TELEGRAM BOT HANDLER ---
@bot.message_handler(commands=['capture'])
def send_frame(message):
    if st.session_state.latest_frame is not None:
        # OpenCV BGR frame එක RGB වලට හරවලා Image එකක් කරනවා
        img_rgb = cv2.cvtColor(st.session_state.latest_frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        
        # Buffer එකකට දාලා Telegram එකට යවනවා
        bio = io.BytesIO()
        img_pil.save(bio, format='PNG')
        bio.seek(0)
        bot.send_photo(message.chat.id, bio, caption="🎯 Current Evolution Frame Captured!")
    else:
        bot.reply_to(message, "⚠️ Streamlit එකේ Visualizer එක තාම Active නැහැ!")

# Bot එක වෙනම Thread එකක රන් කරනවා
def run_bot():
    bot.polling(none_stop=True)

if 'bot_thread' not in st.session_state:
    threading.Thread(target=run_bot, daemon=True).start()
    st.session_state.bot_thread = True

# --- 🌐 STREAMLIT INTERFACE ---
st.set_page_config(page_title="Mathematical Evolution", layout="wide")
st.title("🛰️ LIVE MATHEMATICAL EVOLUTION (GOD MODE)")

# Sidebar Settings
st.sidebar.header("Evolution Controls")
speed = st.sidebar.slider("Evolution Speed", 0.5, 5.0, 1.5)
intensity = st.sidebar.slider("Ripple Intensity", 0.1, 1.0, 0.3)

# Video Placeholder
frame_placeholder = st.empty()

# --- 🧬 MATH EVOLUTION ENGINE ---
width, height = 640, 480
x = np.linspace(-10, 10, width, dtype=np.float32)
y = np.linspace(-10, 10, height, dtype=np.float32)
X, Y = np.meshgrid(x, y)
vals = np.array([10, 20, 30, 40, 50, 60, 70, 80, 90, 100], dtype=np.float32)

start_time = time.time()

# ලයිව් loop එක
while True:
    t = (time.time() - start_time) * speed
    Z = np.zeros((height, width), dtype=np.float32)
    
    # සංකීර්ණ Interference ලොජික් එක
    for i in range(4):
        s_val1 = vals[i % len(vals)] / 30.0
        s_val2 = vals[(i + 3) % len(vals)] / 40.0
        Z += np.sin(s_val1 * X + t) * np.cos(s_val2 * Y - t)
    
    # ⚡ උඹ ඉල්ලපු Circular Ripple Effect එක (Intensity slider එකත් එක්ක)
    R = np.sqrt(X**2 + Y**2)
    Z += np.sin(R * 5.0 - t * 4.0) * intensity

    # Normalization & Coloring
    Z_norm = cv2.normalize(Z, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
    img_color = cv2.applyColorMap(Z_norm, cv2.COLORMAP_INFERNO)
    
    # FPS පෙන්වීම
    cv2.putText(img_color, f"EVOLVING... t={t:.1f}", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # Frame එක Session State එකට දානවා Bot එකට පේන්න
    st.session_state.latest_frame = img_color

    # Streamlit එකේ පෙන්වීම (RGB වලට හරවලා)
    frame_placeholder.image(img_color, channels="BGR", use_container_width=True)
    
    # පොඩි delay එකක් දානවා streamlit එක හිර නොවී ඉන්න
    time.sleep(0.01)
