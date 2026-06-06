from groq import Groq
import ollama
import time
from config import GROQ_API_KEY

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY)

def ask_brain(prompt, retries=3):
    """
    Main brain function. Every module in ReachIQ AI
    calls this instead of setting up its own AI client.
    Groq is primary, Ollama is local fallback.
    """

    # Try Groq first
    for attempt in range(retries):
        try:
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content

        except Exception as e:
            error = str(e)

            # Rate limit hit — wait and retry
            if "429" in error:
                wait = (attempt + 1) * 10
                print(f"Rate limit hit. Waiting {wait} seconds...")
                time.sleep(wait)
                continue

            # Other error — try Ollama
            print(f"Groq failed: {e}")
            break

    # Fallback to Ollama
    try:
        print("Falling back to Ollama...")
        response = ollama.chat(
            model="llama3.2:1b",
            messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"]

    except Exception as e:
        print(f"Ollama also failed: {e}")
        return None


if __name__ == "__main__":
    print("Testing brain...")
    result = ask_brain("Say hello in one word.")
    if result:
        print("Brain response:", result)
        print("Brain is working perfectly.")
    else:
        print("Brain failed.")