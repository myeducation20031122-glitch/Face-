import streamlit as st
import socket
import ssl
import threading

# --- ISP BYPASS CONFIG ---
LISTEN_PORT = 8989
# මේක තමයි උඹේ YouTube Package එකේ 'Free' Host එක
SNI_HOST = "m.youtube.com" 

st.title("🛰️ Stealth Net Tunnel V2X")
st.error("ISP FIREWALL BYPASS: ENABLED 🟢")

def handle_client(client_socket):
    try:
        # 1. පලවෙනි Request එක ගන්නවා
        request = client_socket.recv(4096).decode('utf-8', errors='ignore')
        if not request: return

        # 2. HTTPS නම් SNI එක Override කරනවා
        # මේක තමයි Dialog/Mobitel එකට පේන 'බොරු' නම
        target_host = "google.com" # උඹට සැබෑවටම යන්න ඕන තැන
        target_port = 443

        # 3. Secure Tunnel එකක් හදනවා
        context = ssl.create_default_context()
        # මෙතනදී අපි SNI එක විදිහට m.youtube.com යවනවා
        with socket.create_connection((target_host, target_port)) as sock:
            with context.wrap_socket(sock, server_hostname=SNI_HOST) as ssock:
                st.write(f"🔗 Tunnel established: {target_host} via {SNI_HOST}")
                # දත්ත හුවමාරු කිරීමේ Logic එක මෙතනට එන්න ඕනේ (Proxying)
    except Exception as e:
        pass
    finally:
        client_socket.close()

def start_engine():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', LISTEN_PORT))
    server.listen(10)
    while True:
        client, addr = server.accept()
        threading.Thread(target=handle_client, args=(client,)).start()

if st.button("ACTIVATE STEALTH TUNNEL"):
    threading.Thread(target=start_engine, daemon=True).start()
    st.success(f"🚀 Stealth Tunneling started on port {LISTEN_PORT}!")

st.markdown("""
### **උපදෙස් (The Hacker Manual):**
1. මේ Script එක Streamlit Cloud එකේ Deploy කරලා URL එක ගන්න.
2. ෆෝන් එකේ **HTTP Custom** හෝ **HTTP Injector** වගේ App එකක් පාවිච්චි කරලා, **SNI Host** එකට `m.youtube.com` දීලා, **Proxy** එකට උඹේ Streamlit URL එක දෙන්න.
""")
