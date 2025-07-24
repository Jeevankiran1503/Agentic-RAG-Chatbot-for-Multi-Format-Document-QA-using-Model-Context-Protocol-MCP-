import uuid
from utils.file_loader import load_documents, basic_chunk_by_paragraph

def create_mcp_message(sender, receiver, type_, payload, trace_id=None):
    return {
        "sender": sender,
        "receiver": receiver,
        "type": type_,
        "trace_id": trace_id,
        "payload": payload
    }

def run_ingestion_agent(document_path):
    documents = load_documents(document_path)
    all_chunks = []

    for doc_text in documents:
        chunks = basic_chunk_by_paragraph(doc_text)
        for chunk in chunks:
            chunk_dict = {
                "id": str(uuid.uuid4()),
                "text": chunk
            }
            all_chunks.append(chunk_dict)

    return all_chunks

def handle_message(mcp_message):
    if mcp_message["type"] == "INGEST":
        document_path = mcp_message["payload"]["document_path"]
        chunks = run_ingestion_agent(document_path)
        return create_mcp_message(
            sender="IngestionAgent",
            receiver=mcp_message["sender"],
            type_="CHUNKS_ADDED",
            payload={"chunks": chunks},
            trace_id=mcp_message["trace_id"]
        )
    else:
        raise ValueError(f"Unknown message type: {mcp_message['type']}")
