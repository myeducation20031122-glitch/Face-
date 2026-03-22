import streamlit as st
import telebot
import threading
import time
import urllib.parse

TOKEN = "7747068384:AAEcjBAH-4vVMEzJtmKeozOZjR7J3vOGvBo"
bot = telebot.TeleBot(TOKEN)

st.title("🛰️ Deep Intel Command Center (V3.0)")

@bot.message_handler(commands=['deep_search'])
def deep_search(message):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "අංකය දාපන් බොසා! (Ex: /deep_search 0771402910)")
        return
    
    num = args[1]
    formatted_num = num.replace(' ', '')
    bot.send_message(message.chat.id, "🧬 Running Deep Dorking Algorithms...")

    # Advanced Google Dorking Queries
    # 1. පද්ධති ඇතුළේ තියෙන PDF/Doc වල නම්බර් එක සෙවීම
    dork1 = f'"{formatted_num}" filetype:pdf OR filetype:xlsx OR filetype:docx'
    # 2. සෝෂල් මීඩියා ඇතුළේ Deep Search
    dork2 = f'site:facebook.com OR site:instagram.com OR site:linkedin.com "{formatted_num}"'
    # 3. Pastebin වගේ leaked දත්ත තියෙන තැන්වල සෙවීම
    dork3 = f'site:pastebin.com OR site:github.com "{formatted_num}"'

    links = f"""
🔥 **Deep Intel Results for {num}:**

📂 **Document Search (PDF/Excel):**
https://www.google.com/search?q={urllib.parse.quote(dork1)}

📱 **Social Media Deep Trace:**
https://www.google.com/search?q={urllib.parse.quote(dork2)}

💀 **Leaked Data & Dev Sites:**
https://www.google.com/search?q={urllib.parse.quote(dork3)}

🔍 **Truecaller Direct (Web Bypass):**
https://www.truecaller.com/search/lk/{formatted_num}
    """
    bot.send_message(message.chat.id, links)

# --- BOT RUNNER ---
def run_bot():
    while True:
        try: bot.polling(none_stop=True)
        except: time.sleep(10)

if 'bot_started' not in st.session_state:
    st.session_state.bot_started = True
    threading.Thread(target=run_bot, daemon=True).start()
