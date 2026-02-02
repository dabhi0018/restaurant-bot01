import streamlit as st
from twilio.rest import Client
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure Gemini AI (for order queries/assistance)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-pro")

# Initialize cart in session state (replicates CartSidebar.tsx)
if "cart" not in st.session_state:
    st.session_state.cart = []

# Twilio WhatsApp Service (replicates whatsappService.ts)
def send_whatsapp_order(order_details):
    try:
        client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
        message = client.messages.create(
            body=f"New Fusion Food Lab Order:\n{order_details}",
            from_=f"whatsapp:{os.getenv('TWILIO_WHATSAPP_NUMBER')}",
            to=f"whatsapp:{os.getenv('RESTAURANT_WHATSAPP_NUMBER')}"
        )
        return True
    except Exception as e:
        st.error(f"Twilio Error: {str(e)}")
        return False

# App UI
st.title("🍴 Fusion Food Lab")
st.subheader("Quantum-Infused Dining")

# Display Menu (replicates FoodCard.tsx)
menu = [
    {"name": "Quantum Burger", "desc": "Juicy patty with quark cheese & teleportation fries", "price": "$12.99"},
    {"name": "Nano Salad", "desc": "Microgreens with molecular dressing & quantum croutons", "price": "$8.99"},
    {"name": "Black Hole Shake", "desc": "Dark chocolate shake with gravitational whipped cream", "price": "$6.99"}
]

st.write("### Our Menu")
cols = st.columns(3)
for idx, item in enumerate(menu):
    with cols[idx %3]:
        st.markdown(f"**{item['name']}**")
        st.write(item['desc'])
        st.write(f"Price: {item['price']}")
        if st.button("Add to Cart", key=f"add_{idx}"):
            st.session_state.cart.append(item)
            st.success(f"Added {item['name']} to cart!")

# Cart Sidebar
st.sidebar.title("🛒 Your Cart")
if st.session_state.cart:
    total = sum(float(i['price'].replace('$','')) for i in st.session_state.cart)
    for item in st.session_state.cart:
        st.sidebar.write(f"- {item['name']}: {item['price']}")
    st.sidebar.write(f"**Total: ${total:.2f}**")
    
    if st.sidebar.button("📤 Send Order via WhatsApp"):
        order_text = "\n".join([f"{i['name']} ({i['price']})" for i in st.session_state.cart]) + f"\nTotal: ${total:.2f}"
        if send_whatsapp_order(order_text):
            st.sidebar.success("Order sent to restaurant! 🍕")
            st.session_state.cart = []
else:
    st.sidebar.write("Your cart is empty!")

# Gemini Chat (optional customer support)
st.write("### Chat with Our Quantum Waiter")
user_query = st.text_input("Ask about menu items or your order:")
if user_query:
    response = model.generate_content(f"Act as a friendly waiter for Fusion Food Lab. Answer: {user_query}")
    st.write(f"🤖 {response.text}")
