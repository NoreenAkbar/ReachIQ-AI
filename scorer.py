from brain import ask_brain
import json

def score_video(title, description, tags, thumbnail_text=""):
    """
    Scores a video across 6 dimensions.
    Returns a clear number to track improvement over time.
    """

    prompt = f"""
You are ReachIQ AI scoring a YouTube video before upload.
Score each dimension from 0 to 10.
Be strict and honest.

Return ONLY valid JSON, no extra text, no markdown.

FORMAT:
{{
  "scores": {{
    "ctr_psychology": 0,
    "packaging_style": 0,
    "virality_potential": 0,
    "emotional_trigger": 0,
    "clarity": 0,
    "searchability": 0
  }},
  "total_score": 0,
  "grade": "",
  "verdict": "",
  "priority_fix": ""
}}

Grades: A (85-100), B (70-84), C (55-69), D (below 55)

TITLE: {title}
DESCRIPTION: {description}
TAGS: {tags}
THUMBNAIL TEXT: {thumbnail_text}
"""

    print("Scoring video...")
    result = ask_brain(prompt)

    if result:
        try:
            clean = result.strip()
            if "```" in clean:
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            parsed = json.loads(clean)
            parsed["scores"]["total_score"] = parsed.get("total_score", 0)
            return parsed
        except:
            return result
    return None


if __name__ == "__main__":
    print("=" * 50)
    print("ReachIQ AI — Content Scorer")
    print("=" * 50)

    result = score_video(
        title="How AI is Changing Education Forever",
        description="In this video we explore how AI is transforming the way students learn.",
        tags="AI, education, students, future, machine learning",
        thumbnail_text="AI Revolution"
    )

    if result:
        print(json.dumps(result, indent=2))
        print("\n" + "=" * 50)
        print(f"TOTAL SCORE: {result.get('total_score', 0)}/100")
        print(f"GRADE: {result.get('grade', 'N/A')}")
        print(f"VERDICT: {result.get('verdict', 'N/A')}")
        print(f"PRIORITY FIX: {result.get('priority_fix', 'N/A')}")