# ai_utils.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Your OpenRouter API key
API_KEY = os.getenv("OPENROUTER_API_KEY") or "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def generate_goal_suggestions(prompt):
    try:
        data = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are an academic mentor helping students create effective study goals."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 300
        }

        response = requests.post(API_URL, headers=HEADERS, json=data)
        response.raise_for_status()

        result = response.json()
        suggestions = [choice["message"]["content"].strip() for choice in result["choices"]]
        return suggestions

    except requests.exceptions.HTTPError as e:
        return [f"⚠️ HTTP Error: {e.response.status_code} - {e.response.text}"]
    except Exception as e:
        return [f"⚠️ Unexpected error: {e}"]
