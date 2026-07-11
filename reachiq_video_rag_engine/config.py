import os
from pathlib import Path
from dotenv import load_dotenv

# Local development
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

try:
    import streamlit as st

    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_SERVICE_KEY = st.secrets["SUPABASE_SERVICE_KEY"]
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    FIREWORKS_API_KEY = st.secrets["FIREWORKS_API_KEY"]
    LLM_PROVIDER = st.secrets.get("RAG_LLM_PROVIDER", "groq")

except Exception:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    FIREWORKS_API_KEY = os.getenv("FIREWORKS_API_KEY")
    LLM_PROVIDER = os.getenv("RAG_LLM_PROVIDER", "groq")

MODELS = {
    "fireworks": "accounts/fireworks/models/gemma-4-31b-it",
    "groq": "openai/gpt-oss-120b",
}