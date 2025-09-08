
import chromadb
from chromadb.utils import embedding_functions
import shutil
import os
from utils.mcp import create_mcp_message

CHROMA_PATH = "chroma_persistent_storage"
if os.path.exists(CHROMA_PATH):
    shutil.rmtree(CHROMA_PATH)  

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction("all-MiniLM-L6-v2")
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection(
    name="document_qa_collection",
    embedding_function=embedding_fn
)

def add_chunks_to_chroma(chunks):
    ids = [doc["id"] for doc in chunks]
    texts = [doc["text"] for doc in chunks]
    if ids and texts:
        collection.add(ids=ids, documents=texts)

def run_retrieval_agent(query, n_results=3):
    results = collection.query(query_texts=[query], n_results=n_results, include=["documents"])
    return [doc for sublist in results["documents"] for doc in sublist]



    msg_type = mcp_message["type"]
    trace_id = mcp_message["trace_id"]

    if msg_type == "ADD_CHUNKS":
        chunks = mcp_message["payload"]["chunks"]
        add_chunks_to_chroma(chunks)
        return create_mcp_message(
            sender="RetrievalAgent",
            receiver=mcp_message["sender"],
            msg_type="CHUNKS_ADDED",
            payload={"count": len(chunks)},
            trace_id=trace_id
        )

    elif msg_type == "RETRIEVE":
        query = mcp_message["payload"]["question"]
        n_results = mcp_message["payload"].get("n_results", 3)
        top_chunks = run_retrieval_agent(query, n_results)
        return create_mcp_message(
            sender="RetrievalAgent",
            receiver=mcp_message["sender"],
            msg_type="CONTEXT_RESPONSE",
            payload={"top_chunks": top_chunks, "query": query},
            trace_id=trace_id
        )

    else:
        raise ValueError(f"Unsupported message type: {msg_type}")
