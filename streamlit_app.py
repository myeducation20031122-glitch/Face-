import streamlit as st
import asyncio
import os
import pikepdf
import threading
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# --- 🛠️ CONFIGURATION ---
# Streamlit Secrets වල 'BOT_TOKEN' කියලා සේව් කරන්න. නැත්නම් පහත එක පාවිච්චි කරන්න.
TOKEN = st.secrets.get("BOT_TOKEN", "3BZ7nhK5kROMEE1if5v95L2lb4E_2cswxn1jbVTnuATksZiY9")

st.set_page_config(page_title="Victims Bot Pro", page_icon="🕵️‍♂️")
st.title("🕵️‍♂️ Victims Bot - Pro Control Panel")

# User States මතක තියාගන්න
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}

# --- 🤖 BOT CORE LOGIC ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("📤 Upload PDF", callback_data='help')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👋 Victims Bot සක්‍රීයයි! මට PDF එකක් එවන්න බොසා.", reply_markup=reply_markup)

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    doc = update.message.document
    
    if not doc.file_name.lower().endswith('.pdf'):
        await update.message.reply_text("❌ PDF එකක් විතරක් එවන්න.")
        return

    status = await update.message.reply_text("📥 ගොනුව බාගත කරමින්...")
    file = await context.bot.get_file(doc.file_id)
    path = f"file_{user_id}_{int(time.time())}.pdf"
    await file.download_to_drive(path)

    st.session_state.user_data[user_id] = {"path": path, "name": doc.file_name, "state": None}
    
    keyboard = [
        [InlineKeyboardButton("🔑 I Know Password", callback_data='know_pwd')],
        [InlineKeyboardButton("📊 Password Range", callback_data='know_range')],
        [InlineKeyboardButton("🤷 I Don't Know Anything", callback_data='know_nothing')]
    ]
    await status.edit_text(f"📄 {doc.file_name} ලැබුණා.\nදැන් මොකක්ද කරන්න ඕනේ?", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if user_id not in st.session_state.user_data:
        await query.edit_message_text("⚠️ පරණ session එකක්. කරුණාකර නැවත PDF එක එවන්න.")
        return

    data = query.data
    if data == 'know_pwd':
        st.session_state.user_data[user_id]['state'] = 'WAIT_PWD'
        await query.edit_message_text("⌨️ Password එක එවන්න:")
    elif data == 'know_range':
        st.session_state.user_data[user_id]['state'] = 'WAIT_RANGE'
        await query.edit_message_text("📏 පරාසය එවන්න (උදා: 25000000-26000000):")
    elif data == 'know_nothing':
        keyboard = [
            [InlineKeyboardButton("🔢 Numbers", callback_data='brute_num')],
            [InlineKeyboardButton("🔠 Letters", callback_data='brute_let')],
            [InlineKeyboardButton("🔀 Mixed", callback_data='brute_mix')]
        ]
        await query.edit_message_text("මොන වගේ Brute Force එකක්ද ඕනේ?", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == 'brute_num':
        # Default range එකකට auto පටන් ගන්නවා
        await start_brute(query, context, user_id, 25880000, 25889000)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in st.session_state.user_data: return
    
    state = st.session_state.user_data[user_id].get('state')
    text = update.message.text
    path = st.session_state.user_data[user_id]['path']

    if state == 'WAIT_PWD':
        try:
            with pikepdf.open(path, password=text) as pdf:
                out = f"dec_{user_id}.pdf"
                pdf.save(out)
                await update.message.reply_document(document=open(out, 'rb'), caption="🔓 Unlocked!")
                os.remove(out)
        except:
            await update.message.reply_text("❌ වැරදි පාස්වර්ඩ් එකක්!")

    elif state == 'WAIT_RANGE':
        if '-' in text:
            try:
                s, e = map(int, text.split('-'))
                await start_brute(update, context, user_id, s, e)
            except:
                await update.message.reply_text("❌ වැරදි පරාසයක්.")

async def start_brute(event, context, user_id, start_r, end_r):
    data = st.session_state.user_data[user_id]
    path = data['path']
    found = False
    
    # Progress update එක පාලනය කරන්න
    prog_msg = await context.bot.send_message(chat_id=user_id, text="🚀 ආරම්භ කළා...")
    last_update_time = time.time()

    try:
        for pwd in range(start_r, end_r + 1):
            pwd_str = str(pwd)
            
            # තත්පර 3කට වරක් පමණක් progress එක පෙන්වයි (Rate limit safe)
            if time.time() - last_update_time > 3:
                await context.bot.edit_message_text(chat_id=user_id, message_id=prog_msg.message_id, text=f"🔍 පරීක්ෂා කරමින්: `{pwd_str}`")
                last_update_time = time.time()

            try:
                with pikepdf.open(path, password=pwd_str) as pdf:
                    out = f"unlocked_{user_id}.pdf"
                    pdf.save(out)
                    await context.bot.send_document(chat_id=user_id, document=open(out, 'rb'), caption=f"✅ හමු වුණා!\n🔑 Password: `{pwd_str}`")
                    os.remove(out)
                    found = True
                    break
            except pikepdf.PasswordError:
                continue
        
        if not found:
            await context.bot.send_message(chat_id=user_id, text="❌ ලබාදුන් පරාසය තුළ Password එක හමු වුණේ නැත.")
    finally:
        # සැමවිටම temp file එක අයින් කරයි
        if os.path.exists(path): os.remove(path)
        st.session_state.user_data.pop(user_id, None)

# --- 🚀 RUNNER ---
def run_bot_forever():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.PDF, handle_document))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()

if "bot_thread" not in st.session_state:
    st.info("🚀 Bot Server එක පණගන්වමින්...")
    thread = threading.Thread(target=run_bot_forever, daemon=True)
    thread.start()
    st.session_state.bot_thread = True

st.success("✅ Bot එක දැන් සක්‍රීයයි. Telegram එකට ගිහින් පාවිච්චි කරන්න.")
