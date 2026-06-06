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
    for a video based on performance data.
    """

    analytics_section = ""
    if analytics_data and isinstance(analytics_data, dict):
        analytics_section = f"""
CURRENT PERFORMANCE:
Views: {analytics_data.get('views', 0)}
Watch Time: {analytics_data.get('watch_time_minutes', 0)} minutes
Avg View Duration: {analytics_data.get('avg_view_duration_seconds', 0)} seconds
Avg View Percentage: {analytics_data.get('avg_view_percentage', 0)}%
Subscribers Gained: {analytics_data.get('subscribers_gained', 0)}
"""

    prompt = f"""
You are ReachIQ AI generating optimized YouTube metadata.

Create complete ready-to-use metadata that will improve this video's performance.
Be specific, practical, and YouTube algorithm friendly.

Return ONLY valid JSON, no extra text, no markdown.

FORMAT:
{{
  "updated_title": "",
  "updated_description": "",
  "updated_tags": [],
  "thumbnail_text": "",
  "pinned_comment": "",
  "end_screen_suggestion": "",
  "update_priority": "",
  "expected_improvement": ""
}}

Rules for description:
- First 2 lines must be hook lines people see before clicking more
- Include timestamps if possible
- - Include relevant links section but ONLY use these verified links:
  ChatGPT: https://chat.openai.com
  Claude: https://claude.ai
  Gemini: https://gemini.google.com
  Do not invent or guess any other URLs
- Include hashtags at the bottom
- Maximum 500 words

Rules for tags:
- Mix of broad and specific tags
- Include long tail keywords
- Maximum 15 tags
- Each tag maximum 3 words

VIDEO TITLE: {video_title}
CURRENT DESCRIPTION: {current_description}
CURRENT TAGS: {current_tags}
{analytics_section}
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