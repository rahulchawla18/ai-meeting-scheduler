import requests
import json
from typing import Dict, Any
from config import get_settings
from models.event import ExtractedMeeting
from fastapi import HTTPException

SYS_PROMPT = """You are a precise meeting scheduling parser.
Extract ONLY a compact JSON with keys:
{
  "title": "string",
  "participants": ["email1@example.com", "..."],
  "start_time": "ISO8601 with timezone, e.g. 2025-08-16T10:00:00+05:30",
  "duration_minutes": number,
  "agenda": "string"
}
- If duration is missing, default 30.
- If timezone words like IST/ET appear, resolve to proper offset.
- Participants should be emails if present; if only names appear, omit them.
Return ONLY JSON, no prose.
"""

def extract_meeting_from_prompt(prompt: str) -> Dict[str, Any]:
    """
    Calls local Ollama mistral chat API to extract structured meeting fields.
    Requires `ollama pull mistral` and Ollama server running.
    """
    s = get_settings()
    url = f"{s.ollama_base_url}/api/chat"

    payload = {
        "model": s.ollama_model,
        "messages": [
            {"role": "system", "content": SYS_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "options": {"temperature": 0.1}
    }

    try:
        r = requests.post(url, json=payload, timeout=60)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Ollama request failed: {e}")

    try:
        data = r.json()
        content = data["message"]["content"].strip()

        # Try direct JSON parsing
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            # Fallback: extract JSON substring
            start = content.find("{")
            end = content.rfind("}")
            if start == -1 or end == -1:
                raise ValueError("No JSON found in model response")
            parsed = json.loads(content[start:end + 1])

        # Validate with Pydantic
        ExtractedMeeting.model_validate(parsed)
        print("parsed....", parsed)
        return parsed

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing Ollama response: {e}")