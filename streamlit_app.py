import streamlit as st
import telebot
import threading
import time
import pandas as pd
from datetime import datetime

# --- CONFIGURATION ---
# මෙතන bot define කරලා තියෙන්නම ඕනේ මුලින්ම
TOKEN = "7747068384:AAEcjBAH-4vVMEzJtmKeozOZjR7J3vOGvBo"
bot = telebot.TeleBot(TOKEN)

# --- SESSION STATE FOR LOGGING ---
if 'status_log' not in st.session_state:
    st.session_state.status_log = []

# --- STREAMLIT UI ---
st.set_page_config(page_title="Ultra Intel Command", page_icon="🛰️")
st.title("🛰️ Ultra Intel Command Center")
st.write("Target: Sasini Tracking System")

# --- BOT COMMANDS ---

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👋 ගැම්මක් තමයි බොසා! Intel Bot එක Online.\n\n/social_check [Number] - Social footprint බලන්න\n/log [Account] [Status] - Status record කරන්න")

@bot.message_handler(commands=['social_check'])
def social_check(message):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "අංකය දාන්න බොසා! (Ex: /social_check 94771402910)")
        return
    
    num = args[1].replace('+', '').replace(' ', '')
    bot.send_message(message.chat.id, f"🔍 Hunting Social Media for: {num}...")
    
    # Intel Links
    true_url = f"https://www.truecaller.com/search/lk/{num}"
    google_url = f"https://www.google.com/search?q=%22{num}%22"
    wa_url = f"https://wa.me/{num}"
    
    bot.send_message(message.chat.id, f"✅ Intel Found:\n\n📞 Truecaller: {true_url}\n🌍 Google: {google_url}\n💬 WhatsApp: {wa_url}")

@bot.message_handler(commands=['log'])
def log_status(message):
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        bot.reply_to(message, "භාවිතය: /log [AccountName] [Status]\n(Ex: /log Sasini_TG Online)")
        return
    
    acc = args[1]
    stat = args[2]
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Streamlit session එකට දත්ත දානවා
    st.session_state.status_log.append({"Time": now, "Account": acc, "Status": stat})
    bot.reply_to(message, f"📊 Data Logged for {acc} at {now}")

# --- DATA VIEW & DOWNLOAD ---
st.subheader("📊 Captured Intel Log")
if st.session_state.status_log:
    df = pd.DataFrame(st.session_state.status_log)
    st.table(df)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Log (CSV)", data=csv, file_name='intel_log.csv', mime='text/csv')
else:
    st.info("තාම Data මොකුත් නැහැ බොසා.")

# --- BOT THREAD ---
def run_bot():
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            time.sleep(10)

if 'bot_started' not in st.session_state:
    st.session_state.bot_started = True
    threading.Thread(target=run_bot, daemon=True).start()
    st.success("Bot Thread Launched!")
