import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found. Check your .env file.")

genai.configure(api_key=api_key)

# Minimal system instruction - just tell it what it is, not how to format
model = genai.GenerativeModel(
    "gemini-3.8-flash",
    system_instruction="You are an expert technical assistant. Answer concisely based on the provided context."
)

def generate_analysis(user_query: str, okf_context: str) -> dict:
    """
    Sends context to LLM with minimal prompt overhead.
    Returns raw response text - formatting handled by Streamlit.
    """
    
    # Ultra-minimal prompt - just context + query
    prompt = f"""Context:
{okf_context}

Query: {user_query}

Answer:"""
    
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=1000  # Limit output to save tokens
            )
        )
        
        return {"response": response.text}
        
    except Exception as e:
        return {"error": str(e)}