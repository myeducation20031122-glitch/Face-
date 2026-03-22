import streamlit as st
import telebot
import threading
import time
import urllib.parse

# --- CONFIG ---
TOKEN = "7747068384:AAEcjBAH-4vVMEzJtmKeozOZjR7J3vOGvBo"
bot = telebot.TeleBot(TOKEN)

# --- UI HACKER THEME ---
st.set_page_config(page_title="CYBER-STALKER V4.0", page_icon="💀", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #00ff00; font-family: 'Courier New', Courier, monospace; }
    stButton>button { background-color: #ff0000; color: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("💀 CYBER-STALKER V4.0 : GOD MODE")
st.write("--- SYSTEM ONLINE | ENCRYPTION: AES-256 ---")

# --- CORE LOGIC ---

@bot.message_handler(commands=['start'])
def welcome(message):
    help_text = """
🔥 **CYBER-STALKER COMMAND LIST** 🔥
━━━━━━━━━━━━━━━━━━━━
📍 `/leak [Number]` - Full Data Breach (Social/Web)
🎯 `/trap` - Generate IP Logger Link (Location Grabber)
💬 `/wa [Number]` - Direct WhatsApp Tunnel (Stealth)
🕵️‍♂️ `/stalk [Name]` - Full Social Media Trace
📄 `/docs [Number]` - Search Leaked Documents (PDF/Excel)
📞 `/identity [Number]` - Truecaller & Global Registry
💀 `/god_mode` - System Status & API Info
━━━━━━━━━━━━━━━━━━━━
    """
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['leak'])
def full_leak(message):
    args = message.text.split()
    if len(args) < 2: return bot.reply_to(message, "❌ Number එක දීපන් පකෝ!")
    
    num = args[1].replace('+', '').replace(' ', '')
    bot.send_message(message.chat.id, "🛰️ Satellite Link Established... Scanning Deep Web...")
    
    # Advanced Dorking Strings
    d1 = urllib.parse.quote(f'"{num}" OR "{num.replace("947", "07")}" filetype:pdf OR filetype:xlsx')
    d2 = urllib.parse.quote(f'site:facebook.com OR site:instagram.com OR site:tiktok.com "{num}"')
    
    report = f"""
🚨 **FULL INTEL REPORT: {num}** 🚨
━━━━━━━━━━━━━━━━━━━━
📱 **WhatsApp Tunnel:** https://wa.me/{num}
📍 **Live Tracker:** https://grabify.link/ (මෙතනින් ලින්ක් එකක් හදලා සසිනිට යවන්න)
📂 **Leaked Docs:** https://www.google.com/search?q={d1}
🌐 **Social Trace:** https://www.google.com/search?q={d2}
📞 **Registry:** https://www.truecaller.com/search/lk/{num}
━━━━━━━━━━━━━━━━━━━━
"""
    bot.send_message(message.chat.id, report)

@bot.message_handler(commands=['trap'])
def ip_trap(message):
    bot.reply_to(message, "ල **IP TRAP GENERATOR**\n\n1. [Grabify](https://grabify.link/) එකට යන්න.\n2. ඕනෑම ලින්ක් එකක් (උදා: Youtube Video එකක්) දීලා ලින්ක් එකක් හදාගන්න.\n3. ඒ ලින්ක් එක සසිනිට යවන්න.\n4. එයා ඒක Click කරපු ගමන් එයාගේ Location එක Grabify dashboard එකේ වැටෙයි!")

# --- STREAMLIT MONITOR ---
col1, col2 = st.columns(2)
with col1:
    st.subheader("📡 Connection Status")
    st.success("Bot is Listening on Telegram...")
    if st.button("FORCE REBOOT SYSTEM"):
        st.warning("Rebooting...")

with col2:
    st.subheader("💀 Target Activity")
    st.info("Currently Monitoring Target: Sasini (25244975)")

def run_bot():
    while True:
        try: bot.polling(none_stop=True)
        except: time.sleep(10)

if 'bot_started' not in st.session_state:
    st.session_state.bot_started = True
    threading.Thread(target=run_bot, daemon=True).start()
