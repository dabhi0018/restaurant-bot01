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
    
    /* FILTERS */
    .filter-section {
        background: white;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
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
            <h3 class="food-price">₹
\<Streaming stoppped because the conversation grew too long for this model\>
