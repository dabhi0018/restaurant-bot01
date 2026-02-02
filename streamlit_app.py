import streamlit as st
import google.generativeai as genai
import requests
from datetime import datetime
import time  # For subtle animations

# Page config for wide, immersive lab view
st.set_page_config(
    page_title="🧪 Fusion Food Lab",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS: Sci-fi lab with gradients, glows, particles
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Space+Grotesk:wght@400;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0c0c0c 0%, #1a0033 50%, #0f0f23 100%);
        background-attachment: fixed;
        color: #e0e0ff;
        font-family: 'Space Grotesk', sans-serif;
    }
    
    .neon-title {
        font-family: 'Orbitron', monospace;
        font-size: 3rem;
        background: linear-gradient(45deg, #ff00ff, #00ffff, #ffff00);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: neon-glow 2s ease-in-out infinite alternate;
        text-align: center;
        text-shadow: 0 0 20px #ff00ff;
    }
    
    @keyframes neon-glow {
        from { filter: hue-rotate(0deg); }
        to { filter: hue-rotate(360deg); }
    }
    
    .lab-card {
        background: rgba(20, 20, 40, 0.8);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 255, 255, 0.3);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 20px 40px rgba(0, 255, 255, 0.1);
        transition: all 0.3s ease;
    }
    
    .lab-card:hover {
        border-color: #00ffff;
        box-shadow: 0 20px 60px rgba(0, 255, 255, 0.3);
        transform: translateY(-5px);
    }
    
    .menu-item {
        background: rgba(255, 255, 255, 0.05);
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 12px;
        border-left: 4px solid #ffd700;
        transition: 0.2s;
    }
    
    .stChatMessage {
        background: rgba(0, 255, 255, 0.1);
        border-radius: 16px;
        border: 1px solid rgba(0, 255, 255, 0.2);
    }
    
    /* Sidebar enhancements */
    .stSidebar {
        background: linear-gradient(180deg, rgba(10,10,30,0.95) 0%, rgba(30,0,60,0.95) 100%);
    }
    
    /* Dark toggle (bonus) */
    .dark-toggle { width: 100%; }
</style>
""", unsafe_allow_html=True)

# Animated title block
col1, col2 = st.columns([3,1])
with col1:
    st.markdown('<div class="lab-card"><h1 class="neon-title">🧪 Fusion Food Lab</h1><p style="text-align:center; font-size:1.2rem;">Molecular Gastronomy | AI-Powered Orders | WhatsApp Delivery</p></div>', unsafe_allow_html=True)

with col2:
    dark_mode = st.toggle("🌙 Night Lab Mode", value=True)
    if not dark_mode:
        st.markdown("""
        <style>
            .stApp { background: linear-gradient(135deg, #f0f8ff 0%, #e6e6fa 100%); color: #333; }
            .lab-card { background: rgba(255,255,255,0.9); border-color: rgba(0,0,255,0.3); }
        </style>
        """, unsafe_allow_html=True)

# Menu prompt for Gemini (unchanged)
restaurant_menu = """
🧪 FUSION FOOD LAB MENU 🧪

(A) VADAPAV SERIES (High-Energy Reactions)
1. Mumbaiya Vada Pav     - ₹25
2. Cheese Burst Vada Pav - ₹40
3. Masala Pav            - ₹20
4. Cheese Masala Pav     - ₹30

(B) FRANKIE LAB 
1. Tandoori Frankie      - ₹85
2. Mayo Frankie          - ₹85
3. Cheese Burst Frankie  - ₹110

(C) LASSI SOLUTIONS 
1. Meethi Lassi          - ₹70
2. Rose Lassi            - ₹75
3. Mango Lassi           - ₹75

IMPORTANT INSTRUCTIONS FOR AI:
- You are a friendly food scientist waiter at "Fusion Food Lab".
- Use fun science terms when describing food (e.g., "molecular," "fusion," "reaction").
- Answer questions about the menu with enthusiasm.
- When a customer completes their order, you MUST end your response with:
  [ORDER_COMPLETE: Item1 (₹25), Item2 (₹40), Total: ₹65]
- This special format helps the system send the order to WhatsApp.
- Keep answers friendly and use food science humor.
- Always use ₹ (rupees) for prices.
"""

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "user", "parts": [restaurant_menu]},
        {"role": "model", "parts": ["Welcome, Lab Partner! 🚀 What explosive fusion dish shall we synthesize today?"]}
    ]

# Secrets & Gemini setup (with fallback)
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")  # ✅ FIXED: Use this instead of "gemini-pro"
    st.success("🧪 Gemini Lab online!")
except KeyError:
    st.error("🔑 GEMINI_API_KEY missing in secrets.toml")
    model = None
except Exception as e:
    st.error(f"Gemini setup failed: {e}")
    model = None

# WhatsApp vars
twilio_sid = st.secrets.get("TWILIO_ACCOUNT_SID", "")
twilio_token = st.secrets.get("TWILIO_AUTH_TOKEN", "")
twilio_from = st.secrets.get("TWILIO_WHATSAPP_NUMBER", "")
your_num = st.secrets.get("YOUR_WHATSAPP_NUMBER", "")

def send_whatsapp_order(order_details):
    if not all([twilio_sid, twilio_token, twilio_from, your_num]):
        st.warning("⚠️ Twilio secrets incomplete – order logged locally.")
        return False
    url = f"https://api.twilio.com/2010-04-01/Accounts/{twilio_sid}/Messages.json"
    payload = {
        "From": twilio_from,
        "To": your_num,
        "Body": f"🧪 LAB ORDER ALERT! 🧪\n\n{order_details}\n\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    }
    try:
        resp = requests.post(url, data=payload, auth=(twilio_sid, twilio_token))
        if resp.status_code == 201:
            st.success("✅ Order beamed to WhatsApp! 🚀")
            st.balloons()
            return True
        else:
            st.error(f"Twilio: {resp.text}")
    except Exception as e:
        st.error(f"WhatsApp send failed: {e}")
    return False

# Sidebar: Interactive Menu
with st.sidebar:
    st.markdown('<div class="lab-card"><h2>🍔 Lab Menu</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="menu-item">🥟 **VadaPav Series**<br>1. Mumbaiya ₹25 | 2. Cheese Burst ₹40 | 3. Masala ₹20 | 4. Cheese Masala ₹30</div>
    <div class="menu-item">🌯 **Frankie Lab**<br>1. Tandoori ₹85 | 2. Mayo ₹85 | 3. Cheese Burst ₹110</div>
    <div class="menu-item">🥛 **Lassi Solutions**<br>1. Meethi ₹70 | 2. Rose ₹75 | 3. Mango ₹75</div>
    """, unsafe_allow_html=True)
    
    if st.button("🔥 Quick Order: VadaPav Combo (₹65)", use_container_width=True):
        st.session_state.messages[-1]["parts"][0] += "\n\nI'd like: Mumbaiya Vada Pav + Mango Lassi."
        st.rerun()

# Chat history display
for msg in st.session_state.messages[1:]:  # Skip initial menu
    with st.chat_message(msg["role"]):
        st.markdown(msg["parts"][0])

# Chat input
if prompt := st.chat_input("💭 Enter your fusion order or question..."):
    st.session_state.messages.append({"role": "user", "parts": [prompt]})
    with st.chat_message("user"):
        st.markdown(prompt)

    if model:
        with st.chat_message("assistant"):
            with st.spinner("🔬 Synthesizing response..."):
                try:
                    response = model.generate_content([
                        {"role": m["role"], "parts": m["parts"]} for m in st.session_state.messages
                    ])
                    resp_text = response.text
                
