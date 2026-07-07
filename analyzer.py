from brain import ask_brain
from youtube_api import get_videos
from query import get_niche_intelligence
from config import DEFAULT_NICHE
import json

def analyze_pre_upload(title, description, tags, script=None):
    """
    Analyzes content before upload using channel history
    + niche top videos comparison.
    """
    from keyword_tracker import find_competing_videos, extract_keywords
    import os
    import datetime

    script_section = f"\nSCRIPT EXCERPT:\n{script[:500]}" if script else ""

    # Load channel history
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
                            f"{h.get('performance_level','unknown')} performance\n"
                        )
            except:
                pass

    # Fetch niche top videos
    niche_context = ""
    try:
        keywords = extract_keywords(title, description)
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
    # Derive niche from existing keyword extraction, no extra LLM call
    niche = None
    if keywords and isinstance(keywords, dict):
        primary = keywords.get("primary_keywords", [])
        angles = keywords.get("trending_angles", [])
        if primary:
            niche = primary[0]
        elif angles:
            niche = angles[0]
    if not niche:
        niche = DEFAULT_NICHE

    rag_context = None
    try:
        rag_context = get_niche_intelligence(niche)
    except Exception as e:
        print(f"Video RAG note: {e}")

    rag_section = ""
    if rag_context:
        rag_section = f"\nNICHE INTELLIGENCE (Video RAG):\n{json.dumps(rag_context)[:800]}\n"
    prompt = f"""
You are ReachIQ AI — elite YouTube growth strategist.

Analyze this video BEFORE upload by comparing against:
1. This channel's historical performance patterns
2. What top niche videos are doing right now

Be brutally honest and specific. Every weakness must have a fix.
Never give generic advice — base everything on the niche and channel data provided.

Return ONLY valid JSON, no extra text, no markdown.

FORMAT:
{{
  "title_analysis": {{
    "score": 0,
    "weaknesses": [],
    "improved_titles": [],
    "best_title": "",
    "vs_niche": ""
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
  "top_3_actions": [],
  "niche_gap_opportunity": "",
  "channel_pattern_insight": ""
}}

TITLE: {title}
DESCRIPTION: {description}
TAGS: {tags}
{script_section}
{channel_context}
{niche_context}
{rag_section}
ANALYSIS RUN: {datetime.datetime.now().isoformat()}
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