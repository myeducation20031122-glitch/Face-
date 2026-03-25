import streamlit as st
import telebot
from telebot import types
import json
import os
import pandas as pd
import plotly.express as px
from datetime import datetime
import threading
import time

# --- 🎯 CONFIG ---
TOKEN = "7747068384:AAEcjBAH-4vVMEzJtmKeozOZjR7J3vOGvBo"
bot = telebot.TeleBot(TOKEN)
DB_FILE = "final_vault_v10.json"

# --- 🛠️ DATABASE LOGIC ---
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: return json.load(f)
    return {"users": {}, "usernames": []}

def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f, indent=4)

# --- ⌨️ KEYBOARDS ---
def guest_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('📝 Register', '🔑 Login')
    return markup

def member_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('🔐 My Vault', '📤 Upload Data', '🗑️ Delete Data', '🚪 Logout')
    return markup

# --- 🤖 BOT LOGIC ---
user_state = {} # Temporary state handling

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🛰️ **CYBER-VAULT V10 ONLINE**\nAccess Restricted.", reply_markup=guest_menu())

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    uid = str(message.from_user.id)
    db = load_db()

    if message.text == '📝 Register':
        msg = bot.send_message(message.chat.id, "ඔබේ අද්විතීය නම (Username) ඇතුළත් කරන්න:")
        bot.register_next_step_handler(msg, process_username)

    elif message.text == '🔑 Login':
        if uid in db["users"]:
            msg = bot.send_message(message.chat.id, "ඔබේ රහස් පදය (Password) ඇතුළත් කරන්න:")
            bot.register_next_step_handler(msg, process_login)
        else:
            bot.send_message(message.chat.id, "❌ ඔබට ගිණුමක් නැත. කරුණාකර Register වන්න.")

    elif uid in db["users"] and db["users"][uid].get("is_logged_in", False):
        if message.text == '🔐 My Vault':
            data = db["users"][uid]["data"]
            res = "\n".join([f"🆔 {i}: {d['content']}" for i, d in enumerate(data)]) if data else "හිස්."
            bot.send_message(message.chat.id, f"🗝️ **YOUR DATA:**\n{res}")
        
        elif message.text == '📤 Upload Data':
            msg = bot.send_message(message.chat.id, "එවන්න ඕනෑම දෙයක්...")
            bot.register_next_step_handler(msg, process_upload)

        elif message.text == '🗑️ Delete Data':
            msg = bot.send_message(message.chat.id, "මකන්න ඕනේ Data එකේ ID එක (අංකය) එවන්න:")
            bot.register_next_step_handler(msg, process_delete)

        elif message.text == '🚪 Logout':
            db["users"][uid]["is_logged_in"] = False
            save_db(db)
            bot.send_message(message.chat.id, "Logout සාර්ථකයි. 🔒", reply_markup=guest_menu())

# --- REGISTER / LOGIN FLOW ---
def process_username(message):
    db = load_db()
    name = message.text.strip().lower()
    if name in db["usernames"]:
        msg = bot.send_message(message.chat.id, "❌ මේ නම දැනටමත් අරන්. වෙනත් නමක් එවන්න:")
        bot.register_next_step_handler(msg, process_username)
    else:
        user_state[message.from_user.id] = {"name": name}
        msg = bot.send_message(message.chat.id, f"නියමයි {name}! දැන් රහස් පදයක් (Password) එවන්න:")
        bot.register_next_step_handler(msg, process_password)

def process_password(message):
    uid = str(message.from_user.id)
    db = load_db()
    name = user_state[uid]["name"]
    pwd = message.text
    db["users"][uid] = {"name": name, "pwd": pwd, "data": [], "joined": str(datetime.now()), "is_logged_in": True}
    db["usernames"].append(name)
    save_db(db)
    bot.send_message(message.chat.id, "✅ ලියාපදිංචිය සාර්ථකයි! ඔබ දැන් ඇතුළු වී ඇත.", reply_markup=member_menu())

def process_login(message):
    uid = str(message.from_user.id)
    db = load_db()
    if message.text == db["users"][uid]["pwd"]:
        db["users"][uid]["is_logged_in"] = True
        save_db(db)
        bot.send_message(message.chat.id, "✅ Access Granted!", reply_markup=member_menu())
    else:
        bot.send_message(message.chat.id, "❌ වැරදි Password එකක්. නැවත උත්සාහ කරන්න.", reply_markup=guest_menu())

# --- ACTION FLOWS ---
def process_upload(message):
    uid = str(message.from_user.id)
    db = load_db()
    content = message.text if message.text else "📁 File/Media Saved"
    db["users"][uid]["data"].append({"content": content, "time": str(datetime.now())})
    save_db(db)
    bot.reply_to(message, "✅ Vault එකට දැම්මා!")

def process_delete(message):
    uid = str(message.from_user.id)
    db = load_db()
    try:
        idx = int(message.text)
        del db["users"][uid]["data"][idx]
        save_db(db)
        bot.send_message(message.chat.id, "🗑️ දත්තය සාර්ථකව මකා දැමුවා!")
    except:
        bot.send_message(message.chat.id, "❌ වැරදි අංකයක්.")

# --- 🌐 STREAMLIT ADMIN ---
st.title("🛰️ MASTER CONTROL: VAULT V10")
db = load_db()
users = db.get("users", {})

c1, c2 = st.columns(2)
c1.metric("Total Agents", len(users))
c2.metric("System Health", "Optimal 🟢")

if users:
    df = pd.DataFrame([{"Name": u["name"], "Records": len(u["data"]), "Joined": u["joined"][:10]} for u in users.values()])
    st.table(df)
    st.plotly_chart(px.bar(df, x="Name", y="Records", template="plotly_dark"))

# --- RUNNER ---
def run_bot():
    while True:
        try: bot.polling(none_stop=True)
        except: time.sleep(5)

if 'bot_v10' not in st.session_state:
    st.session_state.bot_v10 = True
    threading.Thread(target=run_bot, daemon=True).start()
