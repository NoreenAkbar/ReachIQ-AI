import os
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID")

if __name__ == "__main__":
    print("YOUTUBE_API_KEY:", "✅ Loaded" if YOUTUBE_API_KEY else "❌ Missing")
    print("GROQ_API_KEY:", "✅ Loaded" if GROQ_API_KEY else "❌ Missing")
    print("CHANNEL_ID:", "✅ Loaded" if CHANNEL_ID else "❌ Missing")