from brain import ask_brain
from youtube_api import get_videos, get_video_stats
import json
import datetime
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def generate_updated_metadata(video_title, current_description,
                               current_tags, analytics_data=None):
    """
    Generates complete ready-to-paste metadata update
    using channel history + niche top videos comparison.
    """
    from keyword_tracker import extract_keywords, find_competing_videos
    import os

    # Load channel history for intelligence
    channel_context = ""
    db_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "performance_history.json")
    if os.path.exists(db_file):
        with open(db_file, "r", encoding="utf-8") as f:
            try:
                history = json.load(f)
                if history:
                    channel_context = "CHANNEL HISTORY:\n"
                    for h in history[-5:]:
                        channel_context += (
                            f"- '{h.get('title','')}': "
                            f"{h.get('views',0)} views, "
                            f"{h.get('performance_level','unknown')} performance, "
                            f"tags: {', '.join(h.get('updated_tags',[])[:3])}\n"
                        )
            except:
                pass

    # Fetch niche top videos for comparison
    niche_context = ""
    try:
        keywords = extract_keywords(video_title)
        if keywords and isinstance(keywords, dict):
            primary_kw = keywords.get("primary_keywords", [])
            if primary_kw:
                competitors = find_competing_videos(
                    primary_kw[0], max_results=5
                )
                if competitors:
                    niche_context = "TOP NICHE VIDEOS:\n"
                    for c in competitors:
                        niche_context += (
                            f"- '{c.get('title','')}' "
                            f"by {c.get('channel','')}\n"
                        )
    except Exception as e:
        print(f"Niche fetch note: {e}")

    analytics_section = ""
    if analytics_data and isinstance(analytics_data, dict):
        analytics_section = f"""
CURRENT PERFORMANCE:
Views: {analytics_data.get('views', 0)}
Watch Time: {analytics_data.get('watch_time_minutes', 0)} minutes
Avg View Duration: {analytics_data.get('avg_view_duration_seconds', 0)} seconds
Avg View Percentage: {analytics_data.get('avg_view_percentage', 0)}%
Subscribers Gained: {analytics_data.get('subscribers_gained', 0)}
Likes: {analytics_data.get('likes', 0)}
Comments: {analytics_data.get('comments', 0)}
"""

    prompt = f"""
You are ReachIQ AI — elite YouTube growth strategist.

Generate highly optimized metadata by analyzing:
1. This video's current performance
2. Channel's historical patterns
3. What top niche videos are doing

Be specific, creative, and different from generic advice.
Every field must be tailored to THIS channel and THIS niche.

Return ONLY valid JSON, no extra text, no markdown.

FORMAT:
{{
  "updated_title": "",
  "updated_description": "",
  "updated_tags": [],
  "thumbnail_text": "",
  "pinned_comment": "",
  "end_screen_suggestion": "",
  "hook_for_description": "",
  "update_priority": "",
  "expected_improvement": "",
  "why_this_will_work": ""
}}

Rules for description:
- First 2 lines must be powerful hook lines
- Include timestamps if possible
- Include relevant links ONLY: ChatGPT: https://chat.openai.com, Claude: https://claude.ai, Gemini: https://gemini.google.com
- Include hashtags at bottom
- Maximum 500 words

Rules for tags:
- Mix broad and specific tags
- Include long tail keywords
- Maximum 15 tags, each max 3 words

VIDEO TITLE: {video_title}
CURRENT DESCRIPTION: {current_description}
CURRENT TAGS: {current_tags}
{analytics_section}
{channel_context}
{niche_context}
ANALYSIS RUN: {datetime.datetime.now().isoformat()}
"""

    print(f"Generating updated metadata for: {video_title}")
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


def save_metadata_report(video_id, video_title, metadata):
    """
    Saves the metadata update to a file so you can
    copy paste directly into YouTube Studio.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"metadata_{video_id}_{timestamp}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"ReachIQ AI — Metadata Update Report\n")
        f.write(f"Generated: {datetime.datetime.now()}\n")
        f.write(f"Video: {video_title}\n")
        f.write("=" * 55 + "\n\n")

        if isinstance(metadata, dict):
            f.write("UPDATED TITLE:\n")
            f.write(metadata.get("updated_title", "") + "\n\n")

            f.write("UPDATED DESCRIPTION:\n")
            f.write(metadata.get("updated_description", "") + "\n\n")

            f.write("UPDATED TAGS:\n")
            tags = metadata.get("updated_tags", [])
            f.write(", ".join(tags) + "\n\n")

            f.write("THUMBNAIL TEXT:\n")
            f.write(metadata.get("thumbnail_text", "") + "\n\n")

            f.write("PINNED COMMENT SUGGESTION:\n")
            f.write(metadata.get("pinned_comment", "") + "\n\n")

            f.write("END SCREEN SUGGESTION:\n")
            f.write(metadata.get("end_screen_suggestion", "") + "\n\n")

            f.write("UPDATE PRIORITY:\n")
            f.write(metadata.get("update_priority", "") + "\n\n")

            f.write("EXPECTED IMPROVEMENT:\n")
            f.write(metadata.get("expected_improvement", "") + "\n\n")
        else:
            f.write(str(metadata))

    print(f"Report saved to: {filename}")
    return filename


def run_metadata_updater():
    """
    Fetches your videos and generates metadata
    updates for each one.
    """
    print("=" * 55)
    print("ReachIQ AI — Metadata Updater")
    print(f"Date: {datetime.date.today()}")
    print("=" * 55)

    videos = get_videos(5)

    for video in videos:
        print(f"\nProcessing: {video['title']}")

        # Get current stats
        stats = get_video_stats(video["video_id"])

        current_description = "No description available"
        current_tags = "No tags available"

        if stats:
            print(f"Current Views: {stats['views']}")
            print(f"Current Likes: {stats['likes']}")

        # Generate updated metadata
        metadata = generate_updated_metadata(
            video_title=video["title"],
            current_description=current_description,
            current_tags=current_tags,
            analytics_data=stats
        )

        if metadata:
            print("\nGenerated Metadata:")
            if isinstance(metadata, dict):
                print(f"New Title: {metadata.get('updated_title', '')}")
                print(f"Thumbnail: {metadata.get('thumbnail_text', '')}")
                print(f"Priority: {metadata.get('update_priority', '')}")
                print(f"Expected: {metadata.get('expected_improvement', '')}")

            # Save full report to file
            save_metadata_report(
                video["video_id"],
                video["title"],
                metadata
            )

        print("-" * 55)

    print("\nMetadata updater complete.")
    print("Check your project folder for saved report files.")


if __name__ == "__main__":
    run_metadata_updater()