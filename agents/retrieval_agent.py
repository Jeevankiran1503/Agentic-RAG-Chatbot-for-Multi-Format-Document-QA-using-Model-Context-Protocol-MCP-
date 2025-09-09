# agents/retrieval_agent.py

import chromadb
from chromadb.utils import embedding_functions
# --- MODIFICATION 1: Import the Settings class ---
from chromadb.config import Settings
import shutil
import os
from utils.mcp import create_mcp_message

CHROMA_PATH = "chroma_persistent_storage"
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction("all-MiniLM-L6-v2")

_chroma_client = None
_collection = None

def get_collection():
    global _chroma_client, _collection
    if _collection is None:
        if _chroma_client is None:
            # --- MODIFICATION 2: Enable reset when creating the client ---
            _chroma_client = chromadb.PersistentClient(
                path=CHROMA_PATH,
                settings=Settings(allow_reset=True)
            )
        _collection = _chroma_client.get_or_create_collection(
            name="document_qa_collection",
            embedding_function=embedding_fn
        )
    return _collection

# No changes to the functions below this point
def add_chunks_to_chroma(chunks):
    collection = get_collection()
    ids = [doc["id"] for doc in chunks]
    texts = [doc["text"] for doc in chunks]
    if ids and texts:
        collection.upsert(ids=ids, documents=texts)

def run_retrieval_agent(query, n_results=3):
    collection = get_collection()
    results = collection.query(query_texts=[query], n_results=n_results, include=["documents"])
    return [doc for sublist in results["documents"] for doc in sublist]


def handle_message(mcp_message):
    msg_type = mcp_message["type"]
    trace_id = mcp_message["trace_id"]

    if msg_type == "RESET_DATABASE":
        global _chroma_client, _collection
        
        if _chroma_client:
            # This call will now be allowed
            _chroma_client.reset()
        
        _chroma_client = None
        _collection = None
        
        return create_mcp_message(
            sender="RetrievalAgent",
            receiver=mcp_message["sender"],
            type_="DATABASE_RESET_SUCCESS",
            payload={"status": "SUCCESS"},
            trace_id=trace_id
        )

    elif msg_type == "ADD_CHUNKS":
        chunks = mcp_message["payload"]["chunks"]
        add_chunks_to_chroma(chunks)
        return create_mcp_message("RetrievalAgent", mcp_message["sender"], "CHUNKS_ADDED", {"count": len(chunks)}, trace_id)

    elif msg_type == "RETRIEVE":
        query = mcp_message["payload"]["question"]
        n_results = mcp_message["payload"].get("n_results", 3)
        top_chunks = run_retrieval_agent(query, n_results)
        return create_mcp_message("RetrievalAgent", mcp_message["sender"], "CONTEXT_RESPONSE", {"top_chunks": top_chunks, "query": query}, trace_id)

    else:
        raise ValueError(f"Unsupported message type: {msg_type}")