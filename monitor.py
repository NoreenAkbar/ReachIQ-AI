from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from youtube_api import get_videos
from brain import ask_brain
import pickle
import json
import os
import datetime
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Scopes needed for analytics
SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly"
]

def get_authenticated_service():
    """
    One time OAuth login. After first login saves token
    so you never have to login again.
    """
    creds = None

    # Load saved token if exists
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    # Login if no valid token
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save token for future runs
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    youtube_analytics = build("youtubeAnalytics", "v2", credentials=creds)
    youtube_data = build("youtube", "v3", credentials=creds)
    return youtube_analytics, youtube_data


def get_video_analytics(youtube_analytics, video_id, days=7):
    """
    Fetches real analytics for a video.
    Default is last 7 days.
    """
    end_date = datetime.date.today().strftime("%Y-%m-%d")
    start_date = (datetime.date.today() - datetime.timedelta(days=days)).strftime("%Y-%m-%d")

    try:
        response = youtube_analytics.reports().query(
            ids="channel==MINE",
            startDate=start_date,
            endDate=end_date,
            metrics="views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,subscribersGained,likes,comments,impressions,clickThroughRate",
            dimensions="video",
            filters=f"video=={video_id}"
        ).execute()

        if response.get("rows"):
            row = response["rows"][0]
            return {
                "video_id": video_id,
                "period_days": days,
                "views": int(row[0]) if row[0] else 0,
                "watch_time_minutes": float(row[1]) if row[1] else 0,
                "avg_view_duration_seconds": float(row[2]) if row[2] else 0,
                "avg_view_percentage": float(row[3]) if row[3] else 0,
                "subscribers_gained": int(row[4]) if row[4] else 0,
                "likes": int(row[5]) if row[5] else 0,
                "comments": int(row[6]) if row[6] else 0,
                "impressions": int(row[7]) if row[7] else 0,
                "ctr_percent": round(float(row[8]) * 100, 2) if row[8] else 0
            }
        return None

    except Exception as e:
        print(f"Analytics error for {video_id}: {e}")
        return None


def get_channel_analytics(youtube_analytics, days=30):
    """
    Fetches overall channel analytics for last 30 days.
    """
    end_date = datetime.date.today().strftime("%Y-%m-%d")
    start_date = (datetime.date.today() - datetime.timedelta(days=days)).strftime("%Y-%m-%d")

    try:
        response = youtube_analytics.reports().query(
            ids="channel==MINE",
            startDate=start_date,
            endDate=end_date,
            metrics="views,estimatedMinutesWatched,subscribersGained,subscribersLost",
        ).execute()

        if response.get("rows"):
            row = response["rows"][0]
            return {
                "period_days": days,
                "total_views": row[0],
                "total_watch_time_minutes": row[1],
                "subscribers_gained": row[2],
                "subscribers_lost": row[3],
                "net_subscribers": row[2] - row[3]
            }
        return None

    except Exception as e:
        print(f"Channel analytics error: {e}")
        return None


def generate_improvement_suggestions(video_title, analytics_data):
    """
    Uses AI brain to suggest improvements based on real analytics.
    """
    prompt = f"""
You are ReachIQ AI analyzing real YouTube analytics data.

Based on these real stats, suggest specific improvements to boost this video's performance.

Return ONLY valid JSON, no extra text, no markdown.

FORMAT:
{{
  "performance_verdict": "",
  "biggest_problem": "",
  "metadata_suggestions": {{
    "update_title": true,
    "suggested_title": "",
    "update_description": true,
    "description_improvements": [],
    "update_tags": true,
    "suggested_tags": []
  }},
  "content_suggestions": [],
  "promotion_suggestions": [],
  "next_video_insights": []
}}

VIDEO TITLE: {video_title}
VIEWS: {analytics_data.get('views', 0)}
WATCH TIME (minutes): {analytics_data.get('watch_time_minutes', 0)}
AVG VIEW DURATION (seconds): {analytics_data.get('avg_view_duration_seconds', 0)}
AVG VIEW PERCENTAGE: {analytics_data.get('avg_view_percentage', 0)}%
SUBSCRIBERS GAINED: {analytics_data.get('subscribers_gained', 0)}
LIKES: {analytics_data.get('likes', 0)}
COMMENTS: {analytics_data.get('comments', 0)}
"""

    return ask_brain(prompt)


def run_daily_monitor():
    """
    Main monitoring function. Run this daily.
    Fetches analytics for all recent videos and
    generates improvement suggestions for each.
    """
    print("=" * 55)
    print("ReachIQ AI — Daily Monitor")
    print(f"Date: {datetime.date.today()}")
    print("=" * 55)

    # Authenticate
    print("\nAuthenticating with YouTube...")
    youtube_analytics, youtube_data = get_authenticated_service()
    print("Authenticated successfully.")

    # Channel overview
    print("\nFetching channel analytics (last 30 days)...")
    channel_stats = get_channel_analytics(youtube_analytics, days=30)
    if channel_stats:
        print(f"\nCHANNEL OVERVIEW (Last 30 days):")
        print(f"Total Views: {channel_stats['total_views']}")
        print(f"Watch Time: {channel_stats['total_watch_time_minutes']} minutes")
        print(f"Subscribers Gained: {channel_stats['subscribers_gained']}")
        print(f"Subscribers Lost: {channel_stats['subscribers_lost']}")
        print(f"Net Subscribers: {channel_stats['net_subscribers']}")

    # Get recent videos
    print("\nFetching your recent videos...")
    videos = get_videos(5)

    # Analyze each video
    for video in videos:
        print(f"\n{'=' * 55}")
        print(f"VIDEO: {video['title']}")
        print(f"{'=' * 55}")

        analytics = get_video_analytics(
            youtube_analytics,
            video["video_id"],
            days=7
        )

        if analytics:
            print(f"Views (7 days): {analytics['views']}")
            print(f"Watch Time: {analytics['watch_time_minutes']} minutes")
            print(f"Avg View Duration: {analytics['avg_view_duration_seconds']}s")
            print(f"Avg View Percentage: {analytics['avg_view_percentage']}%")
            print(f"Subscribers Gained: {analytics['subscribers_gained']}")

            print("\nGenerating AI improvement suggestions...")
            suggestions = generate_improvement_suggestions(
                video["title"], analytics
            )

            if suggestions:
                try:
                    clean = suggestions.strip()
                    if "```" in clean:
                        clean = clean.split("```")[1]
                        if clean.startswith("json"):
                            clean = clean[4:]
                    parsed = json.loads(clean)
                    print(json.dumps(parsed, indent=2))
                except:
                    print(suggestions)
        else:
            print("No analytics data available for this video yet.")
            print("Videos need at least 1-2 days after upload for analytics to appear.")

    print(f"\n{'=' * 55}")
    print("Daily monitor complete.")
    print(f"{'=' * 55}")


if __name__ == "__main__":
    run_daily_monitor()