import os
import time
from groq import Groq
import ollama
from config import GROQ_API_KEY

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ─────────────────────────────────────────────
# REACHIQ AI — BRAIN MODULE v2.0
# Primary: Groq Llama 3.3 70B (general tasks)
# Analysis: Groq Llama 3.3 70B (analysis tasks)
# Local Advanced: Ollama Gemma3 12B
# Local Fallback: Ollama llama3.2:1b
# ─────────────────────────────────────────────

groq_client = Groq(api_key=GROQ_API_KEY)

MODELS = {
    "general": "llama-3.3-70b-versatile",
    "analysis": "llama-3.3-70b-versatile",
    "openrouter_gemma": "google/gemma-3-12b-it:free",
    "local_advanced": "gemma3:12b",
    "local_fallback": "llama3.2:1b"
}


def _call_groq(prompt, model, retries=3):
    for attempt in range(retries):
        try:
            response = groq_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content

        except Exception as e:
            error = str(e)
            if "429" in error:
                wait = (attempt + 1) * 10
                print(f"Rate limit hit. Waiting {wait}s...")
                time.sleep(wait)
                continue
            if "model" in error.lower() and \
               "not found" in error.lower():
                print(f"Model {model} not available.")
                return None
            print(f"Groq error: {e}")
            break
    return None


def _call_ollama(prompt, model):
    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"]
    except Exception as e:
        error = str(e)
        if "memory" in error.lower():
            print(f"Not enough RAM for {model}.")
        elif "not found" in error.lower():
            print(f"{model} not installed. "
                  f"Run: ollama pull {model}")
        else:
            print(f"Ollama error: {e}")
        return None


def ask_brain(prompt, retries=3):
    """General tasks — Llama 3.3 70B"""
    return _call_groq(prompt, MODELS["general"], retries)


def ask_brain_analysis(prompt, retries=3):
    """Deep analysis tasks — Llama 3.3 70B with fallback"""
    result = _call_groq(prompt, MODELS["analysis"], retries)
    if result:
        return result
    return _call_groq(prompt, MODELS["general"], retries)


def ask_brain_local(prompt, use_advanced=False):
    """Local Ollama brain"""
    if use_advanced:
        result = _call_ollama(prompt, MODELS["local_advanced"])
        if result:
            return result
    return _call_ollama(prompt, MODELS["local_fallback"])


def ask_with_fallback(prompt, task_type="general"):
    """
    Full fallback chain:
    1. Groq primary
    2. Ollama local advanced
    3. Ollama local fallback
    """
    if task_type == "analysis":
        result = ask_brain_analysis(prompt)
    else:
        result = ask_brain(prompt)

    if result:
        return result

    print("Groq unavailable. Trying local Ollama...")
    result = ask_brain_local(prompt, use_advanced=True)
    if result:
        return result

    print("All AI models unavailable.")
    return None


if __name__ == "__main__":
    print("=" * 55)
    print("ReachIQ AI — Brain Module Test")
    print("=" * 55)

    print("\nTest 1 — General (Llama 3.3 70B):")
    result = ask_brain("Say hello in one word.")
    print(f"Response: {result}")

    print("\nTest 2 — Analysis:")
    result = ask_brain_analysis(
        "What makes a good YouTube title? One sentence."
    )
    print(f"Response: {result}")

    print("\nTest 3 — Full fallback chain:")
    result = ask_with_fallback(
        "What is AI in one sentence?",
        task_type="general"
    )
    print(f"Response: {result}")

    print("\nBrain module ready.")
    print(f"Models: {list(MODELS.keys())}")