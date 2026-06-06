from googleapiclient.discovery import build
from brain import ask_brain
from youtube_api import get_videos
from config import YOUTUBE_API_KEY
import json
import datetime
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)


def extract_keywords(video_title, video_description=""):
    """
    Extracts the most important keywords from
    your video title and description.
    """
    prompt = f"""
You are ReachIQ AI extracting YouTube SEO keywords.

Extract the most important keywords from this video content.
Focus on keywords people actually search on YouTube.

Return ONLY valid JSON, no extra text, no markdown.

FORMAT:
{{
  "primary_keywords": [],
  "secondary_keywords": [],
  "long_tail_keywords": [],
  "trending_angles": [],
  "search_intent": ""
}}

Rules:
- Primary keywords: 3-5 main keywords with highest search volume
- Secondary keywords: 5-8 supporting keywords
- Long tail keywords: 5-8 specific phrases people search
- Trending angles: 3-5 ways to position this topic for maximum views

VIDEO TITLE: {video_title}
DESCRIPTION: {video_description}
"""

    result = ask_brain(prompt)
    if result:
        try:
            clean = result.strip()
            if "```" in clean:
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            return json.loads(clean)
        except:
            return result
    return None


def find_competing_videos(keyword, max_results=5):
    """
    Finds top performing videos for a keyword
    so you can see what the competition is doing.
    """
    try:
        response = youtube.search().list(
            part="snippet",
            q=keyword,
            type="video",
            order="viewCount",
            maxResults=max_results
        ).execute()

        competitors = []
        for item in response.get("items", []):
            competitors.append({
                "title": item["snippet"]["title"],
                "channel": item["snippet"]["channelTitle"],
                "video_id": item["id"]["videoId"],
                "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                "published": item["snippet"]["publishedAt"][:10]
            })
        return competitors

    except Exception as e:
        print(f"Search error: {e}")
        return []


def analyze_competition(your_title, competitors):
    """
    Compares your video against top competitors
    and tells you exactly what to do differently.
    """
    comp_text = "\n".join([
        f"- {c['title']} ({c['channel']})"
        for c in competitors
    ])

    prompt = f"""
You are ReachIQ AI doing competitive analysis for a YouTube video.

Compare this video against the top performing competitors.
Give specific actionable advice to outperform them.

Return ONLY valid JSON, no extra text, no markdown.

FORMAT:
{{
  "competitive_position": "",
  "what_competitors_do_better": [],
  "your_advantages": [],
  "gap_opportunities": [],
  "title_improvements": [],
  "content_angle_suggestions": [],
  "ranking_difficulty": "",
  "recommended_action": ""
}}

YOUR VIDEO: {your_title}

TOP COMPETITORS:
{comp_text}
"""

    result = ask_brain(prompt)
    if result:
        try:
            clean = result.strip()
            if "```" in clean:
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            return json.loads(clean)
        except:
            return result
    return None


def find_distribution_opportunities(keywords):
    """
    Finds YouTube videos and channels in your niche
    where you can engage and promote your content.
    """
    opportunities = []

    for keyword in keywords[:3]:
        try:
            response = youtube.search().list(
                part="snippet",
                q=keyword,
                type="video",
                order="date",
                maxResults=3,
                publishedAfter=(
                    datetime.datetime.now() -
                    datetime.timedelta(days=30)
                ).strftime("%Y-%m-%dT%H:%M:%SZ")
            ).execute()

            for item in response.get("items", []):
                opportunities.append({
                    "keyword": keyword,
                    "title": item["snippet"]["title"],
                    "channel": item["snippet"]["channelTitle"],
                    "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                    "published": item["snippet"]["publishedAt"][:10]
                })

        except Exception as e:
            print(f"Search error for {keyword}: {e}")

    return opportunities


def generate_keyword_report(video_title, keywords_data,
                             competitors, competition_analysis,
                             opportunities):
    """
    Saves complete keyword and competition report to file.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"keyword_report_{timestamp}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write("ReachIQ AI — Keyword & Competition Report\n")
        f.write(f"Generated: {datetime.datetime.now()}\n")
        f.write(f"Video: {video_title}\n")
        f.write("=" * 55 + "\n\n")

        f.write("EXTRACTED KEYWORDS:\n")
        f.write(json.dumps(keywords_data, indent=2))
        f.write("\n\n")

        f.write("TOP COMPETING VIDEOS:\n")
        for c in competitors:
            f.write(f"- {c['title']}\n")
            f.write(f"  Channel: {c['channel']}\n")
            f.write(f"  URL: {c['url']}\n\n")

        f.write("COMPETITION ANALYSIS:\n")
        f.write(json.dumps(competition_analysis, indent=2))
        f.write("\n\n")

        f.write("DISTRIBUTION OPPORTUNITIES:\n")
        for o in opportunities:
            f.write(f"Keyword: {o['keyword']}\n")
            f.write(f"Video: {o['title']}\n")
            f.write(f"Channel: {o['channel']}\n")
            f.write(f"URL: {o['url']}\n\n")

    print(f"Keyword report saved to: {filename}")
    return filename


def run_keyword_tracker():
    """
    Main keyword tracking function.
    Runs for all your recent videos.
    """
    print("=" * 55)
    print("ReachIQ AI — Keyword Tracker")
    print(f"Date: {datetime.date.today()}")
    print("=" * 55)

    videos = get_videos(3)

    for video in videos:
        print(f"\n{'=' * 55}")
        print(f"VIDEO: {video['title']}")
        print(f"{'=' * 55}")

        # Extract keywords
        print("\nExtracting keywords...")
        keywords_data = extract_keywords(video["title"])

        if keywords_data:
            print("\nPrimary Keywords:")
            for kw in keywords_data.get("primary_keywords", []):
                print(f"  - {kw}")

            # Find competitors for first primary keyword
            primary_kw = keywords_data.get("primary_keywords", [])
            if primary_kw:
                print(f"\nFinding competitors for: {primary_kw[0]}")
                competitors = find_competing_videos(primary_kw[0])

                print(f"Found {len(competitors)} competing videos")
                for c in competitors:
                    print(f"  - {c['title']} ({c['channel']})")

                # Analyze competition
                print("\nAnalyzing competition...")
                competition_analysis = analyze_competition(
                    video["title"], competitors
                )

                if competition_analysis:
                    print(f"\nCompetitive Position: "
                          f"{competition_analysis.get('competitive_position', '')}")
                    print(f"Ranking Difficulty: "
                          f"{competition_analysis.get('ranking_difficulty', '')}")
                    print(f"Recommended Action: "
                          f"{competition_analysis.get('recommended_action', '')}")

                # Find distribution opportunities
                print("\nFinding distribution opportunities...")
                opportunities = find_distribution_opportunities(
                    primary_kw[:3]
                )
                print(f"Found {len(opportunities)} opportunities")

                # Save report
                generate_keyword_report(
                    video["title"],
                    keywords_data,
                    competitors,
                    competition_analysis,
                    opportunities
                )

        print(f"\nDone: {video['title']}")

    print(f"\n{'=' * 55}")
    print("Keyword tracker complete.")
    print("Check your project folder for keyword reports.")
    print(f"{'=' * 55}")


if __name__ == "__main__":
    run_keyword_tracker()