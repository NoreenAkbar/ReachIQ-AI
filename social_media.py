from brain import ask_brain
from youtube_api import get_videos
import json
import datetime
import os
import webbrowser

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def generate_platform_posts(video_title, video_url, 
                             keywords, channel_name="SmartMindAIverse"):
    """
    Generates platform specific posts for each
    social media platform. You click post.
    """

    prompt = f"""
You are ReachIQ AI creating social media posts to promote a YouTube video.

Create platform specific posts that feel native and genuine.
Never sound spammy. Always provide value first.

Return ONLY valid JSON, no extra text, no markdown.

FORMAT:
{{
  "youtube_community": {{
    "post": "",
    "emoji_hooks": []
  }},
  "facebook": {{
    "post": "",
    "suggested_groups": [],
    "hashtags": []
  }},
  "linkedin": {{
    "post": "",
    "angle": "",
    "hashtags": []
  }},
  "reddit": {{
    "suggested_subreddits": [],
    "post_title": "",
    "post_body": "",
    "comment_template": ""
  }},
  "quora": {{
    "suggested_questions_to_answer": [],
    "answer_template": ""
  }},
  "twitter": {{
    "tweet": "",
    "thread_starter": "",
    "hashtags": []
  }}
}}

Rules:
- Each post must feel native to that platform
- Reddit and Quora must lead with genuine value not promotion
- LinkedIn must be professional and insight focused
- Facebook must be conversational and engaging
- Include video URL naturally not spammy
- Maximum tweet length 280 characters

VIDEO TITLE: {video_title}
VIDEO URL: {video_url}
CHANNEL: {channel_name}
KEYWORDS: {keywords}
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


def find_reddit_opportunities(keywords):
    """
    Suggests relevant subreddits and discussion angles
    for each keyword.
    """
    keywords_text = ", ".join(keywords[:5])

    prompt = f"""
You are ReachIQ AI finding Reddit promotion opportunities.

For these keywords find the best subreddits and discussion angles.
Focus on genuinely helpful engagement not spam.

Return ONLY valid JSON, no extra text, no markdown.

FORMAT:
{{
  "subreddits": [
    {{
      "name": "",
      "reason": "",
      "engagement_angle": "",
      "sample_comment": ""
    }}
  ],
  "best_subreddit": "",
  "engagement_strategy": ""
}}

KEYWORDS: {keywords_text}
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


