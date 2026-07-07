import os
from dotenv import load_dotenv

load_dotenv()
def _get(key):
    try:
        import streamlit as st
        return st.secrets["general"][key] if "general" in st.secrets and key in st.secrets["general"] else os.getenv(key)
    except Exception:
        return os.getenv(key)

YOUTUBE_API_KEY = _get("YOUTUBE_API_KEY")
GROQ_API_KEY = _get("GROQ_API_KEY")
CHANNEL_ID = _get("CHANNEL_ID")
AIML_API_KEY = _get("AIML_API_KEY")
DEFAULT_NICHE = "AI Automation & Education"

if __name__ == "__main__":
    print("YOUTUBE_API_KEY:", "✅ Loaded" if YOUTUBE_API_KEY else "❌ Missing")
    print("GROQ_API_KEY:", "✅ Loaded" if GROQ_API_KEY else "❌ Missing")
    print("CHANNEL_ID:", "✅ Loaded" if CHANNEL_ID else "❌ Missing")
    print("AIML_API_KEY:", "✅ Loaded" if AIML_API_KEY else "❌ Missing")