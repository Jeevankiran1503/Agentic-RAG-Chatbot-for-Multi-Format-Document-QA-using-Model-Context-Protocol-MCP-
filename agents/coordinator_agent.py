from agents.ingestion_agent import handle_message as ingestion_handle_message
from agents.retrieval_agent import handle_message as retrieval_handle_message
from agents.llm_response_agent import handle_message as llm_handle_message
from utils.mcp import create_mcp_message
import uuid

def coordinate_chat(question, document_path):
    trace_id = str(uuid.uuid4())  

    ingest_msg = create_mcp_message("Coordinator", "IngestionAgent", "INGEST", {"document_path": document_path}, trace_id)
    ingest_response = ingestion_handle_message(ingest_msg)
    chunks = ingest_response["payload"]["chunks"]

    add_msg = create_mcp_message("Coordinator", "RetrievalAgent", "ADD_CHUNKS", {"chunks": chunks}, trace_id)
    _ = retrieval_handle_message(add_msg)

   
    retrieve_msg = create_mcp_message("Coordinator", "RetrievalAgent", "RETRIEVE", {"question": question}, trace_id)
    retrieve_response = retrieval_handle_message(retrieve_msg)
    top_chunks = retrieve_response["payload"]["top_chunks"]

    llm_msg = create_mcp_message("Coordinator", "LLMResponseAgent", "GENERATE_RESPONSE", {"question": question, "top_chunks": top_chunks}, trace_id)
    llm_response = llm_handle_message(llm_msg)

    return llm_response["payload"]["final_response"]
