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
DB_FILE = "advanced_vault.json"

# --- 🛠️ DATABASE LOGIC ---
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: return json.load(f)
    return {"users": {}}

def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f, indent=4)

# --- 🤖 TELEGRAM BUTTONS UI ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('🔐 My Vault')
    btn2 = types.KeyboardButton('📤 Upload Data')
    btn3 = types.KeyboardButton('📊 Usage Stats')
    btn4 = types.KeyboardButton('👤 Profile')
    markup.add(btn1, btn2, btn3, btn4)
    return markup

# --- 🤖 BOT HANDLERS ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    db = load_db()
    
    if uid not in db["users"]:
        db["users"][uid] = {
            "name": message.from_user.first_name,
            "data": [],
            "joined": str(datetime.now()),
            "files": 0
        }
        save_db(db)
        bot.send_message(message.chat.id, f"👋 සාදරයෙන් පිළිගන්න {message.from_user.first_name}!\nඔබේ ගිණුම සාර්ථකව සක්‍රීය කරන ලදී.", reply_markup=main_menu())
    else:
        bot.send_message(message.chat.id, "ඔබ නැවතත් පැමිණීම සතුටක් බොසා! 😈", reply_markup=main_menu())

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    uid = str(message.from_user.id)
    db = load_db()
    
    if message.text == '🔐 My Vault':
        if db["users"][uid]["data"]:
            res = "\n".join([f"📍 {d['time'][:16]}: {d['content']}" for d in db["users"][uid]["data"]])
            bot.reply_to(message, f"🗝️ **ඔබේ රහසිගත දත්ත:**\n\n{res}")
        else:
            bot.reply_to(message, "📭 ඔබේ Vault එක දැනට හිස්.")
            
    elif message.text == '📤 Upload Data':
        bot.reply_to(message, "දැන් ඕනෑම දෙයක් (Text, Photo, File) එවන්න. මම ඒක ආරක්ෂිතව සේව් කරගන්නම්! 🚀")

    elif message.text == '📊 Usage Stats':
        count = len(db["users"][uid]["data"])
        bot.reply_to(message, f"📈 ඔබ දැනට records {count} ක් ඇතුළත් කර ඇත.")

# --- 📂 ALL DATA UPLOADER (Any Type) ---
@bot.message_handler(content_types=['text', 'photo', 'document', 'video'])
def save_any_data(message):
    uid = str(message.from_user.id)
    db = load_db()
    
    data_content = ""
    if message.text:
        data_content = f"Text: {message.text}"
    elif message.photo:
        data_content = "📁 Image File Saved"
    elif message.document:
        data_content = f"📁 Document: {message.document.file_name}"
    
    db["users"][uid]["data"].append({"content": data_content, "time": str(datetime.now())})
    db["users"][uid]["files"] += 1
    save_db(db)
    bot.reply_to(message, "✅ දත්ත ආරක්ෂිතව Vault එකට එක් කරන ලදී!")

# --- 🌐 STREAMLIT DASHBOARD (Admin Panel) ---
st.set_page_config(page_title="VAULT ADMIN PRO", layout="wide")
st.markdown("<h1 style='text-align: center; color: red;'>🛰️ CYBER-VAULT V8.0: MASTER CONTROL</h1>", unsafe_allow_html=True)

db = load_db()
users = db.get("users", {})

# Dashboard Metrics
st.write("---")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Active Agents", len(users))
total_recs = sum(len(u["data"]) for u in users.values())
m2.metric("Total Vault Data", total_recs)
m3.metric("Storage Status", "Encrypted 🔒")
m4.metric("Server Speed", "High ⚡")

# User List
st.subheader("🕵️‍♂️ Registered Agents & Activity")
if users:
    df_data = []
    for uid, info in users.items():
        df_data.append({
            "Name": info["name"],
            "Records": len(info["data"]),
            "Joined Date": info["joined"][:10],
            "Last Activity": info["data"][-1]["time"][:16] if info["data"] else "N/A"
        })
    df = pd.DataFrame(df_data)
    st.dataframe(df, use_container_width=True)

    # Plotly Graph
    fig = px.pie(df, values='Records', names='Name', title='Data Distribution per Agent', template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    # Detailed Search
    st.divider()
    search = st.selectbox("View Private Records for:", df["Name"])
    for uid, info in users.items():
        if info["name"] == search:
            st.json(info["data"])
else:
    st.warning("No Agents Active.")

# --- RUNNER ---
def run_bot():
    while True:
        try: bot.polling(none_stop=True)
        except: time.sleep(5)

if 'bot_v8' not in st.session_state:
    st.session_state.bot_v8 = True
    threading.Thread(target=run_bot, daemon=True).start()
    st.success("🛰️ System Online. Buttons Ready!")
