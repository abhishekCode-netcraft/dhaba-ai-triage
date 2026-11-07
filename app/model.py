import json
import httpx

OLLAMA_URL = 'http://localhost:11434/api/generate'
MODEL_NAME = 'gemma4:e2b'

async def generate_triage(ticket_data):
    with open('prompt/triage_prompt.txt', 'r') as file:
        system_prompt = file.read()

    prompt = f"""
{system_prompt}

Analyze this support ticket:

{json.dumps(ticket_data, ensure_ascii=False)}

Return only valid JSON.
"""

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "format": "json",
            },
        )

        response.raise_for_status()

        result = response.json()

        return json.loads(result["response"])