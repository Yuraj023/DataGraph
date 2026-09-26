import os
import json
import re
import time
from typing import Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# Agent Personas (Structured for OKF Enterprise Tasks)
# ============================================================

PERSONAS: Dict[str, Dict[str, Any]] = {
    "data_analyst": {
        "instruction": "Expert Data Analyst. Write production-ready, optimized SQL strictly honoring schema constraints, join rules, and PII masking.",
        "keys": ["logic", "sql", "tip", "error"]
    },
    "devops_engineer": {
        "instruction": "Expert DevOps & Reliability Engineer. Diagnose infrastructure issues and provide actionable CLI runbook commands.",
        "keys": ["diagnosis", "commands", "escalation", "error"]
    },
    "security_auditor": {
        "instruction": "Expert Security & Compliance Auditor. Assess risks, check GDPR/PII compliance rules, and identify governance gaps.",
        "keys": ["risk_assessment", "recommendations", "compliance_gaps", "error"]
    }
}

_client: Optional[OpenAI] = None

def get_client() -> OpenAI:
    """Lazily initializes and caches the API client."""
    global _client
    if _client is not None:
        return _client

    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("API key not found. Please provide OPENROUTER_API_KEY or GEMINI_API_KEY in your .env file.")

    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    _client = OpenAI(base_url=base_url, api_key=api_key)
    return _client

def get_model() -> str:
    """Returns the model configured in the environment."""
    return os.getenv("OPENROUTER_MODEL", "openrouter/free")

def extract_value_from_broken_json(text: str, key: str) -> str:
    """
    Regex fallback extractor for JSON broken by token truncation or markdown wrappers.
    Recovers both complete and truncated (unclosed) string values.
    """
    # 1. Try matching fully-quoted value
    pattern_closed = rf'"{re.escape(key)}"\s*:\s*"((?:\\.|[^"\\])*)"'
    match = re.search(pattern_closed, text, re.DOTALL)
    
    # 2. If truncated before closing quote, match until end of string
    if not match:
        pattern_unclosed = rf'"{re.escape(key)}"\s*:\s*"((?:\\.|[^"\\])*)$'
        match = re.search(pattern_unclosed, text, re.DOTALL)

    if match:
        raw_val = match.group(1)
        try:
            parsed = json.loads(f'"{raw_val}"')
            return str(parsed).strip()
        except Exception:
            cleaned = (
                raw_val
                .replace("\\n", "\n")
                .replace('\\"', '"')
                .replace("\\\\", "\\")
            )
            return cleaned.strip()

    return ""

def generate_analysis(
    user_query: str,
    okf_context: str,
    agent_type: str = "data_analyst"
) -> Dict[str, Any]:
    """Generates structured JSON response strictly adhering to the persona schema."""
    persona = PERSONAS.get(agent_type, PERSONAS["data_analyst"])
    keys_str = ", ".join(f'"{key}"' for key in persona["keys"])

    prompt = f"""Context:
{okf_context}

Query: {user_query}

Return a valid JSON object with exactly these keys: {keys_str}.
Do not include markdown fences, comments, or extra keys. Empty string if not applicable."""

    try:
        client = get_client()
    except Exception as e:
        return {"error": str(e)}

    model = get_model()
    response = None

    # Retry loop with exponential backoff for rate limits
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": persona["instruction"]},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1500,
                response_format={"type": "json_object"}
            )
            break
        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg and attempt < 2:
                wait_time = 4 * (attempt + 1)
                time.sleep(wait_time)
            else:
                return {"error": f"API Error: {err_msg}"}

    if not response or not response.choices:
        return {"error": "LLM failed to return a valid completion."}

    raw_text = (response.choices[0].message.content or "").strip()
    if not raw_text:
        return {"error": "LLM returned an empty response."}

    # Clean markdown wrappers if present
    if raw_text.startswith("```"):
        raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text, flags=re.IGNORECASE)
        raw_text = re.sub(r"\s*```$", "", raw_text)

    # Parse JSON or fallback via regex
    try:
        start_idx = raw_text.find("{")
        end_idx = raw_text.rfind("}")
        if start_idx != -1 and end_idx != -1:
            result = json.loads(raw_text[start_idx:end_idx + 1])
        else:
            raise json.JSONDecodeError("No JSON boundaries found", raw_text, 0)
    except json.JSONDecodeError:
        result = {
            key: extract_value_from_broken_json(raw_text, key)
            for key in persona["keys"]
        }
        if not any(result.values()):
            return {
                "error": "Failed to parse JSON from LLM.",
                "raw_response": raw_text
            }

    # Clean formatting using dictionary comprehension
    cleaned_result = {
        k: (
            re.sub(r"^(?:sql|bash)\s*", "", v.strip().strip("`"), flags=re.IGNORECASE)
            if isinstance(v, str) else v
        )
        for k, v in result.items()
    }

    return cleaned_result