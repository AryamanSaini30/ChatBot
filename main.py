import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from datetime import datetime
import time

# Load API key from .env
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Streamlit page config
st.set_page_config(page_title="☁️ Cloud Cost Optimizer", page_icon="💬")

# Sidebar content
with st.sidebar:
    st.header("📘 Help & Tips")
    st.markdown("""
    Ask me anything about:
    - 💻 EC2 / Azure VM / GCE cost-saving tips
    - 📦 Storage (S3, Blob, GCS)
    - 🗃️ RDS / Azure SQL / BigQuery
    - ⚙️ Auto-scaling, right-sizing
    - 📊 Idle resource cleanup
    - 📉 Monitoring & licensing
    """)
    theme = st.radio("Theme", ["Light", "Dark"])
    if theme == "Dark":
        st.markdown("""
            <style>
                body {
                    background-color: #0e1117;
                    color: white;
                }
            </style>
        """, unsafe_allow_html=True)
    
    if st.button("💾 Export Chat"):
        filename = f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        history = st.session_state.chat.history
        transcript = "\n\n".join([
            f"{msg.role.capitalize()}: {msg.parts[0] if msg.role != 'user' else msg.parts}" for msg in history
        ])
        st.download_button("Download", transcript, file_name=filename)

# Title
st.title("☁️ Cloud Cost Optimizer Chatbot")
st.caption("Ask anything about AWS, Azure, or GCP cloud cost savings!")

# Initialize chat session
if "chat" not in st.session_state:
    model = genai.GenerativeModel("gemini-1.5-pro")
    st.session_state.chat = model.start_chat(history=[
        {
            "role": "model",
            "parts": [
                """
                👋 Welcome to your Cloud Cost Optimization Assistant!

                I'm here to help you reduce cloud costs across AWS, Azure, and GCP.

                You can ask me about:
                - Instance right-sizing
                - Spot vs Reserved instances
                - Storage optimization
                - Identifying idle resources
                - Database cost optimization
                - And much more!

                Let's optimize your cloud spending and make it smarter and more efficient. 🌩️
                """
            ]
        }
    ])

# Display messages
def display_message(role, text, stream=False):
    with st.chat_message(role):
        if stream:
            placeholder = st.empty()
            full_text = ""
            for chunk in text:
                full_text += chunk
                placeholder.markdown(full_text)
                time.sleep(0.01)
        else:
            st.markdown(str(text).strip())

# Show chat history
for msg in st.session_state.chat.history:
    role = msg.role
    text = msg.parts[0] if role == "model" else msg.parts
    display_message(role, text)

# Quick action buttons
st.subheader("⚡ Quick Prompts")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("EC2 Cost Tips"):
        st.session_state.quick_prompt = "Optimize my EC2 usage"
with col2:
    if st.button("Idle Resources"):
        st.session_state.quick_prompt = "Find idle resources across AWS"
with col3:
    if st.button("Storage Costs"):
        st.session_state.quick_prompt = "Reduce cloud storage cost in GCP"

# Get user input
user_input = st.chat_input("Ask your cloud cost question...")
if user_input or "quick_prompt" in st.session_state:
    if not user_input:
        user_input = st.session_state.quick_prompt
        del st.session_state.quick_prompt

    display_message("user", user_input)
    response = st.session_state.chat.send_message(user_input)
    display_message("assistant", response.text, stream=True)
