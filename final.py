import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import pandas as pd # Import pandas

# Load environment variables (API key)
load_dotenv()
# --- Safety Check for API Key ---
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("GEMINI_API_KEY not found. Please set it in your .env file.")
    st.stop() # Stop execution if key is missing
genai.configure(api_key=api_key)
# ---------------------------------

# Set up Streamlit page
st.set_page_config(page_title="☁️ Cloud Cost Optimizer+", page_icon="💸")

# --- Global variable for DataFrame ---
# Use session state to store the dataframe
if 'cost_data_df' not in st.session_state:
    st.session_state.cost_data_df = None
# -------------------------------------

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Settings & Data")

    # File Uploader
    uploaded_file = st.file_uploader("Upload Cloud Cost CSV", type=["csv"])
    if uploaded_file is not None:
        try:
            # Read the CSV into a pandas DataFrame
            st.session_state.cost_data_df = pd.read_csv(uploaded_file)
            st.success("CSV file loaded successfully!")
            # Display basic info in sidebar
            st.write("Data Preview:")
            st.dataframe(st.session_state.cost_data_df.head())
            st.write(f"Shape: {st.session_state.cost_data_df.shape}")
        except Exception as e:
            st.error(f"Error reading CSV: {e}")
            st.session_state.cost_data_df = None # Reset dataframe on error
    elif st.session_state.cost_data_df is not None:
         st.info("Using previously uploaded data. Upload a new file to replace.")
         # Optionally show preview again if needed
         # st.dataframe(st.session_state.cost_data_df.head())


    st.markdown("---") # Separator
    st.header("Chat Settings")
    mode = st.radio("Response Style", ["Brief", "Detailed", "Bullet Points"])
# -------------

# Header
st.title("☁️ Cloud Cost Optimizer Chatbot+")
st.markdown("---")

# Initial system message (updated)
system_message = """
Cloud costs got you down? Let's fix that! 💸

I'm your expert in AWS, Azure, and GCP savings.
**Upload your cost data (CSV) via the sidebar** and ask me questions about it, or ask general cloud cost questions!
"""

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "model", "parts": [system_message.strip()]}]

# Display chat messages cleanly
def display_message(role, text):
    # Ensure text is a string
    if isinstance(text, (list, tuple)) and text: # Handle potential list format from Gemini
         display_text = str(text[0]).strip()
    else:
         display_text = str(text).strip()

    with st.chat_message(role):
        st.markdown(display_text)


# Show past messages
for msg in st.session_state.chat_history:
    # Add basic safety check for message structure
    if isinstance(msg, dict) and "role" in msg and "parts" in msg:
        display_message(msg["role"], msg["parts"]) # Pass the parts directly
    else:
        st.warning(f"Skipping malformed message: {msg}")


# User input
if user_input := st.chat_input("Ask about your data or general cloud costs..."):
    display_message("user", user_input)

    # Add user message to history
    st.session_state.chat_history.append({"role": "user", "parts": [user_input]})

    # --- Prepare prompt for Gemini ---
    # Basic Context Injection (if data exists) - VERY SIMPLIFIED
    context_prompt = user_input
    if st.session_state.cost_data_df is not None:
        # Example: Add column names as context (can be much more sophisticated)
        available_columns = ", ".join(st.session_state.cost_data_df.columns)
        context_prompt = f"""
        Context: User has uploaded cloud cost data with the following columns: {available_columns}.
        User Question (apply {mode.lower()} style): {user_input}
        """
        # !! IMPORTANT: For real analysis, you'd trigger Python functions
        # !! based on the user_input, analyze st.session_state.cost_data_df,
        # !! and then feed the RESULTS to Gemini, possibly using function calling.
        # !! Simply adding column names is NOT enough for real analysis.
    else:
         # Add style preference if no data
         context_prompt = f"Please answer in a {mode.lower()} style: {user_input}"

    # Temporarily adjust the last user message in history for the API call context
    # NOTE: This modifies the history temporarily for the API call.
    # A cleaner approach might involve preparing a separate input for the model.
    original_last_message = st.session_state.chat_history[-1]
    st.session_state.chat_history[-1] = {"role": "user", "parts": [context_prompt]}
    # --------------------------------

    # Send history to Gemini model
    model = genai.GenerativeModel("gemini-1.5-pro") # Or gemini-1.5-flash for potentially faster/cheaper responses
    with st.spinner("Generating response..."):
        try:
            response = model.generate_content(st.session_state.chat_history) # Send modified history

             # --- Restore original user message in history ---
            st.session_state.chat_history[-1] = original_last_message
             # --------------------------------------------

            # Add assistant response to history
            # Ensure 'parts' is always a list, handle potential errors in response structure
            response_text = ""
            if hasattr(response, 'text'):
                 response_text = response.text
            elif hasattr(response, 'parts'):
                 # Assuming parts is iterable and contains text parts
                 response_text = " ".join(str(part) for part in response.parts)

            st.session_state.chat_history.append({"role": "model", "parts": [response_text]}) # Store as model role

            # Show assistant response
            display_message("model", response_text) # Use model role for display

        except Exception as e:
             # --- Restore original user message in history on error ---
            st.session_state.chat_history[-1] = original_last_message
             # -------------------------------------------------------
            st.error(f"An error occurred: {e}")
            # Optionally remove the failed user message from history or add an error message
            # st.session_state.chat_history.pop() # Remove user msg that caused error


# Add an expander for additional info.
with st.expander("ℹ️ Additional Information"):
    st.write("This chatbot can answer general cloud cost questions (AWS, Azure, GCP).")
    st.write("You can also upload a CSV file containing your cloud cost data via the sidebar.")
    st.write("**Note:** The chatbot currently has limited direct analysis capabilities on the uploaded data. Complex data analysis requires further development (e.g., using function calling).")
    st.write("Select a response style from the sidebar to customize the output format.")