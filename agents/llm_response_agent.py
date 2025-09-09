# agents/llm_response_agent.py

"""
This module represents the final stage of the RAG pipeline. It is responsible
for synthesizing a coherent, human-readable answer based on the user's question
and the context provided by the Retrieval Agent. It uses a powerful generative
language model (Google's Gemini Pro) to generate the final response.
"""

import google.generativeai as genai
from dotenv import load_dotenv
import os
from utils.mcp import create_mcp_message

# --- Model Initialization ---

# Load environment variables from a .env file (e.g., for the API key).
load_dotenv()

# Configure the Google Generative AI library with the API key.
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Instantiate the specific generative model to be used for answering questions.
model = genai.GenerativeModel("gemini-2.5-pro") 

# --- Core Logic Function ---

def run_llm_response_agent(question: str, context_chunks: list[str]) -> str:
    """
    Generates a final answer by feeding the question and context to a language model.

    This function constructs a detailed prompt that instructs the model to act as a
    helpful assistant and answer the user's question strictly based on the provided
    context chunks.

    Args:
        question (str): The original question from the user.
        context_chunks (list[str]): A list of relevant text chunks retrieved
                                    from the vector database.

    Returns:
        str: The generated answer from the language model, or an error message if
             the API call fails.
    """
    # Combine the individual context chunks into a single string, separated by newlines.
    context = "\n\n".join(context_chunks)
    
    # Construct the prompt using a template. This is a form of "prompt engineering".
    prompt = f"""
You are a helpful assistant that answers user questions using the provided context.
Your goal is to be accurate and concise.

If the answer is present in the context, formulate a clear response.
If the answer is not present in the context, respond with "I am sorry, but I cannot answer this question based on the provided documents."

Context:
---
{context}
---

Question:
{question}

Answer:
"""
    try:
        # Send the complete prompt to the generative model.
        response = model.generate_content(prompt)
        # Extract and return the plain text from the model's response.
        return response.text
    except Exception as e:
        # Handle potential errors during the API call (e.g., network issues, API key problems).
        print(f"An error occurred while generating the LLM response: {e}")
        return f"An error occurred while trying to generate an answer. Please check the logs."

# --- Message Handling ---

def handle_message(mcp_message: dict) -> dict:
    """
    Acts as the public interface for the LLM Response Agent, handling incoming messages.

    It processes messages of type "GENERATE_RESPONSE" by calling the language model
    and returning the final answer in a new message.

    Args:
        mcp_message (dict): A message dictionary following the Message Communication Protocol.

    Returns:
        dict: A response message containing the final, synthesized answer.

    Raises:
        ValueError: If the message type is unknown or unsupported.
    """
    # Check if the message is a "GENERATE_RESPONSE" request.
    if mcp_message["type"] == "GENERATE_RESPONSE":
        # Extract the question and the retrieved context chunks from the message payload.
        question = mcp_message["payload"]["question"]
        top_chunks = mcp_message["payload"]["top_chunks"]
        
        # Call the core logic function to generate the final response from the LLM.
        final_response = run_llm_response_agent(question, top_chunks)
        
        # Create and return the final response message.
        return create_mcp_message(
            sender="LLMResponseAgent",
            receiver=mcp_message["sender"],
            type_="FINAL_RESPONSE",
            payload={"final_response": final_response},
            trace_id=mcp_message["trace_id"]
        )
    else:
        # If the message type is not supported, raise an error.
        raise ValueError(f"Unknown message type: {mcp_message['type']}")