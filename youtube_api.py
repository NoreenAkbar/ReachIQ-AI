from googleapiclient.discovery import build
from config import YOUTUBE_API_KEY, CHANNEL_ID

# Initialize YouTube client once
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

def get_videos(max_results=10):
    """Fetch latest videos from your channel"""
    channel_response = youtube.channels().list(
        part="contentDetails",
        id=CHANNEL_ID
    ).execute()

    uploads_id = channel_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    playlist_response = youtube.playlistItems().list(
        part="snippet",
        playlistId=uploads_id,
        maxResults=max_results
    ).execute()

    videos = []
    for item in playlist_response["items"]:
        videos.append({
            "title": item["snippet"]["title"],
            "video_id": item["snippet"]["resourceId"]["videoId"],
            "published": item["snippet"]["publishedAt"],
            "url": f"https://www.youtube.com/watch?v={item['snippet']['resourceId']['videoId']}"
        })
    return videos


def get_video_stats(video_id):
    """Fetch stats for a specific video"""
    response = youtube.videos().list(
        part="statistics,snippet",
        id=video_id
    ).execute()

    if not response["items"]:
        return None

    item = response["items"][0]
    stats = item["statistics"]

    return {
        "title": item["snippet"]["title"],
        "views": int(stats.get("viewCount", 0)),
        "likes": int(stats.get("likeCount", 0)),
        "comments": int(stats.get("commentCount", 0)),
        "published": item["snippet"]["publishedAt"]
    }


if __name__ == "__main__":
    print("Testing YouTube API module...")
    print("\nFetching your videos...")
    videos = get_videos(5)
    for v in videos:
        print(f"\nTitle: {v['title']}")
        print(f"ID: {v['video_id']}")
        print(f"URL: {v['url']}")

    print("\nFetching stats for first video...")
    stats = get_video_stats(videos[0]["video_id"])
    if stats:
        print(f"Views: {stats['views']}")
        print(f"Likes: {stats['likes']}")
        print(f"Comments: {stats['comments']}")