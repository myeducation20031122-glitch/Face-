import streamlit as st
import asyncio
import os
import pikepdf
import threading
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# --- 🛠️ CONFIGURATION ---
# උඹ කිව්වා වගේ Token එක මෙතනම තියෙනවා බොසා!
TOKEN = "7747068384:AAEcjBAH-4vVMEzJtmKeozOZjR7J3vOGvBo"

st.set_page_config(page_title="Victims Bot Pro", page_icon="🕵️‍♂️")
st.title("🕵️‍♂️ Victims Bot - Pro Control Panel")
st.markdown("---")

# User States මතක තියාගන්න Session State එක පාවිච්චි කරනවා
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}

# --- 🤖 BOT CORE LOGIC ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("📤 Upload PDF", callback_data='help')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 හායි බොසා! මම Victims Bot.\nඔයාගේ Locked PDF එකක් එවන්න, මම ඒක පරීක්ෂා කරලා එවන්නම්. 🔓", 
        reply_markup=reply_markup
    )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    doc = update.message.document
    
    if not doc.file_name.lower().endswith('.pdf'):
        await update.message.reply_text("❌ PDF එකක් විතරක් එවන්න බොසා!")
        return

    status = await update.message.reply_text("📥 ගොනුව බාගත කරමින්... 🔍")
    file = await context.bot.get_file(doc.file_id)
    
    # අද්විතීය නමක් දෙනවා එකම වෙලේ කිහිප දෙනෙක් පාවිච්චි කළොත් පටලැවෙන්නේ නැති වෙන්න
    path = f"file_{user_id}_{int(time.time())}.pdf"
    await file.download_to_drive(path)

    # User ගේ විස්තර Save කරගන්නවා
    st.session_state.user_data[user_id] = {"path": path, "name": doc.file_name, "state": None}
    
    keyboard = [
        [InlineKeyboardButton("🔑 I Know Password", callback_data='know_pwd')],
        [InlineKeyboardButton("📊 Password Range", callback_data='know_range')],
        [InlineKeyboardButton("🤷 I Don't Know Anything", callback_data='know_nothing')]
    ]
    await status.edit_text(
        f"📄 ගොනුව: {doc.file_name}\nදැන් මොකක්ද කරන්න ඕනේ?", 
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if user_id not in st.session_state.user_data:
        await query.edit_message_text("⚠️ කරුණාකර නැවත PDF එක එවන්න (Session Expired).")
        return

    data = query.data
    if data == 'know_pwd':
        st.session_state.user_data[user_id]['state'] = 'WAIT_PWD'
        await query.edit_message_text("⌨️ කරුණාකර PDF එකේ Password එක එවන්න:")
        
    elif data == 'know_range':
        st.session_state.user_data[user_id]['state'] = 'WAIT_RANGE'
        await query.edit_message_text("📏 පරාසය එවන්න (උදා: 25000000-26000000):")
        
    elif data == 'know_nothing':
        keyboard = [
            [InlineKeyboardButton("🔢 Numbers Only", callback_data='brute_num')],
            [InlineKeyboardButton("🔠 Letters Only", callback_data='brute_let')],
            [InlineKeyboardButton("🔀 Mixed Mode", callback_data='brute_mix')]
        ]
        await query.edit_message_text("මොන වගේ Brute Force එකක්ද ඕනේ?", reply_markup=InlineKeyboardMarkup(keyboard))
        
    elif data == 'brute_num':
        # Default Auto Brute Force Range එක
        await start_brute(query, context, user_id, 25880000, 25889999)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in st.session_state.user_data: return
    
    state = st.session_state.user_data[user_id].get('state')
    text = update.message.text
    path = st.session_state.user_data[user_id]['path']

    if state == 'WAIT_PWD':
        try:
            with pikepdf.open(path, password=text) as pdf:
                out = f"unlocked_{user_id}.pdf"
                pdf.save(out)
                await update.message.reply_document(document=open(out, 'rb'), caption="🔓 සාර්ථකයි! මෙන්න Unlocked PDF එක.")
                os.remove(out)
        except:
            await update.message.reply_text("❌ වැරදි Password එකක්. නැවත උත්සාහ කරන්න.")

    elif state == 'WAIT_RANGE':
        if '-' in text:
            try:
                s, e = map(int, text.split('-'))
                await update.message.reply_text(f"🚀 පරාසය පරීක්ෂා කිරීම ආරම්භ කළා: {s} - {e}")
                await start_brute(update, context, user_id, s, e)
            except:
                await update.message.reply_text("❌ වැරදි Format එකක්. (උදා: 100-500)")

async def start_brute(event, context, user_id, start_r, end_r):
    data = st.session_state.user_data[user_id]
    path = data['path']
    found = False
    
    # Progress Message එක
    prog_msg = await context.bot.send_message(chat_id=user_id, text="⏳ සෙවීම ආරම්භ කළා...")
    last_update = time.time()

    try:
        for pwd in range(start_r, end_r + 1):
            pwd_str = str(pwd)
            
            # Rate limit වැළැක්වීමට තත්පර 3කට වරක් update කරයි
            if time.time() - last_update > 3:
                try:
                    await context.bot.edit_message_text(
                        chat_id=user_id, 
                        message_id=prog_msg.message_id, 
                        text=f"🔍 පරීක්ෂා කරමින්: `{pwd_str}`"
                    )
                except: pass
                last_update = time.time()

            try:
                with pikepdf.open(path, password=pwd_str) as pdf:
                    out = f"final_{user_id}.pdf"
                    pdf.save(out)
                    await context.bot.send_document(
                        chat_id=user_id, 
                        document=open(out, 'rb'), 
                        caption=f"✅ Password එක හමු වුණා!\n🔑 Password: `{pwd_str}`"
                    )
                    os.remove(out)
                    found = True
                    break
            except pikepdf.PasswordError:
                continue
        
        if not found:
            await context.bot.send_message(chat_id=user_id, text="❌ ලබාදුන් පරාසය තුළ Password එක හමු වුණේ නැත.")
            
    finally:
        # File එක අනිවාර්යයෙන්ම අයින් කරනවා
        if os.path.exists(path): os.remove(path)
        st.session_state.user_data.pop(user_id, None)

# --- 🚀 RUNNER ---
def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.PDF, handle_document))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("🚀 Bot is running...")
    app.run_polling()

# Streamlit එක load වුණු ගමන් Background එකේ Bot පටන් ගන්නවා
if "bot_active" not in st.session_state:
    st.info("🛰️ Bot Server එක සක්‍රීය කරමින්... කරුණාකර රැඳී සිටින්න.")
    thread = threading.Thread(target=run_bot, daemon=True)
    thread.start()
    st.session_state.bot_active = True

st.success("✅ Victims Bot දැන් සක්‍රීයයි! Telegram එකේ වැඩ පටන් ගන්න.")
