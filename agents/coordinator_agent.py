# agents/coordinator_agent.py

"""
This module acts as the central orchestrator for the agentic RAG system.
It coordinates the flow of information between the ingestion, retrieval, and
language model agents to process a user's query and generate a response.
It also handles special commands for system management, such as clearing data.
"""

import os
import shutil
import uuid
from agents.ingestion_agent import handle_message as ingestion_handle_message
from agents.retrieval_agent import handle_message as retrieval_handle_message
from agents.llm_response_agent import handle_message as llm_handle_message
from utils.mcp import create_mcp_message

def empty_directory(directory_path: str):
    """
    Deletes all files and subdirectories within a specified directory,
    leaving the directory itself empty.

    Args:
        directory_path (str): The absolute or relative path to the directory to empty.
    """
    # Guard clause: If the directory doesn't exist, do nothing.
    if not os.path.exists(directory_path):
        return
    
    # Iterate over each item in the directory.
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        try:
            # Check if the item is a file or a symbolic link and delete it.
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            # Check if the item is a subdirectory and delete it recursively.
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            # Print an error message if any item fails to be deleted.
            print(f'Failed to delete {file_path}. Reason: {e}')

def coordinate_chat(question: str, document_path: str) -> str:
    """
    Orchestrates the entire RAG pipeline or handles special system commands.

    This function manages the sequence of agent interactions:
    1. Ingestion: Loads and chunks documents.
    2. Indexing: Adds document chunks to the vector database.
    3. Retrieval: Fetches relevant context for a given question.
    4. Generation: Synthesizes a final answer using an LLM.

    It also intercepts special commands like "CLEAR_ALL_DATA" to manage the system's state.

    Args:
        question (str): The user's query or a special command string.
        document_path (str): The path to the directory containing uploaded documents.

    Returns:
        str: The final answer from the language model or a status message.
    """
    # Generate a unique trace ID to track this entire operation across all agents.
    trace_id = str(uuid.uuid4())

    # Check if the input is a special command for clearing data.
    if question == "CLEAR_ALL_DATA":
        try:
            # Create and send a message to the RetrievalAgent to reset its database.
            reset_msg = create_mcp_message("Coordinator", "RetrievalAgent", "RESET_DATABASE", {}, trace_id)
            retrieval_handle_message(reset_msg)
            
            # Empty the local directory where uploaded documents are stored.
            empty_directory(document_path)
            
            # Return a success message to the user interface.
            return "✅ Successfully cleared all data from the database and document folder."
        except Exception as e:
            # Return an error message if any part of the cleanup fails.
            return f"❌ Error during cleanup: {str(e)}"

    # --- Standard RAG Pipeline ---

    # Step 1: Ingestion
    # Send a message to the IngestionAgent to process the documents.
    ingest_msg = create_mcp_message("Coordinator", "IngestionAgent", "INGEST", {"document_path": document_path}, trace_id)
    ingest_response = ingestion_handle_message(ingest_msg)
    
    # Validate the response from the IngestionAgent.
    if ingest_response.get("status") == "error" or not ingest_response["payload"].get("chunks"):
        return "No documents found to process. Please upload documents first."
        
    # Extract the document chunks from the response payload.
    chunks = ingest_response["payload"]["chunks"]

    # Step 2: Indexing
    # Send the chunks to the RetrievalAgent to be added to the vector database.
    add_msg = create_mcp_message("Coordinator", "RetrievalAgent", "ADD_CHUNKS", {"chunks": chunks}, trace_id)
    # The response from adding chunks is not critical for the flow, so it's ignored.
    _ = retrieval_handle_message(add_msg)

    # Step 3: Retrieval
    # Send the user's question to the RetrievalAgent to find relevant context.
    retrieve_msg = create_mcp_message("Coordinator", "RetrievalAgent", "RETRIEVE", {"question": question}, trace_id)
    retrieve_response = retrieval_handle_message(retrieve_msg)
    # Extract the most relevant chunks (top_chunks) from the response.
    top_chunks = retrieve_response["payload"]["top_chunks"]

    # Step 4: Generation
    # Send the question and the retrieved context to the LLMResponseAgent.
    llm_msg = create_mcp_message("Coordinator", "LLMResponseAgent", "GENERATE_RESPONSE", {"question": question, "top_chunks": top_chunks}, trace_id)
    llm_response = llm_handle_message(llm_msg)

    # Return the final, synthesized response from the language model.
    return llm_response["payload"]["final_response"]