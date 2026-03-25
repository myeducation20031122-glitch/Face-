import streamlit as st
import telebot
from telebot import types
import json
import os
import pandas as pd
from datetime import datetime
import threading
import time

# --- 🎯 CONFIG ---
TOKEN = "7747068384:AAEcjBAH-4vVMEzJtmKeozOZjR7J3vOGvBo"
bot = telebot.TeleBot(TOKEN)
DB_FILE = "persistent_vault.json"

# --- 🛠️ DATABASE PERSISTENCE LOGIC ---
# App එක restart වුණත් session එක ඇතුළේ data තියාගන්න මෙන්න මේක ඕනේ
if 'global_db' not in st.session_state:
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            st.session_state.global_db = json.load(f)
    else:
        st.session_state.global_db = {"users": {}, "usernames": []}

def load_db():
    return st.session_state.global_db

def save_db(data):
    st.session_state.global_db = data
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- 🤖 BOT HANDLERS (Same logic as before but with persistent DB) ---

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🛰️ **CYBER-VAULT V11: PERSISTENT ACTIVE**", reply_markup=guest_menu())

def guest_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('📝 Register', '🔑 Login')
    return markup

def member_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('🔐 My Vault', '📤 Upload Data', '🗑️ Delete Data', '🚪 Logout')
    return markup

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    uid = str(message.from_user.id)
    db = load_db()

    if message.text == '📝 Register':
        msg = bot.send_message(message.chat.id, "නමක් (Username) එවන්න:")
        bot.register_next_step_handler(msg, process_username)
    
    elif message.text == '🔑 Login':
        if uid in db["users"]:
            msg = bot.send_message(message.chat.id, "Password එවන්න:")
            bot.register_next_step_handler(msg, process_login)
        else:
            bot.send_message(message.chat.id, "❌ Register වෙලා නැහැ!")

    # ... (අනිත් Action ලොජික් ටික කලින් වගේමයි)

def process_username(message):
    db = load_db()
    name = message.text.strip().lower()
    if name in db["usernames"]:
        msg = bot.send_message(message.chat.id, "❌ නම පාවිච්චි කරලා. වෙන එකක් එවන්න:")
        bot.register_next_step_handler(msg, process_username)
    else:
        # තාවකාලිකව data තියාගන්න session එක පාවිච්චි කරනවා
        st.session_state[f"temp_{message.from_user.id}"] = name
        msg = bot.send_message(message.chat.id, f"නියමයි {name}! Password එකක් එවන්න:")
        bot.register_next_step_handler(msg, process_password)

def process_password(message):
    uid = str(message.from_user.id)
    db = load_db()
    name = st.session_state.get(f"temp_{message.from_user.id}")
    pwd = message.text
    
    db["users"][uid] = {"name": name, "pwd": pwd, "data": [], "joined": str(datetime.now()), "is_logged_in": True}
    db["usernames"].append(name)
    save_db(db)
    bot.send_message(message.chat.id, "✅ ලියාපදිංචිය සාර්ථකයි!", reply_markup=member_menu())

def process_login(message):
    uid = str(message.from_user.id)
    db = load_db()
    if message.text == db["users"][uid]["pwd"]:
        db["users"][uid]["is_logged_in"] = True
        save_db(db)
        bot.send_message(message.chat.id, "✅ ඇතුළු විය!", reply_markup=member_menu())
    else:
        bot.send_message(message.chat.id, "❌ වැරදියි!")

# --- 🌐 STREAMLIT ADMIN ---
st.title("🛡️ VAULT V11: DATA PERSISTENCE ENABLED")
db = load_db()
st.write(f"Registered Agents: {len(db['users'])}")
st.json(db)

# --- RUNNER ---
def run_bot():
    while True:
        try: bot.polling(none_stop=True)
        except: time.sleep(5)

if 'bot_v11' not in st.session_state:
    st.session_state.bot_v11 = True
    threading.Thread(target=run_bot, daemon=True).start()
