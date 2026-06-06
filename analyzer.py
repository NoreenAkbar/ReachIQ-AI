from brain import ask_brain
from youtube_api import get_videos
import json

def analyze_pre_upload(title, description, tags, script=None):
    """
    Analyzes content before you upload.
    Scores title, description, tags, hook, and thumbnail suggestion.
    """

    script_section = f"\nSCRIPT EXCERPT:\n{script[:500]}" if script else ""

    prompt = f"""
You are ReachIQ AI, an elite YouTube growth strategist.

Analyze this video content before upload.
Give honest, specific, actionable feedback.

Return ONLY valid JSON, no extra text, no markdown.

FORMAT:
{{
  "title_analysis": {{
    "score": 0,
    "weaknesses": [],
    "improved_titles": [],
    "best_title": ""
  }},
  "description_analysis": {{
    "score": 0,
    "weaknesses": [],
    "improvements": []
  }},
  "tags_analysis": {{
    "score": 0,
    "missing_tags": [],
    "recommended_tags": []
  }},
  "hook_suggestion": "",
  "thumbnail_text": "",
  "overall_score": 0,
  "upload_ready": true,
  "top_3_actions": []
}}

TITLE: {title}
DESCRIPTION: {description}
TAGS: {tags}
{script_section}
"""

    print("ReachIQ AI analyzing your content...")
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


def analyze_channel_patterns():
    """
    Analyzes your existing videos to find
    what is working and what is not.
    """
    videos = get_videos(10)

    titles = [v["title"] for v in videos]
    titles_text = "\n".join([f"- {t}" for t in titles])

    prompt = f"""
You are ReachIQ AI analyzing a YouTube channel's content patterns.

Study these video titles and identify patterns.

Return ONLY valid JSON, no extra text, no markdown.

FORMAT:
{{
  "strong_titles": [],
  "weak_titles": [],
  "content_patterns": [],
  "what_works": [],
  "what_to_avoid": [],
  "recommended_next_topics": [],
  "channel_positioning": ""
}}

CHANNEL TITLES:
{titles_text}
"""

    print("Analyzing your channel patterns...")
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


if __name__ == "__main__":
    print("=" * 50)
    print("TEST 1 — Pre Upload Analysis")
    print("=" * 50)

    result = analyze_pre_upload(
        title="How AI is Changing Education Forever",
        description="In this video we explore how artificial intelligence is transforming the way students learn and teachers teach.",
        tags="AI, education, machine learning, students, future",
        script="Welcome back everyone. Today we are going to talk about something that is literally changing everything in education right now."
    )

    if result:
        print(json.dumps(result, indent=2))

    print("\n" + "=" * 50)
    print("TEST 2 — Channel Pattern Analysis")
    print("=" * 50)

    patterns = analyze_channel_patterns()
    if patterns:
        print(json.dumps(patterns, indent=2))