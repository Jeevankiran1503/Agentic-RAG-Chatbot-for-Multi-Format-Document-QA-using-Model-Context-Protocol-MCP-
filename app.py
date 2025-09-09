# app.py

"""
This script launches the web-based user interface for the Agentic RAG Chatbot
using the Streamlit library. It handles file uploads, displays the chat history,
and captures user input. All backend processing is delegated to the
`coordinate_chat` function in the coordinator agent.
"""

import streamlit as st
import os
from agents.coordinator_agent import coordinate_chat

# Define a constant for the directory where uploaded files will be temporarily stored.
UPLOAD_DIR = "./Documents"

# --- Page Configuration ---
# Set the title, icon, and layout for the browser tab and page.
st.set_page_config(page_title="Agentic RAG Chatbot", layout="centered")

# Display the main title and a brief description on the page.
st.title("Agentic RAG Chatbot")
st.markdown("Upload documents and ask questions based on their content.")


# --- State Management and Callbacks ---

# Initialize a key in the session state for the file uploader.
# This is part of the "dynamic key trick" to programmatically reset the widget.
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

def clear_data_callback():
    """
    Callback function executed when the 'Clear All Data' button is clicked.
    It orchestrates the clearing of backend data and resets the UI state.
    """
    # Send a command to the coordinator agent to clear the database and document folder.
    response = coordinate_chat("CLEAR_ALL_DATA", UPLOAD_DIR)
    
    # Reset the chat history stored in the session state.
    st.session_state.chat_history = []
    
    # Increment the uploader's key. This forces Streamlit to create a new
    # file uploader widget on the next rerun, effectively clearing its state.
    st.session_state.uploader_key += 1
    
    # Display the success message from the backend in the sidebar.
    st.sidebar.success(response)


# --- Sidebar UI Elements ---

st.sidebar.header("📁 Upload Files")

# Create the file uploader widget in the sidebar.
uploaded_files = st.sidebar.file_uploader(
    "Upload one or more documents:",
    type=["pdf", "docx", "pptx", "csv", "txt", "md"],
    accept_multiple_files=True,
    # The key is dynamically set from the session state. Changing this key's
    # value will cause the widget to reset.
    key=st.session_state.uploader_key
)

# Create the button to clear all data, linking it to the callback function.
st.sidebar.button("🗑️ Clear All Data", on_click=clear_data_callback)


# --- File Processing Logic ---

# This block executes only if the user has uploaded files in the widget.
if uploaded_files:
    # Ensure the target directory for uploads exists.
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    # Loop through each uploaded file object.
    for file in uploaded_files:
        # Open a new file in binary write mode and save the uploaded content.
        with open(os.path.join(UPLOAD_DIR, file.name), "wb") as f:
            f.write(file.getbuffer())
    # Provide feedback to the user in the sidebar.
    st.sidebar.success(f"{len(uploaded_files)} file(s) processed!")


# --- Main Chat Interface ---

# Initialize the chat history in the session state if it doesn't exist.
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display the past conversation messages from the chat history on every rerun.
for msg in st.session_state.chat_history:
    # Use st.chat_message to create distinct message bubbles for "user" and "bot".
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Only display the chat input box if documents have been uploaded and exist on disk.
if os.path.exists(UPLOAD_DIR) and os.listdir(UPLOAD_DIR):
    # Create the chat input widget at the bottom of the page.
    if question := st.chat_input("Ask your question about the documents..."):
        # Add the user's new message to the chat history.
        st.session_state.chat_history.append({"role": "user", "content": question})
        # Display the user's new message immediately in the chat interface.
        with st.chat_message("user"):
            st.markdown(question)

        # Display the bot's response bubble with a loading spinner.
        with st.chat_message("bot"):
            with st.spinner("Thinking..."):
                # Call the backend coordinator to get the answer.
                answer = coordinate_chat(question, UPLOAD_DIR)
                # Display the answer from the bot.
                st.markdown(answer)
        
        # Add the bot's new message to the chat history.
        st.session_state.chat_history.append({"role": "bot", "content": answer})
else:
    # If no documents are uploaded, display an informational message.
    st.info("Upload one or more documents to begin chatting.")