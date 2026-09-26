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
    You are an expert Senior Data Analyst and AI Assistant. 
    You are provided with structured context from an Open Knowledge Format (OKF) bundle.
    
    Your task is to help the user understand their data and solve their problem.
    1. First, briefly explain the business logic or rules that apply to their request based on the context.
    2. Second, provide the optimized SQL query to solve their problem.
    3. Third, add a "Pro-Tip" mentioning any data quality warnings, SLAs, or known bugs from the runbooks that they should be aware of.
    
    Be concise, professional, and strictly adhere to the provided context.
    
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