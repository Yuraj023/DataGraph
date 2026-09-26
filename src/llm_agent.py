import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Debug check to ensure API key is loaded
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError(" GEMINI_API_KEY not found! Check your .env file.")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-3.8-flash")

def generate_sql(user_query: str, okf_context: str) -> str:
    """Sends the OKF context and user query to Gemini to generate a clean response."""
    
    system_prompt = """
    You are an expert Senior Data Analyst AI Assistant. 
    You are provided with structured context from an Open Knowledge Format (OKF) bundle.
    
    Your task is to help the user understand their data and solve their problem concisely.
    Format your response EXACTLY like this:

    ** Business Logic:** [1-2 sentences explaining the rules applied from the context]
    ** SQL Query:** 
    ```sql
    [The optimized, production-ready SQL query]
    ```
    ** Pro-Tip:** [1 sentence on data quality, SLAs, partition keys, or edge cases from the runbooks]

    If the provided context does not contain the information needed, state clearly: " The current OKF bundle does not contain documentation for this specific metric/table." Do not hallucinate schemas.
    """
    
    user_prompt = f"""
    OKF KNOWLEDGE CONTEXT:
    {okf_context}
    
    USER REQUEST:
    {user_query}
    """
    
    response = model.generate_content(
        [system_prompt, user_prompt],
        generation_config=genai.types.GenerationConfig(
            temperature=0.1,
        )
    )
    
    return response.text