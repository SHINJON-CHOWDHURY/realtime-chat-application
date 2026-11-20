import requests


OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "gemma3:4b"


def ask_ai(prompt):
    print("AI 1: function started")

    try:
        print("AI 2: sending request to Ollama")

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
            },
            timeout=180,
        )

        print("AI 3: Ollama responded")
        print("Status:", response.status_code)

        response.raise_for_status()

        print("AI 4: converting response to JSON")

        data = response.json()

        print("AI 5: JSON received")

        print("AI response:", data.get("response"))

        return data["response"]

    except Exception as e:
        print("AI ERROR:", type(e).__name__)
        print("AI ERROR MESSAGE:", str(e))
        raise