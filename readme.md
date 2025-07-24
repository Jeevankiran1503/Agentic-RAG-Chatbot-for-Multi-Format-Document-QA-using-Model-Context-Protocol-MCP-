# Agentic RAG Chatbot

This project is an agent-based Retrieval-Augmented Generation (RAG) chatbot that answers questions from user-uploaded documents using a modular architecture and agent coordination protocol (MCP). It supports multiple file formats and delivers intelligent, context-aware responses.

---

## Features

- Multi-format document ingestion: PDF, DOCX, PPTX, CSV, TXT, MD
- Agentic architecture using Model Communication Protocol (MCP)
- ChromaDB-based semantic search with MiniLM embeddings
- Gemini 2.5 for natural language response generation
- Streamlit UI for file upload and interactive chat
- Session-based memory reset for consistent results

---

## Architecture Overview

- **IngestionAgent**: Parses multi-format documents and chunks content
- **RetrievalAgent**: Adds chunks to ChromaDB and retrieves relevant context
- **LLMResponseAgent**: Formats the prompt and communicates with the LLM
- **CoordinatorAgent**: Manages interaction between agents using MCP
- **Streamlit Frontend**: Enables file uploads, clearing files, and chatting with the system

---

## Tech Stack

| Component        | Technology                                 |
|------------------|--------------------------------------------|
| Language         | Python 3.9+                                |
| Vector Store     | [ChromaDB](https://www.trychroma.com/)     |
| Embeddings       | Sentence Transformers (MiniLM-L6-v2)       |
| LLM              | Gemini 2.5                                 |
| UI Framework     | Streamlit                                  |
| Document Parsing | PyMuPDF, python-docx, python-pptx, pandas  |

---

## Getting Started

### Prerequisites

- Python 3.9+
- A valid Google Gemini API key (stored in a `.env` file as `GEMINI_API_KEY`)

### Installation

1. Clone the repository

   ```bash
   git clone https://github.com/your-username/agentic-rag-chatbot.git
   cd agentic-rag-chatbot
Create a virtual environment

bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies

bash
Copy
Edit
pip install -r requirements.txt
Add your .env file

ini
Copy
Edit
GEMINI_API_KEY=your_google_gemini_api_key
Running the App
To start the Streamlit chatbot UI:

bash
Copy
Edit
streamlit run app.py
This will open the chatbot in your browser. You can upload documents, ask questions, and get intelligent answers.

Folder Structure
bash
Copy
Edit
├── agents/
│   ├── ingestion_agent.py
│   ├── retrieval_agent.py
│   ├── llm_response_agent.py
│   └── coordinator_agent.py
├── utils/
│   ├── file_loader.py
│   └── mcp.py
├── chroma_persistent_storage/
├── app.py               # Streamlit frontend
├── main.py              # Script for local testing
├── .env
├── requirements.txt
└── README.md
