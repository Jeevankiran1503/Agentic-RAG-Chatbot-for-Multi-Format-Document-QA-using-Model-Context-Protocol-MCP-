def create_mcp_message(sender, receiver, type_, payload, trace_id=None):
    import uuid
    return {
        "sender": sender,
        "receiver": receiver,
        "type": type_,
        "trace_id": trace_id or str(uuid.uuid4()),
        "payload": payload
    }
