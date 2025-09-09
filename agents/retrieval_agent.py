# agents/retrieval_agent.py

"""
This module serves as the memory and search component of the RAG system.
It manages all interactions with the ChromaDB vector database, including:
- Creating and managing a persistent client connection.
- Indexing (embedding and storing) document chunks.
- Retrieving relevant document chunks based on a query's semantic similarity.
- Handling database lifecycle commands, such as resetting the database.
"""

import chromadb
from chromadb.utils import embedding_functions
from chromadb.config import Settings
import shutil
import os
from utils.mcp import create_mcp_message

# --- Configuration and Constants ---

# Define the file path for ChromaDB's persistent storage.
CHROMA_PATH = "chroma_persistent_storage"
# Specify the sentence-transformer model to be used for creating embeddings (vectors).
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction("all-MiniLM-L6-v2")

# --- Singleton State Management ---

# These global-like variables will hold the single instance of the client and collection
# to prevent multiple connections and potential file-locking issues.
_chroma_client = None
_collection = None

def get_collection():
    """
    Retrieves the singleton instance of the ChromaDB collection.

    This function implements the Singleton Pattern. It ensures that only one
    instance of the ChromaDB client and collection is created during the
    application's lifecycle, which is crucial for managing the connection
    to the persistent database file safely and efficiently.

    Returns:
        chromadb.Collection: The singleton collection object.
    """
    global _chroma_client, _collection
    
    # If the collection object has not been created yet...
    if _collection is None:
        # And if the client object has not been created yet...
        if _chroma_client is None:
            # Create the persistent client instance.
            _chroma_client = chromadb.PersistentClient(
                path=CHROMA_PATH,
                # Pass a settings object to enable the .reset() method.
                # This is a security feature to prevent accidental data loss.
                settings=Settings(allow_reset=True)
            )
        # Using the client, get or create the collection for our documents.
        _collection = _chroma_client.get_or_create_collection(
            name="document_qa_collection",
            embedding_function=embedding_fn
        )
    # Return the existing or newly created collection object.
    return _collection

# --- Core Logic Functions ---

def add_chunks_to_chroma(chunks: list[dict]):
    """
    Adds or updates a list of document chunks in the ChromaDB collection.

    Args:
        chunks (list[dict]): A list of dictionaries, where each dictionary
                             represents a chunk with an 'id' and 'text'.
    """
    collection = get_collection()
    # Extract the IDs and text content from the list of chunk dictionaries.
    ids = [doc["id"] for doc in chunks]
    texts = [doc["text"] for doc in chunks]
    
    # Ensure there is data to process before calling the database.
    if ids and texts:
        # Use 'upsert' to add new chunks or update existing ones with the same ID.
        # This is safer than 'add' as it prevents errors on duplicate IDs.
        collection.upsert(ids=ids, documents=texts)

def run_retrieval_agent(query: str, n_results: int = 3) -> list[str]:
    """
    Performs a semantic search to find the most relevant document chunks for a query.

    Args:
        query (str): The user's question or search term.
        n_results (int): The maximum number of relevant chunks to retrieve.

    Returns:
        list[str]: A list of the text content of the most relevant chunks.
    """
    collection = get_collection()
    # Query the collection for chunks that are semantically similar to the input query.
    results = collection.query(
        query_texts=[query], 
        n_results=n_results, 
        include=["documents"]
    )
    # The results are returned in a nested list; this flattens it.
    return [doc for sublist in results["documents"] for doc in sublist]

# --- Message Handling ---

def handle_message(mcp_message: dict) -> dict:
    """
    Acts as the public interface for the Retrieval Agent, handling incoming messages.

    Routes messages to the appropriate function based on their type.

    Args:
        mcp_message (dict): A message dictionary following the Message Communication Protocol.

    Returns:
        dict: A response message with the result of the requested operation.
    """
    msg_type = mcp_message["type"]
    trace_id = mcp_message["trace_id"]

    # Route: Handles requests to clear the entire database.
    if msg_type == "RESET_DATABASE":
        global _chroma_client, _collection
        
        # If a client instance exists, call its reset method.
        if _chroma_client:
            _chroma_client.reset()
        
        # Set the singleton variables back to None to ensure a fresh start
        # on the next operation and to release the old connection.
        _chroma_client = None
        _collection = None
        
        # Return a success message.
        return create_mcp_message(
            sender="RetrievalAgent",
            receiver=mcp_message["sender"],
            type_="DATABASE_RESET_SUCCESS",
            payload={"status": "SUCCESS"},
            trace_id=trace_id
        )

    # Route: Handles requests to add new document chunks to the database.
    elif msg_type == "ADD_CHUNKS":
        chunks = mcp_message["payload"]["chunks"]
        add_chunks_to_chroma(chunks)
        # Return a confirmation message with the count of added chunks.
        return create_mcp_message("RetrievalAgent", mcp_message["sender"], "CHUNKS_ADDED", {"count": len(chunks)}, trace_id)

    # Route: Handles requests to retrieve relevant context for a query.
    elif msg_type == "RETRIEVE":
        query = mcp_message["payload"]["question"]
        n_results = mcp_message["payload"].get("n_results", 3)
        top_chunks = run_retrieval_agent(query, n_results)
        # Return the retrieved chunks in the message payload.
        return create_mcp_message("RetrievalAgent", mcp_message["sender"], "CONTEXT_RESPONSE", {"top_chunks": top_chunks, "query": query}, trace_id)

    # Fallback for any unsupported message types.
    else:
        raise ValueError(f"Unsupported message type: {msg_type}")