import streamlit as st
import telebot
import threading
import time
import urllib.parse

# --- CONFIG ---
TOKEN = "7747068384:AAEcjBAH-4vVMEzJtmKeozOZjR7J3vOGvBo"
bot = telebot.TeleBot(TOKEN)

st.set_page_config(page_title="OMNI-LEAK COMMAND", page_icon="💀")
st.title("🛰️ OMNI-LEAK: God Level OSINT Framework")
st.markdown("---")

# --- PRO HACKER LOGIC ---

@bot.message_handler(commands=['leak'])
def omni_leak(message):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "❌ භාවිතය: /leak [Phone_Number]\nEx: /leak 94771402910")
        return
    
    num = args[1].replace('+', '').replace(' ', '')
    bot.send_message(message.chat.id, f"💀 **Initiating Full System Scan for: {num}**...")
    time.sleep(1)

    # 1. WhatsApp Intel
    wa_link = f"https://api.whatsapp.com/send?phone={num}"
    wa_check = f"https://checkchat.online/check-whatsapp-online-status/{num}"

    # 2. Google Dorking (Advanced)
    dork_docs = urllib.parse.quote(f'"{num}" OR "{num.replace("947", "07")}" filetype:pdf OR filetype:xlsx')
    dork_social = urllib.parse.quote(f'site:facebook.com OR site:instagram.com OR site:twitter.com "{num}"')

    # 3. Social Registry
    true_url = f"https://www.truecaller.com/search/lk/{num}"
    
    report = f"""
🚨 **OMNI-LEAK INTEL REPORT** 🚨
━━━━━━━━━━━━━━━━━━━━
📱 **Target Number:** {num}

✅ **WhatsApp Intelligence:**
- Direct Profile: {wa_link}
- Status Tracker: {wa_check}
*(සසිනිගේ Photo එක සහ Last Seen එක මේකෙන් බලන්න)*

🔍 **Deep Web & Documents:**
- [PDF/Excel Sheets Leak] - https://www.google.com/search?q={dork_docs}
*(ක්ලාස් ලිස්ට් වල නම්බර් එක තිබුණොත් මෙතන අහුවෙනවා)*

🌐 **Social Media Footprint:**
- [Social Deep Trace] - https://www.google.com/search?q={dork_social}

📞 **Caller Identity:**
- Truecaller Web: {true_url}
━━━━━━━━━━━━━━━━━━━━
⚠️ **PRO TIP:** නම්බර් එක සේව් නොකර ටෙලිග්‍රාම් එකේ **"Add Contact"** ගිහින් බලන්න එයාගේ නම වැටෙනවද කියලා.
    """
    bot.send_message(message.chat.id, report)

@bot.message_handler(commands=['god_send'])
def god_send(message):
    # RapidAPI එක හරහා මැසේජ් යවන ලොජික් එක කලින් වගේමයි
    bot.reply_to(message, "⚙️ God Send Mode Active. API Keys තවම configure වී නැත.")

# --- UI & RUNNER ---
st.info("System is monitoring Telegram commands...")
if st.button("Clear Logs"):
    st.write("Logs cleared.")

def run_bot():
    while True:
        try: bot.polling(none_stop=True)
        except: time.sleep(10)

if 'bot_started' not in st.session_state:
    st.session_state.bot_started = True
    threading.Thread(target=run_bot, daemon=True).start()
    st.success("🛰️ Satellite Link Established!")
