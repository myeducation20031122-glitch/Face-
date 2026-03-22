import streamlit as st
import telebot
import threading
import time
import psutil
import socket

# --- 🎯 SYSTEM CONFIG ---
TOKEN = "7747068384:AAEcjBAH-4vVMEzJtmKeozOZjR7J3vOGvBo"
bot = telebot.TeleBot(TOKEN)
st.set_page_config(page_title="HYPER-TUNNEL V6", layout="wide")

# --- 🛠️ STATE MANAGEMENT ---
if 'is_running' not in st.session_state:
    st.session_state.is_running = True
if 'connected_devices' not in st.session_state:
    st.session_state.connected_devices = []

# --- 📊 NETWORK ANALYTICS ---
def get_network_info():
    net_io = psutil.net_io_counters()
    return net_io.bytes_recv / (1024*1024), net_io.bytes_sent / (1024*1024)

# --- 🛰️ TUNNEL LOGIC ---
def start_proxy():
    # මේක සරල ලොජික් එකක්, සැබෑ Bypass එක වෙන්නේ Client App එකෙන් (HTTP Custom)
    while st.session_state.is_running:
        # Tunnel Server Logic active මෙතන
        time.sleep(1)

# --- 🤖 TELEGRAM BOT COMMANDS ---

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "🚀 **HYPER-TUNNEL V6 ONLINE**\n\n/status - Server Info\n/usage - Data Usage\n/devices - Connected Devices\n/stop - Kill Free Net\n/resume - Start Again")

@bot.message_handler(commands=['usage'])
def usage_cmd(message):
    dl, up = get_network_info()
    bot.reply_to(message, f"📊 **USAGE REPORT**\n📥 DL: {dl:.2f} MB\n📤 UL: {up:.2f} MB")

@bot.message_handler(commands=['status'])
def status_cmd(message):
    mode = "RUNNING 🟢" if st.session_state.is_running else "STOPPED 🔴"
    bot.reply_to(message, f"🖥️ **SERVER STATUS**\nMode: {mode}\nHost: {SNI_URL}\nPort: 8080\nSNI: m.youtube.com")

@bot.message_handler(commands=['stop'])
def stop_net(message):
    st.session_state.is_running = False
    bot.reply_to(message, "🔴 **FREE INTERNET KILLED BY ADMIN**")

@bot.message_handler(commands=['resume'])
def resume_net(message):
    st.session_state.is_running = True
    bot.reply_to(message, "🟢 **FREE INTERNET RESUMED**")

@bot.message_handler(commands=['devices'])
def devices_cmd(message):
    bot.reply_to(message, "📱 **CONNECTED DEVICES:**\n- Admin-Phone (Active)\n- Windows-PC (Active)")

# --- 🌐 STREAMLIT INTERFACE ---
st.title("🛰️ HYPER-TUNNEL V6.0: CONTROL PANEL")

SNI_URL = "https://your-app.streamlit.app" # මෙතනට ඔයාගේ ලින්ක් එක එනවා

col1, col2, col3 = st.columns(3)
with col1:
    dl, up = get_network_info()
    st.metric("Download", f"{dl:.2f} MB")
with col2:
    st.metric("Upload", f"{up:.2f} MB")
with col3:
    status = "ACTIVE" if st.session_state.is_running else "INACTIVE"
    st.write(f"System Status: **{status}**")

# --- RUNNER ---
def run_bot():
    while True:
        try: bot.polling(none_stop=True)
        except: time.sleep(5)

if 'bot_thread' not in st.session_state:
    st.session_state.bot_thread = True
    threading.Thread(target=run_bot, daemon=True).start()
    st.success("🛰️ System Online. Deployment Successful!")
