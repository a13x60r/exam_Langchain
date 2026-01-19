import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

def get_llm():
    """
    Initializes and returns the Groq LLM model.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable not set")
    
    return ChatGroq(
        temperature=0,
        model_name="llama-3.3-70b-versatile",
        api_key=api_key
    )
