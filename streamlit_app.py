import streamlit as st
import google.generativeai as genai
import os
import json

# Configure page settings
st.set_page_config(
    page_title="WhatsApp Food Order Generator",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to make it look a bit nicer
st.markdown("""
<style>
    .stTextArea textarea {
        font-size: 14px;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E293B;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #334155;
        margin-top: 1rem;
    }
    .info-box {
        background-color: #EFF6FF;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #BFDBFE;
        color: #1E40AF;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    if 'menu_items' not in st.session_state:
        st.session_state.menu_items = [
            {"name": "Cheesy Smash Burger", "price": "$12"},
            {"name": "Pepperoni Pizza XL", "price": "$18"},
            {"name": "Truffle Fries", "price": "$8"}
        ]
    if 'generated_content' not in st.session_state:
        st.session_state.generated_content = None

init_session_state()

# Sidebar Configuration
with st.sidebar:
    st.header("🏪 Restaurant Config")
    
    restaurant_name = st.text_input("Restaurant Name", value="Burger & Bites")
    cuisine = st.text_input("Cuisine / Vibe", value="American Fast Food")
    upi_id = st.text_input("UPI ID / Payment Link", value="9876543210@upi")
    
    st.divider()
    
    st.subheader("📋 Menu Items")
    
    # Simple form to add items
    with st.form("add_item_form", clear_on_submit=True):
        c1, c2 = st.columns([2, 1])
        new_name = c1.text_input("Item Name")
        new_price = c2.text_input("Price")
        submitted = st.form_submit_button("Add Item")
        if submitted and new_name and new_price:
            st.session_state.menu_items.append({"name": new_name, "price": new_price})
            st.rerun()

    # List items with delete button
    if st.session_state.menu_items:
        st.write("Current Menu:")
        for i, item in enumerate(st.session_state.menu_items):
            col1, col2 = st.columns([4, 1])
            col1.text(f"{item['name']} - {item['price']}")
            if col2.button("🗑️", key=f"del_{i}"):
                st.session_state.menu_items.pop(i)
                st.rerun()
    else:
        st.warning("No items in menu!")

    st.divider()
    tone = st.selectbox("Tone", ["Fun & Hungry", "Polite & Professional", "Luxury & Minimal"], index=0)

# Main Content
st.markdown('<div class="main-header">🍔 WhatsApp Chef</div>', unsafe_allow_html=True)
st.markdown("Generate perfect, emoji-rich scripts for your manual ordering system.")

# Check for API Key
api_key = os.environ.get("API_KEY")
if not api_key:
    st.warning("⚠️ API_KEY not found in environment variables. Please check your settings.")
    # Fallback for manual entry if needed, though strictly we should rely on env
    api_key = st.text_input("Or enter your Google API Key manually:", type="password")

if st.button("✨ Generate WhatsApp Copy", type="primary", use_container_width=True):
    if not api_key:
        st.error("Please provide a valid API Key to proceed.")
    elif not st.session_state.menu_items:
        st.error("Please add at least one menu item.")
    else:
        try:
            genai.configure(api_key=api_key)
            # Using the model specified in instructions suitable for text tasks
            model = genai.GenerativeModel('gemini-3-flash-preview')

            menu_string = "\n".join([f"- {item['name']} ({item['price']})" for item in st.session_state.menu_items])

            prompt = f"""
            Act as a professional Restaurant Manager and Copywriter.
            I need you to write 3 specific text blocks formatted effectively for WhatsApp (using Bold *, Italics _, and Emojis).
            
            Restaurant Name: {restaurant_name}
            Cuisine/Vibe: {cuisine}
            Tone: {tone} (Make it {tone.lower()})
            UPI/Payment Info: {upi_id}

            Menu Items to Feature:
            {menu_string}

            Requirements:
            1. **Welcome & Menu Message**: A friendly greeting. A clear list of the provided food items. Call to action: "Reply with your order!".
            2. **Bill & Payment Template**: A template with placeholders like [ITEM 1], [ITEM 2], and [TOTAL PRICE]. Polite request for screenshot. Include the UPI ID: {upi_id}.
            3. **Order Sent to Kitchen Message**: Confirmation that order is received. Estimated time (15-20 mins).
            
            Ensure strict WhatsApp formatting:
            - Use *text* for bold.
            - Use _text_ for italics.
            - Use plenty of appetizing emojis.

            Return the response in JSON format with keys: 'welcome', 'bill', 'kitchen'.
            """

            with st.spinner("Chef is cooking up your scripts... 🍳"):
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        response_mime_type="application/json"
                    )
                )
                
                try:
                    content = json.loads(response.text)
                    st.session_state.generated_content = content
                    st.success("Scripts generated successfully!")
                except json.JSONDecodeError:
                    st.error("Error parsing the response. Please try again.")
                    st.write(response.text)
                    
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Display Results
if st.session_state.generated_content:
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="sub-header">👋 Welcome</div>', unsafe_allow_html=True)
        st.caption("Auto-reply for new messages")
        st.text_area("Copy this:", value=st.session_state.generated_content.get('welcome', ''), height=300)
        
    with col2:
        st.markdown('<div class="sub-header">💸 Bill Template</div>', unsafe_allow_html=True)
        st.caption("Paste and edit for each order")
        st.text_area("Copy this:", value=st.session_state.generated_content.get('bill', ''), height=300)
        
    with col3:
        st.markdown('<div class="sub-header">🍳 Kitchen</div>', unsafe_allow_html=True)
        st.caption("Confirmation message")
        st.text_area("Copy this:", value=st.session_state.generated_content.get('kitchen', ''), height=300)

    st.markdown("""
    <div class="info-box">
        <strong>💡 Pro Tip:</strong> Copy these strings into your Python/Twilio bot code as string templates!
    </div>
    """, unsafe_allow_html=True)
