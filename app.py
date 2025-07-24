import streamlit as st
import os
import shutil
from agents.coordinator_agent import coordinate_chat

UPLOAD_DIR = "./Documents"

# Page Config
st.set_page_config(page_title="Agentic RAG Chatbot", layout="centered")

st.title("Agentic RAG Chatbot")
st.markdown("Upload documents and ask questions based on their content.")


st.sidebar.header("📁 Upload Files")

uploaded_files = st.sidebar.file_uploader(
    "Upload one or more documents:",
    type=["pdf", "docx", "pptx", "csv", "txt", "md"],
    accept_multiple_files=True
)


if st.sidebar.button("🗑️ Clear Uploaded Files"):
    if os.path.exists(UPLOAD_DIR):
        shutil.rmtree(UPLOAD_DIR)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    st.sidebar.success("Cleared uploaded documents.")


if uploaded_files:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    for file in uploaded_files:
        with open(os.path.join(UPLOAD_DIR, file.name), "wb") as f:
            f.write(file.getbuffer())
    st.sidebar.success("Files uploaded successfully!")


if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if os.path.exists(UPLOAD_DIR) and os.listdir(UPLOAD_DIR):
    question = st.text_input("Ask your question about the uploaded documents:", key="user_input")

    if st.button("🔍 Ask"):
        if question:
            st.session_state.chat_history.append({"role": "user", "content": question})
            with st.spinner("Processing..."):
                answer = coordinate_chat(question, UPLOAD_DIR)
            st.session_state.chat_history.append({"role": "bot", "content": answer})
        else:
            st.warning("Please enter a question.")

    
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(f"**Bot:** {msg['content']}")
else:
    st.info("Upload one or more documents to begin chatting.")
