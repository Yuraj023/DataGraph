import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure the Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 👇 UPDATE THIS LINE 👇
# Use the most intelligent Flash model for agents and coding
model = genai.GenerativeModel("gemini-3.8-flash") 

def generate_sql(user_query: str, okf_context: str) -> str:
    """Sends the OKF context and user query to Gemini 3.8 Flash to generate SQL."""
    
    prompt = f"""
    You are an expert Data Engineer and SQL Developer. 
    You are provided with structured context from an Open Knowledge Format (OKF) bundle.
    This context contains metric definitions, table schemas, and business rules.
    
    Your task is to write a flawless, optimized SQL query based on the user's request.
    You MUST strictly follow the business rules and edge cases defined in the context.
    Do not hallucinate column names; only use columns explicitly listed in the schemas.
    Return ONLY the SQL query, no explanations.
    
    ---
    
    OKF KNOWLEDGE CONTEXT:
    {okf_context}
    
    ---
    
    USER REQUEST:
    {user_query}
    """
    
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=0.1, # Keep it low for strict SQL generation
        )
    )
    
    return response.text