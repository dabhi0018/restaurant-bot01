import streamlit as st
from utils.twilio_service import WhatsAppService

# Initialize WhatsApp service
whatsapp = WhatsAppService()

# Streamlit App
st.title("🍕 WhatsApp Food Ordering System")
st.write("Send food orders via WhatsApp!")

# UI for sending WhatsApp messages
with st.form("send_message"):
    st.subheader("Send Order via WhatsApp")
    
    phone_number = st.text_input(
        "Customer Phone Number", 
        placeholder="+1234567890"
    )
    
    # Food menu
    food_items = {
        "🍕 Pizza": 12.99,
        "🍔 Burger": 8.99,  
        "🌮 Tacos": 6.99,
        "🍝 Pasta": 10.99
    }
    
    selected_food = st.selectbox("Select Food Item", list(food_items.keys()))
    quantity = st.number_input("Quantity", min_value=1, value=1)
    
    # Calculate total
    total = food_items[selected_food] * quantity
    st.write(f"**Total: ${total:.2f}**")
    
    submitted = st.form_submit_button("Send WhatsApp Order")
    
    if submitted:
        if phone_number:
            # Create order message
            order_msg = f"""
🍽️ **NEW ORDER**

Item: {selected_food}
Quantity: {quantity}
Total: ${total:.2f}

Reply 'CONFIRM' to confirm your order!
            """
            
            # Send WhatsApp message
            success, result = whatsapp.send_message(phone_number, order_msg)
            
            if success:
                st.success(f"✅ Order sent to {phone_number}!")
                st.balloons()
            else:
                st.error(f"❌ Failed to send: {result}")
        else:
            st.error("Please enter a phone number")

# Display recent orders (you can expand this with database)
st.subheader("📋 Recent Orders")
if 'orders' not in st.session_state:
    st.session_state.orders = []

# Show orders (this is just for demo)
for i, order in enumerate(st.session_state.orders[-5:]):  # Show last 5
    st.write(f"{i+1}. {order}")
