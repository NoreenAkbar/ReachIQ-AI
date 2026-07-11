import requests
from groq import Groq
from reachiq_video_rag_engine.config import GROQ_API_KEY, FIREWORKS_API_KEY, LLM_PROVIDER, MODELS

groq_client = Groq(api_key=GROQ_API_KEY)


def _call_groq(prompt):
    response = groq_client.chat.completions.create(
        model=MODELS["groq"],
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def _call_fireworks(prompt):
    response = requests.post(
        "https://api.fireworks.ai/inference/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {FIREWORKS_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": MODELS["fireworks"],
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 2000,
            "temperature": 0.3
        },
        timeout=60
    )
    data = response.json()

    print("\n========== FIREWORKS RESPONSE ==========")
    print(data)
    print("========================================\n")

    if "choices" not in data:
        raise Exception(f"Fireworks Error: {data}")

    return data["choices"][0]["message"]["content"]


def ask_llm(prompt, provider=None):
    """
    Provider-agnostic entry point.
    provider=None uses config default (LLM_PROVIDER).
    """
    use = provider or LLM_PROVIDER
    if use == "fireworks":
        return _call_fireworks(prompt)
    return _call_groq(prompt)