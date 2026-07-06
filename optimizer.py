import os
import json
from brain import ask_brain, ask_brain_analysis

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ─────────────────────────────────────────────
# REACHIQ AI — RECURSIVE OPTIMIZATION ENGINE
# Max 3 adaptive passes to self-improve output
# Each pass critiques and improves the previous
# Prevents infinite loops and hallucinations
# ─────────────────────────────────────────────

MAX_PASSES = 3
IMPROVEMENT_THRESHOLD = 7.5


def self_review(content, content_type="youtube_title", original_topic=None):
    topic_line = f"\nORIGINAL TOPIC (must stay on this subject): {original_topic}" if original_topic else ""
    prompt = f"""
You are ReachIQ AI self-review system.
Critically evaluate this {content_type} output.
Be strict and honest.
{topic_line}
CRITICAL RULE: If the content has drifted to a different topic/domain than the original topic, set "topic_drift" to true and score to 0.

Return ONLY valid JSON, no extra text, no markdown.

FORMAT:
{{
  "score": 0,
  "passes_threshold": false,
  "topic_drift": false,
  "weaknesses": [],
  "specific_improvements": []
}}

Threshold for passing: score >= 7.5 out of 10

CONTENT TO REVIEW:
{str(content)[:800]}
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
            return {"score": 5.0, "passes_threshold": False, "topic_drift": False,
                    "weaknesses": ["Could not parse review"],
                    "specific_improvements": ["Retry"]}
    return None


def improve_content(original_content, weaknesses, improvements,
                    content_type, pass_num, original_topic=None):
    topic_line = f"\nORIGINAL TOPIC (the improved version MUST stay strictly about this — never switch subject/domain): {original_topic}" if original_topic else ""
    prompt = f"""
You are ReachIQ AI improvement engine on pass {pass_num} of {MAX_PASSES}.

Improve this {content_type} by fixing the specific weaknesses identified.
Make targeted improvements only — do not change what is already working.
{topic_line}
CRITICAL: The improved content must remain about the exact same subject as the original. Never introduce an unrelated topic or domain.

Return ONLY valid JSON, no extra text, no markdown.

FORMAT:
{{
  "improved_content": "",
  "changes_made": [],
  "confidence": 0
}}

ORIGINAL:
{str(original_content)[:500]}

WEAKNESSES TO FIX:
{json.dumps(weaknesses)}

SPECIFIC IMPROVEMENTS TO MAKE:
{json.dumps(improvements)}
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
            return None
    return None

def recursive_optimize(initial_content, content_type="youtube_title", original_topic=None):
    history = []
    current_content = initial_content
    final_score = 0
    original_topic = original_topic or initial_content

    print(f"Starting recursive optimization for: {content_type}")

    for pass_num in range(1, MAX_PASSES + 1):
        print(f"\nPass {pass_num}/{MAX_PASSES}...")

        review = self_review(current_content, content_type, original_topic)
        if not review:
            print(f"Pass {pass_num}: Review failed, stopping.")
            break

        if review.get("topic_drift"):
            print(f"Pass {pass_num}: Topic drift detected, discarding this iteration.")
            history.append({
                "pass": pass_num, "content": current_content, "score": 0,
                "passes_threshold": False, "weaknesses": ["Topic drift detected - discarded"],
                "improvements_suggested": [], "rejected": True
            })
            continue  # retry same pass content, don't advance current_content

        score = review.get("score", 0)
        passes = review.get("passes_threshold", False)
        weaknesses = review.get("weaknesses", [])
        improvements = review.get("specific_improvements", [])
        final_score = score

        history.append({
            "pass": pass_num, "content": current_content, "score": score,
            "passes_threshold": passes, "weaknesses": weaknesses,
            "improvements_suggested": improvements
        })

        print(f"Pass {pass_num} score: {score}/10")

        if passes or score >= IMPROVEMENT_THRESHOLD:
            print(f"Threshold met at pass {pass_num}. Stopping.")
            break
        if pass_num == MAX_PASSES:
            print("Max passes reached. Using best version.")
            break

        improved = improve_content(current_content, weaknesses, improvements,
                                   content_type, pass_num, original_topic)
        if improved and isinstance(improved, dict):
            new_content = improved.get("improved_content", current_content)
            history[-1]["changes_made"] = improved.get("changes_made", [])
            current_content = new_content
            print(f"Improvements applied.")
        else:
            print("Could not generate improvements. Using current.")
            break

    return {
        "original_content": initial_content,
        "final_content": current_content,
        "final_score": final_score,
        "passes_completed": len(history),
        "threshold_met": final_score >= IMPROVEMENT_THRESHOLD,
        "history": history
    }


def optimize_title(title):
    return recursive_optimize(title, "youtube_title", original_topic=title)

def optimize_description(description):
    return recursive_optimize(description, "youtube_description", original_topic=description)

def optimize_hook(hook, topic=None):
    return recursive_optimize(hook, "youtube_hook", original_topic=topic or hook)


if __name__ == "__main__":
    print("=" * 55)
    print("ReachIQ AI — Recursive Optimization Engine Test")
    print("=" * 55)

    test_title = "How AI is Changing Education"
    print(f"\nOptimizing title: {test_title}")

    result = optimize_title(test_title)

    print(f"\nOriginal: {result['original_content']}")
    print(f"Final: {result['final_content']}")
    print(f"Final Score: {result['final_score']}/10")
    print(f"Passes: {result['passes_completed']}")
    print(f"Threshold Met: {result['threshold_met']}")

    print("\nOptimization History:")
    for h in result["history"]:
        print(f"\nPass {h['pass']}:")
        print(f"  Score: {h['score']}/10")
        print(f"  Weaknesses: {h['weaknesses']}")