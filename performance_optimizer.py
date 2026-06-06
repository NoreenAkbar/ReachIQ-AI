from googleapiclient.discovery import build
from groq import Groq
import json
import time
from config import YOUTUBE_API_KEY, GROQ_API_KEY, CHANNEL_ID

# Initialize clients
groq_client = Groq(api_key=GROQ_API_KEY)
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

# Get uploads playlist
channel_response = youtube.channels().list(
    part="contentDetails",
    id=CHANNEL_ID
).execute()

uploads_playlist_id = channel_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

# Get last 5 videos
playlist_response = youtube.playlistItems().list(
    part="snippet",
    playlistId=uploads_playlist_id,
    maxResults=5
).execute()

# Analyze each video
for item in playlist_response["items"]:
    title = item["snippet"]["title"]
    video_id = item["snippet"]["resourceId"]["videoId"]

    print("\n==============================")
    print("CURRENT TITLE:")
    print(title)
    print("==============================\n")

    prompt = f"""
You are an elite YouTube CTR strategist.

Analyze this YouTube title and maximize curiosity, clickability, emotional trigger, and virality.

Rules:
- Avoid academic tone
- Avoid documentary style
- Use simple language
- Maximum 55 characters
- Make humans curious instantly
- Sound native to YouTube

Return ONLY valid JSON, no extra text, no markdown.

FORMAT:
{{
  "current_title_score": 0,
  "weaknesses": [],
  "improved_titles": [],
  "best_replacement": "",
  "reasoning": ""
}}

TITLE: {title}
"""

    try:
        print("Analyzing with Groq (Primary Brain)...")
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        optimized_output = response.choices[0].message.content

        # Parse and display
        try:
            clean = optimized_output.strip()
            if "```" in clean:
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            parsed = json.loads(clean)
            print(json.dumps(parsed, indent=2))
        except:
            print(optimized_output)

    except Exception as e:
        print(f"Groq failed: {e}")

    print("-" * 50)
    time.sleep(3)