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

Installation
Clone the repository:

bash
git clone https://github.com/your-username/agentic-rag-chatbot.git
cd agentic-rag-chatbot
Create and activate virtual environment:

bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies:

bash
pip install -r requirements.txt
Create .env file:

ini
GEMINI_API_KEY=your_google_gemini_api_key
Running the Application
Start the Streamlit interface:

bash
streamlit run app.py
📂 Project Structure
text
agentic-rag-chatbot/
├── agents/                   # Agent implementations
│   ├── ingestion_agent.py    # Document processing
│   ├── retrieval_agent.py    # Vector store operations
│   ├── llm_response_agent.py # LLM interface
│   └── coordinator_agent.py  # Workflow orchestration
├── utils/                    # Utility modules
│   ├── file_loader.py        # Document loading
│   └── mcp.py               # Model Communication Protocol
├── chroma_persistent_storage/ # Vector database
├── app.py                    # Streamlit application
├── main.py                   # CLI testing script
├── .env                      # Environment variables
├── requirements.txt          # Dependencies
└── README.md                 # This file