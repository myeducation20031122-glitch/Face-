import streamlit as st
import numpy as np
import time

# පිටුවේ සැකසුම් (Page Config)
st.set_page_config(page_title="Multiverse Engine", layout="centered")

# CSS මගින් Dark Theme එක සහ UI එක ලස්සන කිරීම
st.markdown("""
    <style>
    .main { background-color: #000000; }
    .stTitle { color: #00f2ff; text-align: center; font-family: 'Courier New', Courier, monospace; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌌 MULTIVERSE ENGINE: UNLIMITED")

# සංකේත වල අගයන් (Mapping Symbols to Frequencies)
vals = np.array([10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 150, 200, 255])

# Grid එක සැකසීම (Resolution එක 150ක් වගේ ගමු Streamlit එකට ගැලපෙන්න)
res = 150
x = np.linspace(-10, 10, res)
y = np.linspace(-10, 10, res)
X, Y = np.meshgrid(x, y)

# රූපය පෙන්වීමට හිස් තැනක් වෙන් කිරීම
placeholder = st.empty()

# සැබෑ සජීවී ලූපය (Infinite Loop for Live Animation)
start_time = time.time()

while True:
    t = time.time() - start_time
    
    # ත්‍රිකෝණමිතික තරංග සමීකරණය
    Z = np.zeros((res, res))
    
    # සංකේත කිහිපයක බලපෑම එකතු කිරීම
    for i in range(4):
        freq = vals[i % len(vals)] / 20.0
        # Linear waves + Circular interference
        Z += np.sin(freq * X + t) * np.cos((vals[(i+1)%len(vals)]/30.0) * Y - t)
        Z += np.sin(np.sqrt(X**2 + Y**2) * (freq/2) - t * 1.5)

    # දත්ත 0-255 අතරට ගෙන ඒම
    Z_norm = (Z - Z.min()) / (Z.max() - Z.min())
    
    # Streamlit එකේ රූපය පෙන්වීම (Inferno Colormap එකට සමාන වර්ණ රටා)
    # මෙහිදී අපිට Plotly හෝ Matplotlib අවශ්‍ය නැහැ, කෙලින්ම Array එක පෙන්විය හැක
    placeholder.image(Z_norm, use_container_width=True, clamp=True)
    
    # සුළු විරාමයක් (Frame rate එක පාලනයට)
    time.sleep(0.01)
