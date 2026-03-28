import streamlit as st
import asyncio
import os
import pikepdf
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- 🛠️ CONFIGURATION ---
TOKEN = "7747068384:AAEcjBAH-4vVMEzJtmKeozOZjR7J3vOGvBo"

st.set_page_config(page_title="PDF Cracker Bot Host", page_icon="🤖")
st.title("🤖 Telegram PDF Cracker Bot")
st.info("මෙම පිටුව විවෘතව තබන්න. එවිට Bot සක්‍රීයව පවතිනු ඇත.")

# --- 🤖 BOT LOGIC ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 හායි බොසා! මට Locked PDF එකක් එවන්න, මම ඒක පරීක්ෂා කරලා එවන්නම්.")

async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    file_name = update.message.document.file_name
    
    status_msg = await update.message.reply_text("📥 PDF එක ලැබුණා. පරීක්ෂා කරමින්... 🔍")
    
    input_path = f"locked_{file_name}"
    await file.download_to_drive(input_path)

    # Password Range
    start_r = 25002500
    end_r = 26002600
    found_pwd = None

    try:
        for password in range(start_r, end_r + 1):
            pwd_str = str(password)
            try:
                with pikepdf.open(input_path, password=pwd_str) as pdf:
                    found_pwd = pwd_str
                    output_path = f"unlocked_{file_name}"
                    pdf.save(output_path)
                    break
            except pikepdf.PasswordError:
                continue

        if found_pwd:
            await status_msg.edit_text(f"✅ Password Found: `{found_pwd}`")
            await update.message.reply_document(document=open(output_path, 'rb'), caption=f"🔓 Unlocked!\n🔑 Password: {found_pwd}")
            os.remove(output_path)
        else:
            await status_msg.edit_text("❌ Password එක හමු වුණේ නැහැ.")

    except Exception as e:
        await status_msg.edit_text(f"⚠️ Error: {str(e)}")
    finally:
        if os.path.exists(input_path): os.remove(input_path)

# --- 🚀 STREAMLIT RUNNER ---
async def run_bot():
    # මෙතනදී කලින් තිබුණු instances අයින් කරලා අලුතින් පටන් ගන්නවා
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))
    
    st.success("🚀 Bot is LIVE and Running...")
    
    async with app:
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        # Bot එක දිගටම run වෙන්න සලස්වනවා
        while True:
            await asyncio.sleep(1)

if st.button("▶️ Start Bot Server"):
    try:
        asyncio.run(run_bot())
    except Exception as e:
        st.error(f"Bot එක දැනටමත් ක්‍රියාත්මකයි හෝ අවුලක් තියෙනවා: {e}")
