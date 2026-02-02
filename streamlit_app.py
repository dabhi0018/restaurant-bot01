import streamlit as st
import google.generativeai as genai
import requests
import json
from datetime import datetime

# 1. SETUP THE PAGE
st.set_page_config(page_title="My AI Restaurant", page_icon="🍔")
st.title("🍔 Welcome to The AI Burger Joint")
st.write("I am your AI Waiter. Ask me about the menu or place an order!")

# 2. CONFIGURE GEMINI API
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("API Key not found. Please set it in secrets.")

# 3. CONFIGURE WHATSAPP (Twilio)
# You'll need to add these to your Streamlit secrets
WHATSAPP_ACCOUNT_SID = st.secrets.get("TWILIO_ACCOUNT_SID", "")
WHATSAPP_AUTH_TOKEN = st.secrets.get("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_NUMBER = st.secrets.get("TWILIO_WHATSAPP_NUMBER", "")  # e.g., "whatsapp:+14155552671"
YOUR_WHATSAPP_NUMBER = st.secrets.get("YOUR_WHATSAPP_NUMBER", "")  # e.g., "whatsapp:+919999999999"

# 4. DEFINE THE MENU
restaurant_menu = """
MENU:
1. Classic Burger - $10
2. Cheese Pizza - $12
3. Spicy Pasta - $11
4. Coke / Sprite - $2
5. Chocolate Cake - $5

IMPORTANT INSTRUCTIONS FOR AI:
- You are a polite waiter.
- Answer questions about the menu.
- When a customer completes their order, you MUST end your response with:
  [ORDER_COMPLETE: Item1 ($10), Item2 ($12), Total: $22]
- This special format helps the system send the order to WhatsApp.
- Keep answers short and friendly.
"""

# 5. INITIALIZE CHAT HISTORY
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "user", "parts": [restaurant_menu]})
    st.session_state.messages.append({"role": "model", "parts": ["Understood. I am ready to take orders."]})

# 6. FUNCTION TO SEND WHATSAPP MESSAGE
def send_whatsapp_order(order_details):
    """Send order details to your WhatsApp using Twilio"""
    if not WHATSAPP_ACCOUNT_SID or not WHATSAPP_AUTH_TOKEN:
        st.warning("⚠️ WhatsApp integration not set up. Order received but not sent to WhatsApp.")
        return False
    
    try:
        url = f"https://api.twilio.com/2010-04-01/Accounts/{WHATSAPP_ACCOUNT_SID}/Messages.json"
        
        message_body = f"""
🍔 NEW ORDER RECEIVED! 🍔

{order_details}

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Please prepare this order!
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

# 7. DISPLAY CHAT HISTORY
for message in st.session_state.messages[2:]:
    with st.chat_message(message["role"]):
        st.markdown(message["parts"][0])

# 8. HANDLE USER INPUT
if prompt := st.chat_input("What would you like to order?"):
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
        
        # 9. CHECK IF ORDER IS COMPLETE
        if "[ORDER_COMPLETE:" in response_text:
            # Extract order details
            order_start = response_text.find("[ORDER_COMPLETE:")
            order_end = response_text.find("]", order_start)
            order_details = response_text[order_start + 15:order_end]
            
            # Send to WhatsApp
            send_whatsapp_order(order_details)
        
    except Exception as e:
        st.error(f"An error occurred: {e}")
