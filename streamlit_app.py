import streamlit as st
import google.generativeai as genai
import requests
from datetime import datetime
import json

# Page config (mobile-first, wide layout like apps)
st.set_page_config(
    page_title="🧪 Fusion Food Lab | Order Now",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS (Zomato/Swiggy inspired: Vibrant gradients, cards, buttons, shadows)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
.stApp { background: linear-gradient(135deg, #ff6b35 0%, #f7931e 50%, #ffd23f 100%); font-family: 'Poppins', sans-serif; }
.header-hero { background: linear-gradient(135deg, #ff6b35, #f7931e); padding: 2rem; border-radius: 20px; color: white; text-align: center; box-shadow: 0 20px 40px rgba(0,0,0,0.2); }
.restaurant-name { font-size: 2.5rem; font-weight: 700; margin: 0; }
.rating { background: #4CAF50; color: white; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.9rem; font-weight: 600; display: inline-block; margin: 0.5rem 0; }
.delivery-info { font-size: 1rem; opacity: 0.9; }
.menu-tab { background: rgba(255,255,255,0.9); border-radius: 15px; padding: 1.5rem; margin: 1rem 0; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
.item-card { background: white; border-radius: 15px; padding: 1.2rem; margin: 1rem 0; box-shadow: 0 8px 25px rgba(0,0,0,0.1); transition: transform 0.3s; position: relative; overflow: hidden; }
.item-card:hover { transform: translateY(-5px); box-shadow: 0 15px 40px rgba(0,0,0,0.15); }
.item-image { width: 100%; height: 150px; background: linear-gradient(45deg, #ff9a56, #ff6b6b); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 3rem; margin-bottom: 1rem; }
.item-name { font-size: 1.3rem; font-weight: 600; color: #333; }
.item-price { font-size: 1.4rem; font-weight: 700; color: #ff6b35; }
.qty-btn { background: #ff6b35; color: white; border: none; border-radius: 50px; padding: 0.5rem 1rem; font-weight: 600; cursor: pointer; transition: all 0.3s; }
.qty-btn:hover { background: #e55a2b; transform: scale(1.05); }
.cart-badge { background: #4CAF50; color: white; border-radius: 50%; padding: 0.3rem 0.6rem; font-size: 0.9rem; font-weight: 600; }
.cart-panel { background: rgba(255,255,255,0.95); border-radius: 20px; padding: 2rem; box-shadow: 0 20px 40px rgba(0,0,0,0.2); position: sticky; top: 20px; }
.checkout-btn { background: linear-gradient(45deg, #4CAF50, #45a049); color: white; border: none; border-radius: 15px; padding: 1rem 2rem; font-size: 1.2rem; font-weight: 600; width: 100%; transition: all 0.3s; }
.checkout-btn:hover { transform: scale(1.02); box-shadow: 0 10px 20px rgba(76,175,80,0.4); }
.empty-cart { text-align: center; color: #666; padding: 3rem; }
.ai-chat { position: fixed; bottom: 20px; right: 20px; width: 60px; height: 60px; background: #ff6b35; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; cursor: pointer; box-shadow: 0 10px 30px rgba(0,0,0,0.3); z-index: 1000; }
.stSidebar { background: linear-gradient(135deg, #ff9a56, #ff6b6b); }
</style>
""", unsafe_allow_html=True)

# Session state for cart
if "cart" not in st.session_state:
    st.session_state.cart = {}
if "total" not in st.session_state:
    st.session_state.total = 0

# Secrets
genai.configure(api_key=st.secrets.get("GEMINI_API_KEY", ""))
twilio_sid = st.secrets.get("TWILIO_ACCOUNT_SID", "")
twilio_token = st.secrets.get("TWILIO_AUTH_TOKEN", "")
twilio_from = st.secrets.get("TWILIO_WHATSAPP_NUMBER", "")
your_num = st.secrets.get("YOUR_WHATSAPP_NUMBER", "")

# WhatsApp send function
def send_whatsapp_order(cart_items, total):
    if not all([twilio_sid, twilio_token, twilio_from, your_num]):
        st.warning("⚠️ WhatsApp not configured. Order logged locally.")
        return False
    order_details = "\n".join([f"{item}: {qty} x ₹{price}" for item, (qty, price) in cart_items.items()]) + f"\n\n💰 Total: ₹{total}"
    url = f"https://api.twilio.com/2010-04-01/Accounts/{twilio_sid}/Messages.json"
    payload = {
        "From": twilio_from,
        "To": your_num,
        "Body": f"🧪 NEW ORDER from Fusion Food Lab!\n\n{order_details}\n\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    }
    try:
        resp = requests.post(url, data=payload, auth=(twilio_sid, twilio_token))
        return resp.status_code == 201
    except:
        return False

# Header (Zomato-style hero)
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("""
    <div class="header-hero">
        <h1 class="restaurant-name">🧪 Fusion Food Lab</h1>
        <div class="rating">4.8 ★ (2.5k)</div>
        <div class="delivery-info">🚀 25-30 mins • ₹50 delivery • 100% veg</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    if st.button("⭐ Rate Us", key="rate"):
        st.success("Thanks for rating! 🌟")

# Menu data (categories like Zomato)
menu = {
    "🥪 VadaPav Reactor": [
        {"name": "Classic Mumbai Vada Pav", "price": 25, "desc": "Traditional molecular structure"},
        {"name": "Cheese Fusion Vada Pav", "price": 40, "desc": "Enhanced with dairy compounds"},
        {"name": "Spiced Masala Pav", "price": 20, "desc": "Aromatic spice molecules"},
        {"name": "Cheese-Masala Hybrid", "price": 30, "desc": "Complex flavor bonding"}
    ],
    "🌯 Frankie Lab": [
        {"name": "Tandoori Protein Wrap", "price": 85, "desc": "Smoky molecular gastronomy"},
        {"name": "Creamy Mayo Fusion", "price": 85, "desc": "Emulsion-based reaction"},
        {"name": "Cheese Burst Experiment", "price": 110, "desc": "Thermal expansion technique"}
    ],
    "🥛 Lassi Solutions": [
        {"name": "Sweet Molecular Lassi", "price": 70, "desc": "Sugar crystal suspension"},
        {"name": "Rose Essence Infusion", "price": 75, "desc": "Floral compound extraction"},
        {"name": "Mango Puree Solution", "price": 75, "desc": "Tropical enzyme activation"}
    ]
}

# Main content: Tabs for categories
tab1, tab2, tab3 = st.tabs(["🥪 VadaPav Reactor", "🌯 Frankie Lab", "🥛 Lassi Solutions"])

for tab, category in zip([tab1, tab2, tab3], menu.values()):
    for item in category:
        with tab.container():
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.markdown(f"""
                <div class="item-card">
                    <div class="item-image">🍔</div>
                    <h3 class="item-name">{item['name']}</h3>
                    <p>{item['desc']}</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div class='item-price'>₹{item['price']}</div>", unsafe_allow_html=True)
            with col3:
                if item['name'] in st.session_state.cart:
                    qty = st.session_state.cart[item['name']][0]
                    col_a, col_b, col_c = st.columns([1,2,1])
                    col_a.button("➖", key=f"dec_{item['name']}", on_click=lambda i=item['name']: update_cart(i, -1))
                    col_b.markdown(f"**{qty}x**")
                    col_c.button("➕", key=f"inc_{item['name']}", on_click=lambda i=item['name']: update_cart(i, 1))
                else:
                    if st.button("🛒 ADD", key=f"add_{item['name']}"):
                        update_cart(item['name'], 1)

# Helper functions (define after menu for lambda)
def update_cart(item_name, delta):
    if item_name in st.session_state.cart:
        qty, price = st.session_state.cart[item_name]
        qty += delta
        if qty <= 0:
            del st.session_state.cart[item_name]
        else:
            st.session_state.cart[item_name] = (qty, price)
    else:
        # Find price from menu
        for cat_items in menu.values():
            for it in cat_items:
                if it['name'] == item_name:
                    st.session_state.cart[item_name] = (1, it['price'])
                    break
    st.session_state.total = sum(q * p for _, (q, p) in st.session_state.cart.items())
    st.rerun()

# Cart Sidebar (fixed like Swiggy)
with st.sidebar:
    st.markdown("<h2>🛒 Your Cart ({len(st.session_state.cart)})</h2>", unsafe_allow_html=True)
    if st.session_state.cart:
        for item, (qty, price) in st.session_state.cart.items():
            st.markdown(f"**{item}** x{qty} • ₹{qty * price}")
            col1, col2 = st.columns([3,1])
            col1.empty()
            if col2.button("✕", key=f"rm_{item}"):
                del st.session_state.cart[item]
                st.session_state.total = sum(q * p for _, (q, p) in st.session_state.cart.items())
                st.rerun()
        st.markdown("---")
        st.markdown(f"### 💰 Total: **₹{st.session_state.total}**")
        st.markdown("**Delivery: FREE**")
        st.markdown(f"### **Grand Total: ₹{st.session_state.total}**")
        if st.button("🚀 PLACE ORDER", help="Sends to WhatsApp"):
            if send_whatsapp_order(st.session_state.cart, st.session_state.total):
                st.success("✅ Order placed! Check WhatsApp 🚀")
                st.balloons()
                st.session_state.cart = {}
                st.session_state.total = 0
                st.rerun()
            else:
                st.error("❌ Order failed. Check secrets.")
    else:
        st.markdown('<div class="empty-cart">Your cart is empty<br>🥺<br>Add items from menu!</div>', unsafe_allow_html=True)

# AI Chat Button (floating, opens expander)
if st.button("💬 AI Help", key="ai_chat", help="Ask Dr. Fusion for recs!"):
    with st.expander("🧪 Chat with Dr. Fusion", expanded=True):
        if "ai_messages" not in st.session_state:
            st.session_state.ai_messages = []
        for msg in st.session_state.ai_messages:
            st.chat_message(msg["role"]).markdown(msg["content"])
        if prompt := st.chat_input("Ask about menu or recs..."):
            st.session_state.ai_messages.append({"role": "user", "content": prompt})
            st.chat_message("user").markdown(prompt)
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                chat = model.start_chat(history=st.session_state.ai_messages)
                resp = chat.send_message(prompt)
                st.session_state.ai_messages.append({"role": "assistant", "content": resp.text})
                st.rerun()
            except Exception as e:
                st.error(f"AI Error: {e}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: white; padding: 1rem; font-size: 0.9rem;'>
    🧪 Fusion Food Lab | Like Zomato/Swiggy | Powered by Streamlit & Gemini
</div>
""", unsafe_allow_html=True)
                
