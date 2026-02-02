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

# [Keep all your existing CSS styling code here - same as before]

# 2. CONFIGURE GEMINI API WITH CORRECT MODEL
api_status = "🔴 Offline"
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Use the CORRECT model name - gemini-2.5-flash instead of gemini-pro
    model = genai.GenerativeModel('gemini-2.5-flash')  # ✅ FIXED MODEL NAME
    test_response = model.generate_content("test")
    api_status = "🟢 Online"
except Exception as e:
    st.error(f"🚨 Gemini API Error: {e}")

# [Keep all the rest of your code the same, but ALSO update the model call in the chat section:]

# 12. HANDLE USER INPUT - UPDATED MODEL CALL
if prompt := st.chat_input("🔬 What molecular gastronomy experiment interests you?"):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Add user message to history
    st.session_state.messages.append({"role": "user", "parts": [prompt]})

    # Get response from Gemini with CORRECT MODEL
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')  # ✅ FIXED MODEL NAME
        chat_history = [
            {"role": m["role"], "parts": m["parts"]} 
            for m in st.session_state.messages
        ]
        
        response = model.generate_content(chat_history)
        response_text = response.text
        
        # [Rest of the code remains the same]
