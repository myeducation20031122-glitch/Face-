import streamlit as st
import telebot
import threading
import time

# ඔයාගේ Token එක
TOKEN = "7747068384:AAEcjBAH-4vVMEzJtmKeozOZjR7J3vOGvBo"
bot = telebot.TeleBot(TOKEN)

st.title("🚀 Telegram Bot Server")
st.write("Bot එක දැනට ක්‍රියාත්මකයි...")

# Bot එකේ වැඩ කෑලි මෙතනින් පල්ලෙහාට ලියන්න
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "අඩෝ බොසා! මම දැන් Streamlit එකේ ඉඳන් වැඩ! 🔥")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"ඔයා කිව්වේ: {message.text}")

# Bot එක පණගන්වන Function එක
def run_bot():
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            time.sleep(15)

# Streamlit එකේ Session එක පාවිච්චි කරලා thread එක එක පාරක් විතරක් start කරනවා
if 'bot_started' not in st.session_state:
    st.session_state.bot_started = True
    thread = threading.Thread(target=run_bot)
    thread.start()
    st.success("Bot thread started successfully!")

st.info("මෙම පිටුව විවෘතව තැබීම අවශ්‍ය නැත, නමුත් සතියකට වරක්වත් මෙතනට පැමිණෙන්න.")
