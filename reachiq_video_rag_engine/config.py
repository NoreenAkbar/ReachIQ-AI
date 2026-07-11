import streamlit as st

SUPABASE_URL = st.secrets["general"]["SUPABASE_URL"]
SUPABASE_SERVICE_KEY = st.secrets["general"]["SUPABASE_SERVICE_KEY"]
GROQ_API_KEY = st.secrets["general"]["GROQ_API_KEY"]
FIREWORKS_API_KEY = st.secrets["general"].get("FIREWORKS_API_KEY", "")

LLM_PROVIDER = "groq"

MODELS = {
    "fireworks": "accounts/fireworks/models/gemma-4-31b-it",
    "groq": "openai/gpt-oss-120b",
}