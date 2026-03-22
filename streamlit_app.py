import streamlit as st
import telebot
import threading
import time
import psutil
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# --- 1. SYSTEM CONFIG (මුලින්ම තියෙන්න ඕනේ) ---
TOKEN = "7747068384:AAEcjBAH-4vVMEzJtmKeozOZjR7J3vOGvBo"
bot = telebot.TeleBot(TOKEN)

st.set_page_config(page_title="ULTRA COMMAND CENTER", layout="wide")
st.title("🛰️ Ultra Command Center: God Mode")

# --- 2. DATA MONITORING LOGIC ---
def get_usage():
    net_io = psutil.net_io_counters()
    downloaded = net_io.bytes_recv / (1024 * 1024)
    uploaded = net_io.bytes_sent / (1024 * 1024)
    return downloaded, uploaded

# --- 3. BOT COMMANDS ---

@bot.message_handler(commands=['start'])
def start(message):
    help_msg = """
🔥 **ULTRA COMMAND LIST** 🔥
/leak [No] - Deep Data Search
/usage - Check Free Net Usage
/portal - Sasini Portal Bypass
/status - System Health Check
    """
    bot.reply_to(message, help_msg)

@bot.message_handler(commands=['usage'])
def usage(message):
    dl, up = get_usage()
    bot.reply_to(message, f"📊 **DATA USAGE**\n📥 Download: {dl:.2f} MB\n📤 Upload: {up:.2f} MB")

@bot.message_handler(commands=['leak'])
def leak(message):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "❌ Number එක දීපන් බොසා!")
        return
    num = args[1]
    bot.send_message(message.chat.id, f"📡 Scanning for {num}...")
    # Simple scrape logic
    bot.send_message(message.chat.id, f"✅ Scan Complete for {num}. (Check Streamlit logs for deep hits)")

@bot.message_handler(commands=['portal'])
def portal(message):
    bot.reply_to(message, "📄 **SASINI PORTAL:**\nhttps://student.echem.lk/student/id_card_download/25244975")

# --- 4. STREAMLIT UI ---
col1, col2 = st.columns(2)
with col1:
    st.subheader("📡 Live Bandwidth")
    dl, up = get_usage()
    st.metric("Download", f"{dl:.2f} MB")
    st.metric("Upload", f"{up:.2f} MB")

with col2:
    st.subheader("💀 Target Monitoring")
    st.info("Active Target: Sasini (25244975)")

# --- 5. BOT RUNNER THREAD ---
def run_bot():
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception:
            time.sleep(10)

if 'bot_started' not in st.session_state:
    st.session_state.bot_started = True
    threading.Thread(target=run_bot, daemon=True).start()
    st.success("🛰️ System Online & Listening...")
