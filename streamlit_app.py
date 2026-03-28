import streamlit as st
import asyncio
import os
import pikepdf
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# --- 🛠️ CONFIGURATION ---
TOKEN = "7747068384:AAEcjBAH-4vVMEzJtmKeozOZjR7J3vOGvBo"

st.set_page_config(page_title="Victims Bot Control", page_icon="⚡")
st.title("⚡ Victims Bot V2.0 - Active")
st.caption("Auto-running background process...")

# --- 🧠 BOT LOGIC & STATE ---
# User ගේ current state එක මතක තියාගන්න (Password Range එකක්ද එවන්නෙ කියලා බලන්න)
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📤 Upload PDF", callback_data='upload_info')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 හායි බොසා! මම Victims Bot.\nඔයාගේ Locked PDF එකක් එවන්න, මම ඒක ගේමක් නැතුව Unlock කරලා දෙන්නම්.",
        reply_markup=reply_markup
    )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_id = update.message.document.file_id
    file_name = update.message.document.file_name
    
    if not file_name.lower().endswith('.pdf'):
        await update.message.reply_text("❌ PDF එකක් විතරක් එවන්න බොසා!")
        return

    # PDF එක තාවකාලිකව සේව් කරමු
    file = await context.bot.get_file(file_id)
    path = f"temp_{update.effective_user.id}.pdf"
    await file.download_to_drive(path)
    
    user_data[update.effective_user.id] = {"path": path, "name": file_name}

    keyboard = [
        [InlineKeyboardButton("🔑 I Know Password", callback_data='know_pwd')],
        [InlineKeyboardButton("📊 I Know Password Range", callback_data='know_range')],
        [InlineKeyboardButton("🤷 I Don't Know Anything", callback_data='know_nothing')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"📄 ගොනුව ලැබුණා: {file_name}\nදැන් මොකද කරන්නේ?", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == 'know_pwd':
        user_data[user_id]['state'] = 'WAITING_PWD'
        await query.edit_message_text("⌨️ කරුණාකර PDF එකේ Password එක එවන්න:")

    elif query.data == 'know_range':
        user_data[user_id]['state'] = 'WAITING_RANGE'
        await query.edit_message_text("📏 පරාසය එවන්න (උදා: 25000000-26000000):")

    elif query.data == 'know_nothing':
        keyboard = [
            [InlineKeyboardButton("🔢 Numbers Only", callback_data='brute_num')],
            [InlineKeyboardButton("🔠 Letters Only", callback_data='brute_let')],
            [InlineKeyboardButton("🔀 Mixed (All)", callback_data='brute_mix')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("මොන වගේ Brute Force එකක්ද ඕනේ?", reply_markup=reply_markup)

    elif query.data == 'brute_num':
        # Default range එකකට auto brute force පටන් ගන්නවා
        await query.edit_message_text("🚀 Auto Brute Force (Numbers) ආරම්භ කළා...")
        await start_brute_force(query, context, user_id, 0, 99999999)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_data: return

    state = user_data[user_id].get('state')
    text = update.message.text

    if state == 'WAITING_PWD':
        # කෙලින්ම unlock කරලා බලනවා
        path = user_data[user_id]['path']
        try:
            with pikepdf.open(path, password=text) as pdf:
                out = f"unlocked_{user_data[user_id]['name']}"
                pdf.save(out)
                await update.message.reply_document(document=open(out, 'rb'), caption="🔓 පට්ට! මෙන්න Unlocked PDF එක.")
                os.remove(out)
        except:
            await update.message.reply_text("❌ වැරදි Password එකක්!")

    elif state == 'WAITING_RANGE':
        # Range එක අරන් brute force කරනවා
        try:
            start_r, end_r = map(int, text.split('-'))
            await update.message.reply_text(f"🚀 පරාසය {start_r} සිට {end_r} දක්වා පරීක්ෂා කරමින්...")
            await start_brute_force(update, context, user_id, start_r, end_r)
        except:
            await update.message.reply_text("❌ වැරදි format එකක්. (200-500 ලෙස එවන්න)")

async def start_brute_force(event, context, user_id, start_r, end_r):
    path = user_data[user_id]['path']
    found = None
    
    # Progress එක පෙන්නන්න message එකක්
    prog_msg = await (event.message.reply_text("⏳ Searching...") if hasattr(event, 'message') else event.edit_message_text("⏳ Searching..."))

    for pwd in range(start_r, end_r + 1):
        pwd_str = str(pwd)
        if pwd % 1000 == 0: # තත්පර ගාණකට වරක් update එකක් දාමු
             await context.bot.edit_message_text(chat_id=user_id, message_id=prog_msg.message_id, text=f"🔍 Checking: {pwd_str}")
        
        try:
            with pikepdf.open(path, password=pwd_str) as pdf:
                found = pwd_str
                out = f"unlocked_{user_data[user_id]['name']}"
                pdf.save(out)
                await context.bot.send_document(chat_id=user_id, document=open(out, 'rb'), caption=f"✅ Found! Pwd: `{pwd_str}`")
                os.remove(out)
                break
        except: continue

    if not found:
        await context.bot.send_message(chat_id=user_id, text="❌ සොයාගත නොහැකි විය.")

# --- 🚀 AUTOMATIC RUNNER ---
async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.PDF, handle_document))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    while True: await asyncio.sleep(1)

# Streamlit එක load වුණු ගමන් auto start වෙන්න මේක කරන්නේ
if "bot_started" not in st.session_state:
    st.session_state.bot_started = True
    asyncio.run(main())
