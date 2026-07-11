import os
from pathlib import Path
from dotenv import load_dotenv

# Always load the .env beside the RAG project
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
FIREWORKS_API_KEY = os.getenv("FIREWORKS_API_KEY")

LLM_PROVIDER = os.getenv("RAG_LLM_PROVIDER", "groq")

MODELS = {
    "fireworks": "accounts/fireworks/models/gemma-4-31b-it",
    "groq": "openai/gpt-oss-120b"
}