def find_quora_opportunities(keywords):
    """
    Finds relevant Quora questions to answer
    with your video as a resource.
    """
    keywords_text = ", ".join(keywords[:5])

    prompt = f"""
You are ReachIQ AI finding Quora promotion opportunities.

Suggest the most relevant Quora questions to answer 
for these keywords where a YouTube video would add value.

Return ONLY valid JSON, no extra text, no markdown.

FORMAT:
{{
  "questions": [
    {{
      "question": "",
      "search_url": "",
      "answer_angle": "",
      "sample_answer": ""
    }}
  ],
  "best_question": "",
  "engagement_strategy": ""
}}

KEYWORDS: {keywords_text}
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


def save_social_media_report(video_title, video_id,
                              posts, reddit_opps, quora_opps):
    """
    Saves all social media content to a single file.
    Ready to copy paste and post.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"social_media_{video_id}_{timestamp}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write("ReachIQ AI — Social Media Distribution Report\n")
        f.write(f"Generated: {datetime.datetime.now()}\n")
        f.write(f"Video: {video_title}\n")
        f.write("=" * 55 + "\n\n")

        if isinstance(posts, dict):
            # YouTube Community
            f.write("YOUTUBE COMMUNITY POST:\n")
            f.write("-" * 30 + "\n")
            yt = posts.get("youtube_community", {})
            f.write(yt.get("post", "") + "\n\n")

            # Facebook
            f.write("FACEBOOK POST:\n")
            f.write("-" * 30 + "\n")
            fb = posts.get("facebook", {})
            f.write(fb.get("post", "") + "\n")
            f.write("Suggested Groups: " +
                    ", ".join(fb.get("suggested_groups", [])) + "\n\n")

            # LinkedIn
            f.write("LINKEDIN POST:\n")
            f.write("-" * 30 + "\n")
            li = posts.get("linkedin", {})
            f.write(li.get("post", "") + "\n\n")

            # Reddit
            f.write("REDDIT POST:\n")
            f.write("-" * 30 + "\n")
            rd = posts.get("reddit", {})
            f.write(f"Title: {rd.get('post_title', '')}\n")
            f.write(f"Body: {rd.get('post_body', '')}\n")
            f.write(f"Comment Template: {rd.get('comment_template', '')}\n")
            subs = rd.get("suggested_subreddits", [])
            f.write(f"Subreddits: {', '.join(subs)}\n\n")

            # Quora
            f.write("QUORA ANSWER:\n")
            f.write("-" * 30 + "\n")
            qr = posts.get("quora", {})
            questions = qr.get("suggested_questions_to_answer", [])
            f.write(f"Questions to answer: {', '.join(questions)}\n")
            f.write(f"Answer template: {qr.get('answer_template', '')}\n\n")

            # Twitter
            f.write("TWITTER/X POST:\n")
            f.write("-" * 30 + "\n")
            tw = posts.get("twitter", {})
            f.write(tw.get("tweet", "") + "\n\n")

        # Reddit opportunities
        if reddit_opps and isinstance(reddit_opps, dict):
            f.write("REDDIT SUBREDDIT OPPORTUNITIES:\n")
            f.write("-" * 30 + "\n")
            for sub in reddit_opps.get("subreddits", []):
                sub_name = sub.get('name', '').replace('r/', '').strip()
                f.write(f"r/{sub_name}\n")
                f.write(f"Reason: {sub.get('reason', '')}\n")
                f.write(f"Comment: {sub.get('sample_comment', '')}\n\n")

        # Quora opportunities
        if quora_opps and isinstance(quora_opps, dict):
            f.write("QUORA QUESTION OPPORTUNITIES:\n")
            f.write("-" * 30 + "\n")
            for q in quora_opps.get("questions", []):
                f.write(f"Question: {q.get('question', '')}\n")
                f.write(f"Answer: {q.get('sample_answer', '')}\n\n")

    print(f"Social media report saved: {filename}")
    return filename


def run_social_media():
    """
    Main social media function.
    Generates distribution content for recent videos.
    """
    print("=" * 55)
    print("ReachIQ AI — Social Media Distribution")
    print(f"Date: {datetime.date.today()}")
    print("=" * 55)

    videos = get_videos(3)

    for video in videos:
        print(f"\n{'=' * 55}")
        print(f"VIDEO: {video['title']}")
        print(f"{'=' * 55}")

        # Generate platform posts
        print("\nGenerating platform posts...")
        keywords = ["AI", "artificial intelligence",
                    "machine learning", "YouTube"]

        posts = generate_platform_posts(
            video_title=video["title"],
            video_url=video["url"],
            keywords=keywords
        )

        # Find Reddit opportunities
        print("Finding Reddit opportunities...")
        reddit_opps = find_reddit_opportunities(keywords)

        # Find Quora opportunities
        print("Finding Quora opportunities...")
        quora_opps = find_quora_opportunities(keywords)

        if posts and isinstance(posts, dict):
            # Preview key outputs
            yt_post = posts.get("youtube_community", {})
            fb_post = posts.get("facebook", {})
            li_post = posts.get("linkedin", {})
            rd_post = posts.get("reddit", {})

            print(f"\nYouTube Community Preview:")
            print(yt_post.get("post", "")[:150] + "...")

            print(f"\nFacebook Suggested Groups:")
            groups = fb_post.get("suggested_groups", [])
            for g in groups[:3]:
                print(f"  - {g}")

            print(f"\nReddit Subreddits:")
            subs = rd_post.get("suggested_subreddits", [])
            for s in subs[:3]:
                s_clean = s.replace("r/", "").strip()
            print(f"  - r/{s_clean}")

            print(f"\nLinkedIn Angle:")
            print(li_post.get("angle", "")[:100])

        # Save full report
        save_social_media_report(
            video["title"],
            video["video_id"],
            posts,
            reddit_opps,
            quora_opps
        )

        print(f"\nDone: {video['title']}")

    print(f"\n{'=' * 55}")
    print("Social media distribution complete.")
    print("Open your report files to copy paste and post.")
    print(f"{'=' * 55}")


if __name__ == "__main__":
    run_social_media()