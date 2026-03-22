import psutil
import streamlit as st

# --- DATA TRACKER FUNCTION ---
def get_usage():
    # සර්වර් එකේ network interface එකෙන් දත්ත ගන්නවා
    net_io = psutil.net_io_counters()
    
    # Bytes වලින් එන ඒවා MB වලට හරවනවා
    downloaded = net_io.bytes_recv / (1024 * 1024)
    uploaded = net_io.bytes_sent / (1024 * 1024)
    total = downloaded + uploaded
    
    return f"📊 **FREE NET USAGE REPORT**\n\n📥 Download: {downloaded:.2f} MB\n📤 Upload: {uploaded:.2f} MB\n🚀 Total Data: {total:.2f} MB"

# --- TELEGRAM COMMAND ---
@bot.message_handler(commands=['usage'])
def send_usage(message):
    usage_report = get_usage()
    bot.reply_to(message, usage_report)

# --- STREAMLIT UI DISPLAY ---
st.subheader("📡 Real-time Bandwidth Monitor")
usage_text = get_usage()
st.code(usage_text)
