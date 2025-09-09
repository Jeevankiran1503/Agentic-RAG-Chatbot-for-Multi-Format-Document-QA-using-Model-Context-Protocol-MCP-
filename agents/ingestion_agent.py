# agents/ingestion_agent.py

"""
This module is responsible for the first stage of the RAG pipeline: ingestion.
It takes a path to a directory of documents, loads their content, and splits
them into smaller, more manageable text chunks suitable for embedding and retrieval.
"""

import uuid
from utils.file_loader import load_documents, basic_chunk_by_paragraph
from utils.mcp import create_mcp_message

def run_ingestion_agent(document_path: str) -> list[dict]:
    """
    Loads all documents from a given path and chunks them into a structured list.

    Args:
        document_path (str): The path to the directory containing documents.

    Returns:
        list[dict]: A list of chunk dictionaries, where each dictionary contains a
                    unique 'id' and the chunk 'text'.
    """
    # Load the raw text content from all supported files in the specified directory.
    documents = load_documents(document_path)
    
    # Initialize an empty list to store all chunks from all documents.
    all_chunks = []

    # Process each loaded document one by one.
    for doc_text in documents:
        # Split the document's text into chunks based on paragraphs.
        chunks = basic_chunk_by_paragraph(doc_text)
        
        # Process each chunk individually.
        for chunk in chunks:
            # Create a dictionary for the chunk, giving it a unique ID and its text content.
            chunk_dict = {
                "id": str(uuid.uuid4()),
                "text": chunk
            }
            # Add the structured chunk dictionary to the master list.
            all_chunks.append(chunk_dict)

    # Return the complete list of chunks.
    return all_chunks

def handle_message(mcp_message: dict) -> dict:
    """
    Acts as the public interface for the Ingestion Agent, handling incoming messages.

    It processes messages of type "INGEST" by running the ingestion pipeline and
    returning the resulting chunks in a new message.

    Args:
        mcp_message (dict): A message dictionary following the Message Communication Protocol.

    Returns:
        dict: A response message containing the processed chunks.
    
    Raises:
        ValueError: If the message type is unknown or unsupported.
    """
    # Check if the message is an "INGEST" request.
    if mcp_message["type"] == "INGEST":
        # Extract the document path from the message payload.
        document_path = mcp_message["payload"]["document_path"]
        
        # Execute the core ingestion logic to get the document chunks.
        chunks = run_ingestion_agent(document_path)
        
        # Create and return a response message containing the chunks.
        return create_mcp_message(
            sender="IngestionAgent",
            receiver=mcp_message["sender"],
            type_="INGESTION_COMPLETE", # Type indicates the operation was successful.
            payload={"chunks": chunks},
            trace_id=mcp_message["trace_id"]
        )
    else:
        # If the message type is not "INGEST", raise an error.
        raise ValueError(f"Unknown message type: {mcp_message['type']}")