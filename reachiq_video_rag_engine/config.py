import os
from pathlib import Path
from dotenv import load_dotenv

# Local development (.env)
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Streamlit Cloud secrets
try:
    import streamlit as st
    secrets = st.secrets
except Exception:
    secrets = {}

def get_config(key, default=None):
    if key in secrets:
        return secrets[key]
    return os.getenv(key, default)

SUPABASE_URL = get_config("SUPABASE_URL")
SUPABASE_SERVICE_KEY = get_config("SUPABASE_SERVICE_KEY")
GROQ_API_KEY = get_config("GROQ_API_KEY")
FIREWORKS_API_KEY = get_config("FIREWORKS_API_KEY")

LLM_PROVIDER = get_config("RAG_LLM_PROVIDER", "groq")

MODELS = {
    "fireworks": "accounts/fireworks/models/gemma-4-31b-it",
    "groq": "openai/gpt-oss-120b"
}