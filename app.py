import streamlit as st
import os
import shutil
from agents.coordinator_agent import coordinate_chat

UPLOAD_DIR = "./Documents"

# Page Config
st.set_page_config(page_title="Agentic RAG Chatbot", layout="centered")

st.title("Agentic RAG Chatbot")
st.markdown("Upload documents and ask questions based on their content.")


# --- MODIFICATION 1: Initialize a key for the uploader in session state ---
# We will use this to force the widget to re-render.
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0


def clear_data_callback():
    """
    Clears all backend data and resets the file uploader.
    """
    response = coordinate_chat("CLEAR_ALL_DATA", UPLOAD_DIR)
    st.session_state.chat_history = []
    
    # --- MODIFICATION 2: Increment the key to reset the file uploader ---
    # This is the crucial fix. Changing the key makes Streamlit create a new widget.
    st.session_state.uploader_key += 1
    
    st.sidebar.success(response)


# --- Sidebar ---
st.sidebar.header("📁 Upload Files")

# --- MODIFICATION 3: Use the dynamic key from session state ---
uploaded_files = st.sidebar.file_uploader(
    "Upload one or more documents:",
    type=["pdf", "docx", "pptx", "csv", "txt", "md"],
    accept_multiple_files=True,
    key=st.session_state.uploader_key
)

st.sidebar.button("🗑️ Clear All Data", on_click=clear_data_callback)


# --- File Upload Logic (no changes here) ---
if uploaded_files:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    for file in uploaded_files:
        with open(os.path.join(UPLOAD_DIR, file.name), "wb") as f:
            f.write(file.getbuffer())
    st.sidebar.success(f"{len(uploaded_files)} file(s) processed!")


# --- Main Chat Interface (no changes here) ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if os.path.exists(UPLOAD_DIR) and os.listdir(UPLOAD_DIR):
    if question := st.chat_input("Ask your question about the documents..."):
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("bot"):
            with st.spinner("Thinking..."):
                answer = coordinate_chat(question, UPLOAD_DIR)
                st.markdown(answer)
        
        st.session_state.chat_history.append({"role": "bot", "content": answer})
else:
    st.info("Upload one or more documents to begin chatting.")