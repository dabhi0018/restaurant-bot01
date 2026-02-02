import streamlit as st
import google.generativeai as genai
import requests
import json
from datetime import datetime

# 1. SETUP THE PAGE (MUST BE FIRST!)
st.set_page_config(page_title="Fusion Food Lab", page_icon="🧪")
st.title("🧪 Welcome to The Fusion Food Lab")
st.write("I am your AI Food Scientist. Explore our molecular gastronomy menu and place your order!")

# 2. CONFIGURE GEMINI API
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("API Key not found. Please set it in secrets.")

# 3. CONFIGURE WHATSAPP (Twilio)
WHATSAPP_ACCOUNT_SID = st.secrets.get("TWILIO_ACCOUNT_SID", "")
WHATSAPP_AUTH_TOKEN = st.secrets.get("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_NUMBER = st.secrets.get("TWILIO_WHATSAPP_NUMBER", "")  # e.g., "whatsapp:+14155552671"
YOUR_WHATSAPP_NUMBER = st.secrets.get("YOUR_WHATSAPP_NUMBER", "")  # e.g., "whatsapp:+919876543210"

# 4. DEFINE THE MENU
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

# 5. INITIALIZE CHAT HISTORY
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "user", "parts": [restaurant_menu]})
    st.session_state.messages.append({"role": "model", "parts": ["Welcome to the Fusion Food Lab! I'm ready to help you create the perfect food reaction. What molecular combination would you like to try today?"]})

# 6. FUNCTION TO SEND WHATSAPP MESSAGE
def send_whatsapp_order(order_details):
    """Send order details to your WhatsApp using Twilio"""
    if not WHATSAPP_ACCOUNT_SID or not WHATSAPP_AUTH_TOKEN:
        st.warning("⚠️ WhatsApp integration not set up. Order received but not sent to WhatsApp.")
        return False
    
    try:
        url = f"https://api.twilio.com/2010-04-01/Accounts/{WHATSAPP_ACCOUNT_SID}/Messages.json"
        
        message_body = f"""
🧪 NEW LAB ORDER! 🧪

{order_details}

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Ready to start cooking! 🔥
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
            st.success("✅ Order sent to your WhatsApp!")
            return True
        else:
            st.error(f"Error sending WhatsApp: {response.text}")
            return False
            
    except Exception as e:
        st.error(f"WhatsApp error: {e}")
        return False

# 7. DISPLAY MENU IN SIDEBAR
with st.sidebar:
    st.header("🧪 Lab Menu")
    st.markdown("""
    **VADAPAV SERIES** *(High-Energy Reactions)*
    - Mumbaiya Vada Pav: ₹25
    - Cheese Burst Vada Pav: ₹40
    - Masala Pav: ₹20
    - Cheese Masala Pav: ₹30
    
    **FRANKIE LAB**
    - Tandoori Frankie: ₹85
    - Mayo Frankie: ₹85
    - Cheese Burst Frankie: ₹110
    
    **LASSI SOLUTIONS**
    - Meethi Lassi: ₹70
    - Rose Lassi: ₹75
    - Mango Lassi: ₹75
    """)

# 8. DISPLAY CHAT HISTORY
for message in st.session_state.messages[2:]:
    with st.chat_message(message["role"]):
        st.markdown(message["parts"][0])

# 9. HANDLE USER INPUT
if prompt := st.chat_input("What fusion experiment would you like to try?"):
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
            st.markdown(response_text)
        
        # Add AI response to history
        st.session_state.messages.append({"role": "model", "parts": [response_text]})
        
        # 10. CHECK IF ORDER IS COMPLETE
        if "[ORDER_COMPLETE:" in response_text:
            # Extract order details
            order_start = response_text.find("[ORDER_COMPLETE:")
            order_end = response_text.find("]", order_start)
            order_details = response_text[order_start + 15:order_end]
            
            # Show order confirmation
            st.balloons()
            st.success("🎉 Order Received! Sending to kitchen...")
            
            # Send to WhatsApp
            send_whatsapp_order(order_details)
        
    except Exception as e:
        st.error(f"An error occurred: {e}")

# 11. ADD SOME STYLE
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)
