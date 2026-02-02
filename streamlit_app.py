import streamlit as st
import google.generativeai as genai
import requests
import json
from datetime import datetime

# 1. SETUP THE PAGE (MUST BE FIRST!)
st.set_page_config(
    page_title="Fusion Food Lab", 
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. CUSTOM CSS FOR ATTRACTIVE DESIGN
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        background-attachment: fixed;
    }
    
    .main-header {
        text-align: center;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-family: 'Orbitron', monospace;
        font-size: 3rem;
        font-weight: 900;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .sub-header {
        text-align: center;
        color: white;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        background: rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 15px;
        backdrop-filter: blur(10px);
    }
    
    .menu-item {
        background: rgba(255, 255, 255, 0.1);
        padding: 10px;
        margin: 5px 0;
        border-radius: 10px;
        border-left: 4px solid #4ecdc4;
        backdrop-filter: blur(5px);
    }
    
    .stChatMessage {
        background: rgba(255, 255, 255, 0.1) !important;
        border-radius: 15px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        backdrop-filter: blur(10px) !important;
    }
    
    .stChatMessage > div {
        background: transparent !important;
    }
    
    .sidebar-content {
        background: rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 15px;
        backdrop-filter: blur(10px);
    }
    
    .order-complete {
        background: linear-gradient(45deg, #00ff88, #00cc88);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        font-weight: bold;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .status-indicator {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 999;
        background: rgba(0, 255, 136, 0.2);
        padding: 10px;
        border-radius: 10px;
        backdrop-filter: blur(10px);
    }
</style>
""", unsafe_allow_html=True)

# 3. MAIN HEADER
st.markdown('<h1 class="main-header">🧪 FUSION FOOD LAB</h1>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">🔬 Advanced Molecular Gastronomy • AI-Powered Food Science • Real-time WhatsApp Orders</div>', unsafe_allow_html=True)

# 4. CONFIGURE GEMINI API
api_status = "🔴 Offline"
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Test the API
    model = genai.GenerativeModel('gemini-pro')
    test_response = model.generate_content("test")
    api_status = "🟢 Online"
except Exception as e:
    st.error(f"🚨 Gemini API Error: {e}")

# 5. CONFIGURE WHATSAPP (Twilio)
WHATSAPP_ACCOUNT_SID = st.secrets.get("TWILIO_ACCOUNT_SID", "")
WHATSAPP_AUTH_TOKEN = st.secrets.get("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_NUMBER = st.secrets.get("TWILIO_WHATSAPP_NUMBER", "")
YOUR_WHATSAPP_NUMBER = st.secrets.get("YOUR_WHATSAPP_NUMBER", "")

whatsapp_status = "🟢 Connected" if all([WHATSAPP_ACCOUNT_SID, WHATSAPP_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER, YOUR_WHATSAPP_NUMBER]) else "🔴 Not Configured"

# 6. STATUS INDICATOR
st.markdown(f'''
<div class="status-indicator">
    <strong>System Status:</strong><br>
    AI Brain: {api_status}<br>
    WhatsApp: {whatsapp_status}
</div>
''', unsafe_allow_html=True)

# 7. DEFINE THE ENHANCED MENU
restaurant_menu = """
🧪 FUSION FOOD LAB MENU 🧪

(A) VADAPAV REACTOR SERIES (High-Energy Street Reactions)
1. Classic Mumbai Vada Pav - ₹25 (Traditional molecular structure)
2. Cheese Fusion Vada Pav - ₹40 (Enhanced with dairy compounds)
3. Spiced Masala Pav - ₹20 (Aromatic spice molecules)
4. Cheese-Masala Hybrid - ₹30 (Complex flavor bonding)

(B) FRANKIE LABORATORY 
1. Tandoori Protein Wrap - ₹85 (Smoky molecular gastronomy)
2. Creamy Mayo Fusion - ₹85 (Emulsion-based reaction)
3. Cheese Burst Experiment - ₹110 (Thermal expansion technique)

(C) LASSI SOLUTION CHEMISTRY
1. Sweet Molecular Lassi - ₹70 (Sugar crystal suspension)
2. Rose Essence Infusion - ₹75 (Floral compound extraction)
3. Mango Puree Solution - ₹75 (Tropical enzyme activation)

LABORATORY PROTOCOLS FOR AI:
- You are Dr. Fusion, the head food scientist at our molecular gastronomy lab
- Use scientific terminology mixed with enthusiasm 
- Explain menu items as "experiments" and "molecular reactions"
- When order is complete, end with: [ORDER_COMPLETE: Item1 (₹25), Item2 (₹40), Total: ₹65]
- Be creative with food science analogies and humor
- Always maintain the lab scientist personality
"""

# 8. INITIALIZE CHAT HISTORY
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "user", "parts": [restaurant_menu]})
    st.session_state.messages.append({
        "role": "model", 
        "parts": ["🧪 Welcome to the Fusion Food Lab! I'm Dr. Fusion, your AI Food Scientist. Our molecular gastronomy lab is now ONLINE and ready to create culinary magic! What delicious experiment shall we conduct today? Each dish is a carefully crafted reaction designed to explode with flavor! 🔬✨"]
    })

# 9. ENHANCED WHATSAPP FUNCTION
def send_whatsapp_order(order_details):
    """Send order details to WhatsApp with enhanced formatting"""
    if not all([WHATSAPP_ACCOUNT_SID, WHATSAPP_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER, YOUR_WHATSAPP_NUMBER]):
        st.warning("⚠️ WhatsApp integration not configured. Order logged locally.")
        return False
    
    try:
        url = f"https://api.twilio.com/2010-04-01/Accounts/{WHATSAPP_ACCOUNT_SID}/Messages.json"
        
        message_body = f"""
🧪 FUSION FOOD LAB - NEW ORDER ALERT! 🧪

📋 ORDER DETAILS:
{order_details}

🕒 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🎯 Status: Ready for molecular preparation!

⚡ Time to start the culinary reaction! 🔥👨‍🍳

Lab Notes: All ingredients prepped and ready for fusion!
        """
        
        data = {
            "From": TWILIO_WHATSAPP_NUMBER,
            "To": YOUR_WHATSAPP_NUMBER,
            "Body": message_body
        }
        
        response = requests.post(
            url,
            data=data,
            auth=(WHATSAPP_ACCOUNT_SID, WHATSAPP_AUTH_TOKEN)
        )
        
        if response.status_code == 201:
            st.success("✅ Order transmitted to lab via WhatsApp quantum tunnel!")
            return True
        else:
            st.error(f"❌ Transmission failed: {response.text}")
            return False
            
    except Exception as e:
        st.error(f"🚨 WhatsApp molecular error: {e}")
        return False

# 10. ENHANCED SIDEBAR MENU
with st.sidebar:
    st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    st.markdown("## 🧪 LAB MENU")
    
    st.markdown("### 🥪 VADAPAV REACTOR SERIES")
    st.markdown('<div class="menu-item">🔸 Classic Mumbai Vada Pav - ₹25</div>', unsafe_allow_html=True)
    st.markdown('<div class="menu-item">🔸 Cheese Fusion Vada Pav - ₹40</div>', unsafe_allow_html=True)
    st.markdown('<div class="menu-item">🔸 Spiced Masala Pav - ₹20</div>', unsafe_allow_html=True)
    st.markdown('<div class="menu-item">🔸 Cheese-Masala Hybrid - ₹30</div>', unsafe_allow_html=True)
    
    st.markdown("### 🌯 FRANKIE LABORATORY")
    st.markdown('<div class="menu-item">🔸 Tandoori Protein Wrap - ₹85</div>', unsafe_allow_html=True)
    st.markdown('<div class="menu-item">🔸 Creamy Mayo Fusion - ₹85</div>', unsafe_allow_html=True)
    st.markdown('<div class="menu-item">🔸 Cheese Burst Experiment - ₹110</div>', unsafe_allow_html=True)
    
    st.markdown("### 🥛 LASSI SOLUTIONS")
    st.markdown('<div class="menu-item">🔸 Sweet Molecular Lassi - ₹70</div>', unsafe_allow_html=True)
    st.markdown('<div class="menu-item">🔸 Rose Essence Infusion - ₹75</div>', unsafe_allow_html=True)
    st.markdown('<div class="menu-item">🔸 Mango Puree Solution - ₹75</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🎯 LAB STATUS")
    st.markdown(f"**AI System:** {api_status}")
    st.markdown(f"**WhatsApp:** {whatsapp_status}")
    st.markdown("**Lab:** 🟢 Operational")
    
    st.markdown('</div>', unsafe_allow_html=True)

# 11. CHAT INTERFACE
st.markdown("## 💬 Chat with Dr. Fusion")

# Display chat history
for message in st.session_state.messages[2:]:
    with st.chat_message(message["role"]):
        if message["role"] == "model":
            st.markdown(f"🧪 **Dr. Fusion:** {message['parts'][0]}")
        else:
            st.markdown(message["parts"][0])

# 12. HANDLE USER INPUT
if prompt := st.chat_input("🔬 What molecular gastronomy experiment interests you?"):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Add user message to history
    st.session_state.messages.append({"role": "user", "parts": [prompt]})

    # Get response from Gemini
    try:
        model = genai.GenerativeModel('gemini-pro')
        chat_history = [
            {"role": m["role"], "parts": m["parts"]} 
            for m in st.session_state.messages
        ]
        
        response = model.generate_content(chat_history)
        response_text = response.text
        
        # Display AI response
        with st.chat_message("model"):
            st.markdown(f"🧪 **Dr. Fusion:** {response_text}")
        
        # Add AI response to history
        st.session_state.messages.append({"role": "model", "parts": [response_text]})
        
        # 13. CHECK IF ORDER IS COMPLETE
        if "[ORDER_COMPLETE:" in response_text:
            # Extract order details
            order_start = response_text.find("[ORDER_COMPLETE:")
            order_end = response_text.find("]", order_start)
            order_details = response_text[order_start + 15:order_end]
            
            # Show enhanced order confirmation
            st.balloons()
            st.markdown(f'''
            <div class="order-complete">
                🎉 EXPERIMENT COMPLETE! 🎉<br>
                Order received and being prepared in our molecular lab!<br>
                <strong>{order_details}</strong>
            </div>
            ''', unsafe_allow_html=True)
            
            # Send to WhatsApp
            send_whatsapp_order(order_details)
        
    except Exception as e:
        st.error(f"🚨 Lab Error: {e}")

# 14. FOOTER
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: rgba(255,255,255,0.7); padding: 20px;'>
    🧪 <strong>Fusion Food Lab</strong> - Where Science Meets Taste<br>
    Powered by Advanced AI • Molecular Gastronomy • Real-time Orders<br>
    <em>Every dish is a scientific breakthrough!</em> ⚡
</div>
""", unsafe_allow_html=True)
