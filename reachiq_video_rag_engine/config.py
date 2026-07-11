import streamlit as st

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_SERVICE_KEY = st.secrets["SUPABASE_SERVICE_KEY"]
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
FIREWORKS_API_KEY = st.secrets["FIREWORKS_API_KEY"]

LLM_PROVIDER = "groq"

MODELS = {
    "fireworks": "accounts/fireworks/models/gemma-4-31b-it",
    "groq": "openai/gpt-oss-120b"
}