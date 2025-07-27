import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import time
import pandas as pd

# Load environment variables (API key)
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("GEMINI_API_KEY not found in environment variables. Please set it.")
    st.stop()
genai.configure(api_key=api_key)

# Streamlit page configuration
st.set_page_config(page_title="☁️ Cloud Cost Optimizer", page_icon="💸")

# Sidebar for settings
with st.sidebar:
    st.header("Settings")
    mode = st.radio("Response Style", ["Brief", "Detailed"])
    if st.button("Clear Chat"):
        st.session_state.chat_history = [{"role": "model", "parts": ["Cloud costs got you down? Let's fix that! 💸\n\nI'm your expert in AWS, Azure, and GCP savings. Ask away!"]}] # reset chat
        st.rerun() #force rerun so chat is cleared.
    uploaded_file = st.file_uploader("Upload CSV for Cost Analysis", type=["csv"])

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

# Show past messages
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(str(msg["parts"][0]).strip())

# User input
if user_input := st.chat_input("Ask your cloud cost question..."):
    with st.chat_message("user"):
        st.markdown(user_input)

    modified_user_input = f"{user_input}. Please provide the response in a {mode.lower()} style."
    st.session_state.chat_history.append({"role": "user", "parts": [modified_user_input]})
    history_for_api = list(st.session_state.chat_history)

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            csv_content = df.to_csv(index=False)
            history_for_api.append({"role": "user", "parts": [f"Here is the data from the uploaded CSV: \n{csv_content}"]}) #send csv data along with the prompt
        except Exception as e:
            st.error(f"Error processing CSV: {e}")

    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        response_stream = model.generate_content(
            history_for_api,
            generation_config=genai.types.GenerationConfig(),
            stream=True,
        )

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response_content = ""
            displayed_text = ""
            char_delay = 0.01

            for chunk in response_stream:
                chunk_text = ""
                try:
                    chunk_text = chunk.text
                except Exception as e:
                    pass

                if chunk_text:
                    for char in chunk_text:
                        displayed_text += char
                        message_placeholder.markdown(displayed_text + "▌")
                        time.sleep(char_delay)
                    full_response_content += chunk_text

            message_placeholder.markdown(full_response_content)
            if full_response_content:
                st.session_state.chat_history.append({"role": "assistant", "parts": [full_response_content]})

    except Exception as e:
        st.error(f"An error occurred during generation: {e}")
        error_message = f"Sorry, I encountered an error: {e}"
        st.session_state.chat_history.append({"role": "assistant", "parts": [error_message]})
        with st.chat_message("assistant"):
            st.error(error_message)

char_delay = 0.01
with st.expander("Additional Information"):
    st.write("This chatbot is designed to help you optimize your cloud costs across AWS, Azure, and GCP.")
    st.write("Select a response style from the sidebar to customize the output.")
    st.write(f"Typing speed delay: {char_delay * 1000} ms per character.")