import os
import streamlit as st

SUPABASE_URL = st.secrets.get("SUPABASE_URL")
SUPABASE_SERVICE_KEY = st.secrets.get("SUPABASE_SERVICE_KEY")
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
FIREWORKS_API_KEY = st.secrets.get("FIREWORKS_API_KEY")

print("URL:", SUPABASE_URL)
print("KEY:", SUPABASE_SERVICE_KEY[:10] if SUPABASE_SERVICE_KEY else None)