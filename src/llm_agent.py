import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found. Check your .env file.")

genai.configure(api_key=api_key)

# Highly compressed personas to save input tokens
PERSONAS = {
    "data_analyst": {
        "instruction": "Expert Data Analyst. Write optimized SQL based on context schemas and rules.",
        "keys": '{"logic":"rules applied","sql":"raw query no markdown","tip":"SLAs/edge cases","error":"missing info"}'
    },
    "devops_engineer": {
        "instruction": "Expert DevOps Engineer. Diagnose issues and provide CLI commands from context.",
        "keys": '{"diagnosis":"root cause","commands":"CLI commands no markdown","escalation":"escalation path","error":"missing info"}'
    },
    "security_auditor": {
        "instruction": "Expert Security Auditor. Assess risks and provide compliance recommendations.",
        "keys": '{"risk_assessment":"security risks","recommendations":"actions to take","compliance_gaps":"violations","error":"missing info"}'
    }
}

# Cache model instances to reduce initialization overhead and latency
_models = {}
def get_model(agent_type):
    if agent_type not in _models:
        # Using Gemini 3.8 Flash - optimized for autonomous agents
        _models[agent_type] = genai.GenerativeModel(
            "gemini-3.8-flash", 
            system_instruction=PERSONAS[agent_type]["instruction"]
        )
    return _models[agent_type]

def generate_analysis(user_query: str, okf_context: str, agent_type: str = "data_analyst") -> dict:
    """
    Generates a structured JSON response with minimal token usage using Gemini 3.8 Flash.
    """
    if agent_type not in PERSONAS:
        agent_type = "data_analyst"
        
    persona = PERSONAS[agent_type]
    model = get_model(agent_type)
    
    # Ultra-minimal prompt (saves ~150 tokens per request)
    prompt = f"""Context:
{okf_context}

Query: {user_query}

Return JSON ONLY. No markdown. Keys: {persona['keys']}"""

    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                response_mime_type="application/json",
                max_output_tokens=600 # Strict limit to prevent runaway costs
            )
        )
        
        result = json.loads(response.text)
        
        # Clean up any accidental markdown the LLM might hallucinate inside the JSON strings
        for key in result:
            if isinstance(result[key], str):
                # Strips accidental backticks or language tags like ```sql
                result[key] = result[key].strip().strip('`').replace('sql\n', '').replace('bash\n', '')
                
        return result
        
    except json.JSONDecodeError:
        # Fallback if JSON fails despite mime_type enforcement
        raw_text = response.text if 'response' in locals() else "No response generated."
        return {"error": "Failed to parse JSON from LLM.", "raw_response": raw_text}
    except Exception as e:
        return {"error": f"API Error: {str(e)}"}