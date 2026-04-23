import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables (API key)
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Set up Streamlit page
st.set_page_config(page_title="☁️ Cloud Cost Optimizer", page_icon="💸")

# Sidebar for settings
with st.sidebar:
    st.header("Settings")
    mode = st.radio("Response Style", ["Brief", "Detailed", "Bullet Points"])

# Header
st.title("☁️ Cloud Cost Optimizer Chatbot")
st.markdown("---")

# Initial system message
system_message = """
Cloud costs got you down? Let's fix that! 💸

I'm your expert in AWS, Azure, and GCP savings. Ask away!
"""

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "model", "parts": [system_message.strip()]}]

# Display chat messages cleanly
def display_message(role, text):
    with st.chat_message(role):
        st.markdown(str(text).strip())

# Show past messages
for msg in st.session_state.chat_history:
    display_message(msg["role"], msg["parts"][0])

# User input
if user_input := st.chat_input("Ask your cloud cost question..."):
    display_message("user", user_input)

    # Add user message to history
    st.session_state.chat_history.append({"role": "user", "parts": [user_input]})

    # Format prompt with selected mode
    formatted_prompt = f"Answer in a {mode.lower()} style:\n{user_input}"

    # Send entire history
    model = genai.GenerativeModel("gemini-1.5-pro")
    with st.spinner("Generating response..."):
        response = model.generate_content(st.session_state.chat_history)

    # Add assistant response to history
    st.session_state.chat_history.append({"role": "assistant", "parts": [response.text]})

    # Show assistant response
    display_message("assistant", response.text)

# Add an expander for additional info.
with st.expander("Additional Information"):
    st.write("This chatbot is designed to help you optimize your cloud costs across AWS, Azure, and GCP.")
    st.write("Select a response style from the sidebar to customize the output.")