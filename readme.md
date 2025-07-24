# Agentic RAG Chatbot

An agent-based Retrieval-Augmented Generation (RAG) chatbot that answers user queries from uploaded documents using modular agents and the Model Communication Protocol (MCP). Supports multiple file formats and provides context-aware, intelligent responses.

---

## Features

-  Multi-format document ingestion: `PDF`, `DOCX`, `PPTX`, `CSV`, `TXT`, `MD`
-  Agentic architecture using **Model Communication Protocol (MCP)**
-  ChromaDB-based semantic search with `MiniLM` embeddings
-  Natural language responses powered by **Gemini 2.5**
-  Streamlit UI for interactive chat and file uploads
-  Session-based memory reset for consistent responses

---

## Architecture Overview

- **IngestionAgent**: Parses and chunks content from multi-format documents  
- **RetrievalAgent**: Indexes chunks in ChromaDB and retrieves relevant context  
- **LLMResponseAgent**: Formats prompts and communicates with the LLM  
- **CoordinatorAgent**: Orchestrates agents using MCP  
- **Streamlit Frontend**: Enables file upload, clearing, and chat interactions

---

# Tech Stack

| Component        | Technology                                 |
|------------------|--------------------------------------------|
| Language         | Python 3.9+                                |
| Vector Store     | [ChromaDB](https://www.trychroma.com/)     |
| Embeddings       | Sentence Transformers (MiniLM-L6-v2)       |
| LLM              | Gemini 2.5                                 |
| UI Framework     | Streamlit                                  |
| Document Parsing | PyMuPDF, python-docx, python-pptx, pandas  |

---

# Getting Started

### Prerequisites

- Python 3.9+
- Google Gemini API Key stored in a `.env` file

### Installation

Clone the repository:

```bash
git clone https://github.com/your-username/agentic-rag-chatbot.git
cd agentic-rag-chatbot
```

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file and add your API key:

```ini
GEMINI_API_KEY=your_google_gemini_api_key
```

### Run the Application

Start the Streamlit app:

```bash
streamlit run app.py
```

---

## Project Structure

```
agentic-rag-chatbot/
├── agents/                   # Agent implementations
│   ├── ingestion_agent.py    # Document processing
│   ├── retrieval_agent.py    # Vector store operations
│   ├── llm_response_agent.py # LLM interface
│   └── coordinator_agent.py  # Workflow orchestration
├── utils/                    # Utility modules
│   ├── file_loader.py        # Document loading
│   └── mcp.py                # Model Communication Protocol
├── chroma_persistent_storage/ # Vector database
├── app.py                    # Streamlit application
├── main.py                   # CLI testing script
├── .env                      # Environment variables
├── requirements.txt          # Dependencies
└── README.md                 # Project documentation
```
## Acknowledgments

- [ChromaDB](https://www.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [Gemini API by Google AI](https://ai.google.dev/)
- [Streamlit](https://streamlit.io/)
