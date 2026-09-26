import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found. Check your .env file.")

genai.configure(api_key=api_key)

# Initialize model with a strict, token-efficient system instruction
model = genai.GenerativeModel(
    "gemini-3.8-flash",
    system_instruction="You are an expert Data Analyst. Output ONLY valid JSON. No markdown, no backticks, no conversational filler."
)

def generate_analysis(user_query: str, okf_context: str) -> dict:
    """Sends context and returns a structured JSON dictionary."""
    
    prompt = f"""
    OKF CONTEXT:
    {okf_context}
    
    USER QUERY:
    {user_query}
    
    Return a JSON object with exactly these 4 keys:
    {{
      "logic": "1-2 sentences explaining the business rules applied from the context.",
      "sql": "The raw SQL query string only. Do NOT wrap in markdown code blocks.",
      "tip": "1 sentence regarding data quality, SLAs, partition keys, or edge cases.",
      "error": "If the context is missing required info, explain here. Otherwise, empty string."
    }}
    """
    
    # Using response_mime_type guarantees valid JSON and saves tokens
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=0.1,
            response_mime_type="application/json"
        )
    )
    
    return json.loads(response.text)