import os
import json
import re
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# OpenRouter Configuration
# ============================================================

api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    raise ValueError("OPENROUTER_API_KEY not found. Check your .env file.")

MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/free")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)

# ============================================================
# Agent Personas
# ============================================================

PERSONAS = {
    "data_analyst": {
        "instruction": (
            "You are an expert Data Analyst. "
            "Write optimized SQL based on the provided context, "
            "schemas, metrics, and rules. Be extremely concise."
        ),
        "keys": ["logic", "sql", "tip", "error"]
    },
    "devops_engineer": {
        "instruction": (
            "You are an expert DevOps Engineer. "
            "Diagnose infrastructure and deployment issues "
            "and provide CLI commands based only on the provided context. Be extremely concise."
        ),
        "keys": ["diagnosis", "commands", "escalation", "error"]
    },
    "security_auditor": {
        "instruction": (
            "You are an expert Security Auditor. "
            "Assess security risks and provide compliance "
            "recommendations based only on the provided context. Be extremely concise."
        ),
        "keys": ["risk_assessment", "recommendations", "compliance_gaps", "error"]
    }
}

# ============================================================
# Helper Functions
# ============================================================

def get_model(agent_type: str) -> str:
    return MODEL

def extract_value_from_broken_json(text: str, key: str) -> str:
    pattern = rf'"{re.escape(key)}"\s*:\s*"((?:\\.|[^"\\])*)"'
    match = re.search(pattern, text, re.DOTALL)
    
    if match:
        value = match.group(1)
        try:
            value = json.loads(f'"{value}"')
        except json.JSONDecodeError:
            value = (
                value
                .replace("\\n", "\n")
                .replace('\\"', '"')
                .replace("\\\\", "\\")
            )
        return value.strip()
    
    return ""

# ============================================================
# Main Analysis Function (With Retry Logic)
# ============================================================

def generate_analysis(
    user_query: str,
    okf_context: str,
    agent_type: str = "data_analyst"
) -> dict:
    if agent_type not in PERSONAS:
        agent_type = "data_analyst"

    persona = PERSONAS[agent_type]
    model = get_model(agent_type)

    keys_str = ", ".join(f'"{key}"' for key in persona["keys"])

    prompt = f"""
Context:
{okf_context}

Query:
{user_query}

Return a JSON object with exactly these keys:
{keys_str}

Rules:
- Return ONLY a valid JSON object.
- Do not use Markdown.
- Do not use ```json.
- Do not add explanations outside the JSON object.
- Use an empty string when a field has no relevant information.
"""

    # ========================================================
    # RETRY LOOP: Tries up to 3 times if it hits a 429 limit
    # ========================================================
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": persona["instruction"]
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=2048,
                response_format={
                    "type": "json_object"
                }
            )
            # If successful, break out of the retry loop
            break 
            
        except Exception as e:
            error_str = str(e)
            # If it's a 429 Rate Limit error, wait and try again
            if "429" in error_str and attempt < 2:
                wait_time = 15 * (attempt + 1) # Waits 15s, then 30s
                print(f"⚠️ Hit free tier token limit (429). Waiting {wait_time}s for quota to refill...")
                time.sleep(wait_time)
            else:
                # If it fails 3 times, or it's a different error, return it
                return {"error": f"API Error: {str(e)}"}

    # ========================================================
    # Parse Response
    # ========================================================
    raw_text = response.choices[0].message.content

    if not raw_text:
        return {"error": "LLM returned an empty response."}

    raw_text = raw_text.strip()

    if raw_text.startswith("```"):
        raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text, flags=re.IGNORECASE)
        raw_text = re.sub(r"\s*```$", "", raw_text)

    try:
        start_idx = raw_text.find("{")
        end_idx = raw_text.rfind("}")

        if start_idx != -1 and end_idx != -1:
            json_str = raw_text[start_idx:end_idx + 1]
            result = json.loads(json_str)
        else:
            raise json.JSONDecodeError("No JSON object found", raw_text, 0)

    except json.JSONDecodeError:
        result = {}
        for key in persona["keys"]:
            result[key] = extract_value_from_broken_json(raw_text, key)

        if not any(result.values()):
            return {
                "error": "Failed to parse JSON from LLM.",
                "raw_response": raw_text
            }

    for key in result:
        if isinstance(result[key], str):
            result[key] = result[key].strip()
            result[key] = result[key].strip("`")
            result[key] = re.sub(r"^sql\s*", "", result[key], flags=re.IGNORECASE)
            result[key] = re.sub(r"^bash\s*", "", result[key], flags=re.IGNORECASE)

    return result