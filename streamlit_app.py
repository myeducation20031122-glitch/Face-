import streamlit as st
import pikepdf
import os
import asyncio
from telegram import Bot
import threading

# --- 🛠️ CONFIGURATION ---
# ඔයාගේ Token එක මෙතන තියෙනවා. Chat ID එක Bot විසින්ම හොයාගනීවි.
TELEGRAM_BOT_TOKEN = "3BZ7nhK5kROMEE1if5v95L2lb4E_2cswxn1jbVTnuATksZiY9"
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Global variable එකක් විදිහට Chat ID එක තියාගන්නවා
if 'chat_id' not in st.session_state:
    st.session_state.chat_id = None

# --- 🎨 PAGE STYLING ---
st.set_page_config(page_title="PDF Unlocker Pro", page_icon="🔓", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        height: 3.5em;
        background: linear-gradient(45deg, #00c6ff, #0072ff);
        color: white;
        font-weight: bold;
        border: none;
        transition: 0.4s;
        font-size: 18px;
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 30px rgba(0, 114, 255, 0.4);
    }
    .stProgress > div > div > div > div { 
        background-image: linear-gradient(to right, #00c6ff, #0072ff); 
    }
    .sidebar .sidebar-content { background-color: #161b22; }
    </style>
    """, unsafe_allow_html=True)

# --- 📱 SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/000000/lock-landscape.png")
    st.header("Control Panel ⚙️")
    start_r = st.number_input("Start Range", value=25002500)
    end_r = st.number_input("End Range", value=26002600)
    
    st.markdown("---")
    st.write("🔔 **Telegram Status:**")
    if st.session_state.chat_id:
        st.success(f"Connected to ID: {st.session_state.chat_id}")
    else:
        st.warning("Bot එකට '/start' මැසේජ් එකක් දාන්න.")

# --- 🚀 FUNCTIONS ---
async def get_chat_id():
    """Bot එකට මැසේජ් එකක් එවපු අලුත්ම කෙනාගේ ID එක ගන්නවා"""
    try:
        updates = await bot.get_updates()
        if updates:
            st.session_state.chat_id = updates[-1].message.chat_id
            return True
        return False
    except Exception:
        return False

async def send_telegram_notification(file_name, found_pwd):
    if st.session_state.chat_id:
        try:
            msg = f"🎯 **PDF UNLOCKED!**\n\n📄 File: `{file_name}`\n🔑 Password: `{found_pwd}`\n\n✅ Recovery Success."
            await bot.send_message(chat_id=st.session_state.chat_id, text=msg, parse_mode='Markdown')
        except Exception as e:
            st.error(f"Telegram Send Error: {e}")

# --- 🚀 MAIN UI ---
st.title("🔓 PDF Password Cracker Pro")
st.write("Fast recovery for encrypted PDF documents.")

uploaded_file = st.file_uploader("Drop your encrypted PDF here", type=["pdf"])

if st.button("⚡ START RECOVERY"):
    if uploaded_file is not None:
        # මුලින්ම Chat ID එක තියෙනවද බලනවා
        with st.spinner("Connecting to Telegram..."):
            asyncio.run(get_chat_id())
        
        if not st.session_state.chat_id:
            st.error("❌ කරුණාකර මුලින්ම ඔයාගේ Telegram එකෙන් Bot ට මැසේජ් එකක් (Hi/Start) දාන්න.")
        else:
            # Cracking ආරම්භය
            with open("temp.pdf", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            found = False
            progress_bar = st.progress(0)
            status_text = st.empty()
            total_steps = end_r - start_r
            
            for i, password in enumerate(range(start_r, end_r + 1)):
                pwd_str = str(password)
                
                if i % 500 == 0:
                    percent = int((i / total_steps) * 100) if total_steps > 0 else 0
                    progress_bar.progress(min(percent, 100))
                    status_text.markdown(f"🔍 Cracking: **{pwd_str}**")

                try:
                    with pikepdf.open("temp.pdf", password=pwd_str) as pdf:
                        st.balloons()
                        st.success(f"🎊 සාර්ථකයි! Password එක: **{pwd_str}**")
                        
                        # Notification
                        asyncio.run(send_telegram_notification(uploaded_file.name, pwd_str))
                        
                        # Save and Download
                        pdf.save("decrypted.pdf")
                        with open("decrypted.pdf", "rb") as dl_file:
                            st.download_button("📥 DOWNLOAD FILE", dl_file, file_name=f"fixed_{uploaded_file.name}")
                        
                        found = True
                        break
                except pikepdf.PasswordError:
                    continue
            
            if not found:
                st.error("❌ පරාසය තුළ Password එක හමු වුණේ නැත.")
            
            # Cleanup
            if os.path.exists("temp.pdf"): os.remove("temp.pdf")
    else:
        st.warning("⚠️ කරුණාකර PDF එකක් තෝරන්න.")

st.markdown("---")
st.caption("Secure PDF Recovery System v2.0")
