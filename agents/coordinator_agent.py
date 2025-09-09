# agents/coordinator_agent.py

import os
import shutil
import uuid
from agents.ingestion_agent import handle_message as ingestion_handle_message
from agents.retrieval_agent import handle_message as retrieval_handle_message
from agents.llm_response_agent import handle_message as llm_handle_message
from utils.mcp import create_mcp_message

def empty_directory(directory_path):
    """Deletes all files and subdirectories within a given directory."""
    if not os.path.exists(directory_path):
        return
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

def coordinate_chat(question: str, document_path: str):
    trace_id = str(uuid.uuid4())

    if question == "CLEAR_ALL_DATA":
        try:
            # --- MODIFICATION: Send the graceful reset command ---
            reset_msg = create_mcp_message("Coordinator", "RetrievalAgent", "RESET_DATABASE", {}, trace_id)
            retrieval_handle_message(reset_msg)
            
            # --- MODIFICATION: Empty the document folder instead of deleting it ---
            empty_directory(document_path)
            
            return "✅ Successfully cleared all data from the database and document folder."
        except Exception as e:
            return f"❌ Error during cleanup: {str(e)}"

    # --- Your Existing RAG Pipeline (No changes needed below) ---
    
    ingest_msg = create_mcp_message("Coordinator", "IngestionAgent", "INGEST", {"document_path": document_path}, trace_id)
    ingest_response = ingestion_handle_message(ingest_msg)
    
    if ingest_response.get("status") == "error" or not ingest_response["payload"].get("chunks"):
        return "No documents found to process. Please upload documents first."
        
    chunks = ingest_response["payload"]["chunks"]

    add_msg = create_mcp_message("Coordinator", "RetrievalAgent", "ADD_CHUNKS", {"chunks": chunks}, trace_id)
    _ = retrieval_handle_message(add_msg)

    retrieve_msg = create_mcp_message("Coordinator", "RetrievalAgent", "RETRIEVE", {"question": question}, trace_id)
    retrieve_response = retrieval_handle_message(retrieve_msg)
    top_chunks = retrieve_response["payload"]["top_chunks"]

    llm_msg = create_mcp_message("Coordinator", "LLMResponseAgent", "GENERATE_RESPONSE", {"question": question, "top_chunks": top_chunks}, trace_id)
    llm_response = llm_handle_message(llm_msg)

    return llm_response["payload"]["final_response"]