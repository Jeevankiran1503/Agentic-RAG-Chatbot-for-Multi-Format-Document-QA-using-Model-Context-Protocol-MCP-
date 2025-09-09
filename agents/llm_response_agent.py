import google.generativeai as genai
from dotenv import load_dotenv
import os
from utils.mcp import create_mcp_message
from utils.mcp import create_mcp_message
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-pro")

def run_llm_response_agent(question, context_chunks):
    context = "\n\n".join(context_chunks)
    prompt = f"""
You are a helpful assistant that answers user questions using the provided context. If the answer is not present in the context, respond with "I don't know."

Context:
{context}

Question:
{question}

Answer:
"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"LLM error: {e}"

def handle_message(mcp_message):
        if mcp_message["type"] == "GENERATE_RESPONSE":
            question = mcp_message["payload"]["question"]
            top_chunks = mcp_message["payload"]["top_chunks"]
            final_response = run_llm_response_agent(question, top_chunks)
            return create_mcp_message(
                sender="LLMResponseAgent",
                receiver=mcp_message["sender"],
                type_="FINAL_RESPONSE",
                payload={"final_response": final_response},
                trace_id=mcp_message["trace_id"]
            )
        else:
            raise ValueError(f"Unknown message type: {mcp_message['type']}")
