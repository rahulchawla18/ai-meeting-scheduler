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
- IMPORTANT: If no timezone is mentioned, assume IST (Indian Standard Time, UTC+5:30) and use +05:30 offset.
- If timezone words like IST/ET appear, resolve to proper offset (IST = +05:30, EST = -05:00, PST = -08:00).
- Participants should be emails if present; if only names appear, omit them.
- IMPORTANT: Use the meeting topic/purpose as the title. If a specific topic is mentioned (e.g., "discuss project updates", "Multi-Agent Orchestration System discussion"), use that as the title.
- Only use generic titles like "Meeting" if no specific topic is provided.
Return ONLY JSON, no prose.
"""

def extract_meeting_from_prompt(prompt: str) -> Dict[str, Any]:
    """
    Calls GROQ API to extract structured meeting fields.
    """
    s = get_settings()
    url = f"{s.groq_base_url}/chat/completions"

    headers = {
        "Authorization": f"Bearer {s.groq_api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": s.groq_model,
        "messages": [
            {"role": "system", "content": SYS_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1
    }

    try:
        r = requests.post(url, json=payload, headers=headers, timeout=60)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        error_detail = str(e)
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = f"{e} - Response: {e.response.text}"
            except:
                pass
        raise HTTPException(status_code=500, detail=f"GROQ API request failed: {error_detail}")

    try:
        data = r.json()
        print(data)
        content = data["choices"][0]["message"]["content"].strip()

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
        raise HTTPException(status_code=500, detail=f"Error parsing GROQ response: {e}")
