import streamlit as st
import google.generativeai as genai
import requests
import json
from datetime import datetime, timedelta
import time

# 🚀 PAGE CONFIGURATION
st.set_page_config(
    page_title="FoodFast - Food Delivery", 
    page_icon="🍕",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 🎨 MODERN CSS (ZOMATO/SWIGGY STYLE)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    .stApp {
        background: #f8f9fa;
        font-family: 'Inter', sans-serif;
    }
    
    /* HEADER SECTION */
    .delivery-header {
        background: linear-gradient(135deg, #fc8019 0%, #ff6b35 100%);
        padding: 20px 0;
        color: white;
        text-align: center;
        box-shadow: 0 2px 20px rgba(252, 128, 25, 0.3);
    }
    
    .delivery-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
    }
    
    .delivery-header p {
        font-size: 1.1rem;
        opacity: 0.9;
        margin-top: 5px;
    }
    
    /* LOCATION BAR */
    .location-bar {
        background: white;
        padding: 15px 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    /* FOOD CARD STYLES */
    .food-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 2px 15px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .food-card:hover {
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
        transform: translateY(-2px);
    }
    
    .food-card .tag {
        position: absolute;
        top: 15px;
        right: 15px;
        background: #28a745;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .food-card .bestseller {
        background: #fc8019;
    }
    
    .food-item-header {
        display: flex;
        justify-content: space-between;
        align-items: start;
        margin-bottom: 10px;
    }
    
    .food-name {
        font-size: 1.3rem;
        font-weight: 600;
        color: #333;
        margin: 0;
    }
    
    .food-price {
        font-size: 1.4rem;
        font-weight: 700;
        color: #fc8019;
        margin: 0;
    }
    
    .food-description {
        color: #666;
        font-size: 0.95rem;
        line-height: 1.5;
        margin: 8px 0;
    }
    
    .food-meta {
        display: flex;
        align-items: center;
        gap: 15px;
        margin: 10px 0;
    }
    
    .rating {
        display: flex;
        align-items: center;
        gap: 5px;
        background: #28a745;
        color: white;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    .prep-time {
        color: #666;
        font-size: 0.85rem;
    }
    
    /* CART SECTION */
    .cart-container {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: #fc8019;
        color: white;
        padding: 15px 25px;
        border-radius: 50px;
        box-shadow: 0 5px 25px rgba(252, 128, 25, 0.4);
        cursor: pointer;
        z-index: 1000;
        font-weight: 600;
        animation: pulse 2s infinite;
    }
    
    .cart-container:hover {
        background: #e67411;
        transform: scale(1.05);
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    
    /* BUTTONS */
    .add-btn {
        background: linear-gradient(135deg, #fc8019 0%, #ff6b35 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
        margin-top: 10px;
    }
    
    .add-btn:hover {
        background: linear-gradient(135deg, #e67411 0%, #e55a2b 100%);
        transform: translateY(-1px);
    }
    
    /* ORDER TRACKING */
    .order-status {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        margin: 20px 0;
        animation: slideIn 0.5s ease-out;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* CHECKOUT SECTION */
    .checkout-section {
        background: white;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 2px 15px rgba(0,0,0,0.1);
        margin: 20px 0;
    }
    
    .checkout-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #333;
        margin-bottom: 20px;
        border-bottom: 2px solid #f0f0f0;
        padding-bottom: 10px;
    }
    
    .bill-item {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid #f5f5f5;
    }
    
    .bill-total {
        display: flex;
        justify-content: space-between;
        padding: 15px 0;
        font-size: 1.2rem;
        font-weight: 700;
        border-top: 2px solid #fc8019;
        color: #fc8019;
    }
    
    /* RESPONSIVE */
    @media (max-width: 768px) {
        .food-item-header {
            flex-direction: column;
            gap: 10px;
        }
        
        .cart-container {
            bottom: 10px;
            right: 10px;
            padding: 12px 20px;
        }
    }
</style>
""", unsafe_allow_html=True)

# 📊 SESSION STATE INITIALIZATION
if "cart" not in st.session_state:
    st.session_state.cart = []
if "cart_total" not in st.session_state:
    st.session_state.cart_total = 0.0
if "order_placed" not in st.session_state:
    st.session_state.order_placed = False
if "delivery_address" not in st.session_state:
    st.session_state.delivery_address = ""
if "order_id" not in st.session_state:
    st.session_state.order_id = None

# 🔧 GEMINI API SETUP
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
    api_status = "🟢 AI Online"
except Exception as e:
    st.error(f"⚠️ AI Service Unavailable: {e}")
    api_status = "🔴 AI Offline"

# 🍕 MENU DATA (LIKE ZOMATO/SWIGGY)
menu_items = [
    {
        "id": 1,
        "name": "Margherita Pizza",
        "description": "Fresh tomato sauce, mozzarella cheese, basil leaves",
        "price": 299.00,
        "category": "Pizza",
        "rating": 4.5,
        "prep_time": "25-30 mins",
        "image": "🍕",
        "veg": True,
        "bestseller": True
    },
    {
        "id": 2,
        "name": "Chicken Biryani",
        "description": "Aromatic basmati rice with tender chicken pieces",
        "price": 349.00,
        "category": "Biryani",
        "rating": 4.8,
        "prep_time": "35-40 mins",
        "image": "🍛",
        "veg": False,
        "bestseller": True
    },
    {
        "id": 3,
        "name": "Paneer Butter Masala",
        "description": "Creamy tomato-based curry with soft paneer cubes",
        "price": 249.00,
        "category": "North Indian",
        "rating": 4.3,
        "prep_time": "20-25 mins",
        "image": "🍛",
        "veg": True,
        "bestseller": False
    },
    {
        "id": 4,
        "name": "Chicken Burger",
        "description": "Grilled chicken patty with lettuce, tomato & cheese",
        "price": 199.00,
        "category": "Burgers",
        "rating": 4.2,
        "prep_time": "15-20 mins",
        "image": "🍔",
        "veg": False,
        "bestseller": False
    },
    {
        "id": 5,
        "name": "Masala Dosa",
        "description": "Crispy dosa with spiced potato filling & chutneys",
        "price": 149.00,
        "category": "South Indian",
        "rating": 4.6,
        "prep_time": "20-25 mins",
        "image": "🥞",
        "veg": True,
        "bestseller": True
    },
    {
        "id": 6,
        "name": "Chocolate Brownie",
        "description": "Warm chocolate brownie with vanilla ice cream",
        "price": 129.00,
        "category": "Desserts",
        "rating": 4.4,
        "prep_time": "10-15 mins",
        "image": "🍫",
        "veg": True,
        "bestseller": False
    }
]

# 🏪 HEADER SECTION
st.markdown("""
<div class="delivery-header">
    <h1>🍕 FoodFast</h1>
    <p>Delicious food delivered fast to your doorstep</p>
</div>
""", unsafe_allow_html=True)

# 📍 LOCATION BAR
st.markdown("""
<div class="location-bar">
    <b>📍 Delivering to:</b> Your Current Location • <span style="color: #fc8019;">Change Address</span>
</div>
""", unsafe_allow_html=True)

# 🔍 FILTERS AND SEARCH
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    search_query = st.text_input("🔍 Search for dishes or restaurants", placeholder="Try 'Pizza', 'Biryani', 'Dosa'...")

with col2:
    category_filter = st.selectbox("Category", ["All", "Pizza", "Biryani", "North Indian", "Burgers", "South Indian", "Desserts"])

with col3:
    veg_filter = st.selectbox("Preference", ["All", "Veg Only", "Non-Veg Only"])

# 🍽️ FOOD ITEMS DISPLAY
st.markdown("## 🍽️ Available Items")

# Filter items based on user selection
filtered_items = menu_items.copy()

if category_filter != "All":
    filtered_items = [item for item in filtered_items if item["category"] == category_filter]

if veg_filter == "Veg Only":
    filtered_items = [item for item in filtered_items if item["veg"]]
elif veg_filter == "Non-Veg Only":
    filtered_items = [item for item in filtered_items if not item["veg"]]

if search_query:
    filtered_items = [item for item in filtered_items if search_query.lower() in item["name"].lower() or search_query.lower() in item["description"].lower()]

# Display food items in cards
for item in filtered_items:
    tag_class = "bestseller" if item["bestseller"] else "tag"
    tag_text = "BESTSELLER" if item["bestseller"] else ("VEG" if item["veg"] else "NON-VEG")
    
    st.markdown(f"""
    <div class="food-card">
        <div class="tag {tag_class}">{tag_text}</div>
        <div class="food-item-header">
            <div>
                <h3 class="food-name">{item['image']} {item['name']}</h3>
                <div class="food-meta">
                    <div class="rating">★ {item['rating']}</div>
                    <div class="prep-time">⏱️ {item['prep_time']}</div>
                </div>
            </div>
            <h3 class="food-price">₹{item['price']}</h3>
        </div>
        <p class="food-description">{item['description']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Add to cart button
    col1, col2, col3 = st.columns([2, 1, 1])
    with col2:
        if st.button(f"Add to Cart", key=f"add_{item['id']}", help=f"Add {item['name']} to cart"):
            st.session_state.cart.append(item)
            st.session_state.cart_total += item['price']
            st.success(f"✅ {item['name']} added to cart!")
            time.sleep(1)
            st.rerun()

# 🛒 CART DISPLAY (FLOATING)
if st.session_state.cart:
    cart_count = len(st.session_state.cart)
    st.markdown(f"""
    <div class="cart-container" onclick="document.getElementById('cart-section').scrollIntoView();">
        🛒 Cart ({cart_count}) • ₹{st.session_state.cart_total:.0f}
    </div>
    """, unsafe_allow_html=True)

# 💰 CHECKOUT SECTION
if st.session_state.cart:
    st.markdown('<div id="cart-section"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="checkout-section">
        <h2 class="checkout-header">🛒 Your Order</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Display cart items
    for idx, item in enumerate(st.session_state.cart):
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.write(f"**{item['name']}**")
        with col2:
            st.write(f"₹{item['price']}")
        with col3:
            if st.button("Remove", key=f"remove_{idx}"):
                st.session_state.cart_total -= item['price']
                st.session_state.cart.pop(idx)
                st.rerun()
    
    # Bill calculation
    subtotal = st.session_state.cart_total
    delivery_fee = 29.0 if subtotal < 500 else 0.0
    gst = subtotal * 0.05  # 5% GST
    total = subtotal + delivery_fee + gst
    
    st.markdown(f"""
    <div class="bill-item">
        <span>Subtotal</span>
        <span>₹{subtotal:.0f}</span>
    </div>
    <div class="bill-item">
        <span>Delivery Fee</span>
        <span>₹{delivery_fee:.0f}</span>
    </div>
    <div class="bill-item">
        <span>GST (5%)</span>
        <span>₹{gst:.0f}</span>
    </div>
    <div class="bill-total">
        <span>Total Amount</span>
        <span>₹{total:.0f}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Address input
    st.markdown("### 📍 Delivery Address")
    delivery_address = st.text_area("Enter your complete address", placeholder="House No., Street, Area, City, Pincode")
    
    # Payment method
    st.markdown("### 💳 Payment Method")
    payment_method = st.selectbox("Select Payment Method", [
        "💳 Credit/Debit Card", 
        "📱 UPI (GPay/PhonePe/Paytm)", 
        "💰 Cash on Delivery",
        "🏦 Net Banking"
    ])
    
    # Place order button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Place Order", type="primary", use_container_width=True):
            if delivery_address:
                # Generate order ID
                st.session_state.order_id = f"FD{int(datetime.now().timestamp())}"
                st.session_state.order_placed = True
                st.session_state.delivery_address = delivery_address
                
                # Show success message
                st.markdown(f"""
                <div class="order-status">
                    <h2>🎉 Order Placed Successfully!</h2>
                    <p><strong>Order ID:</strong> {st.session_state.order_id}</p>
                    <p><strong>Total:</strong> ₹{total:.0f}</p>
                    <p><strong>Estimated Delivery:</strong> 35-45 minutes</p>
                    <p>📱 You'll receive updates via SMS and email</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Clear cart after order
                st.balloons()
                time.sleep(3)
                st.session_state.cart = []
                st.session_state.cart_total = 0.0
                st.rerun()
            else:
                st.error("⚠️ Please enter your delivery address")

# 📱 ORDER TRACKING
if st.session_state.order_placed and st.session_state.order_id:
    st.markdown("### 📍 Track Your Order")
    
    # Simulated order progress
    progress_steps = [
        "✅ Order Confirmed",
        "👨‍🍳 Preparing your food",
        "🚴 Out for delivery",
        "📦 Delivered"
    ]
    
    current_step = 2  # Simulating current progress
    
    for i, step in enumerate(progress_steps):
        if i <= current_step:
            st.success(step)
        else:
            st.info(step)
    
    st.progress(min(current_step / 3, 1.0))
    st.write("🚴 **Delivery Partner:** Rohit Kumar | 📞 +91 98765 43210")

# 🎯 FOOTER
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 40px 20px; background: #f8f9fa; border-radius: 12px; margin-top:
