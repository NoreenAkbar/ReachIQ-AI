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


def self_review(content, content_type="youtube_title"):
    """
    AI critiques its own output.
    Returns score and specific weaknesses.
    """
    prompt = f"""
You are ReachIQ AI self-review system.
Critically evaluate this {content_type} output.
Be strict and honest.

Return ONLY valid JSON, no extra text, no markdown.

FORMAT:
{{
  "score": 0,
  "passes_threshold": false,
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
            return {"score": 5.0, "passes_threshold": False,
                    "weaknesses": ["Could not parse review"],
                    "specific_improvements": ["Retry"]}
    return None


def improve_content(original_content, weaknesses,
                    improvements, content_type, pass_num):
    """
    Generates improved version based on critique.
    """
    prompt = f"""
You are ReachIQ AI improvement engine on pass {pass_num} of {MAX_PASSES}.

Improve this {content_type} by fixing the specific weaknesses identified.
Make targeted improvements only — do not change what is already working.

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


def recursive_optimize(initial_content, content_type="youtube_title"):
    """
    Main 3-pass recursive optimization loop.

    Pass 1 — Review initial content, identify weaknesses
    Pass 2 — Improve based on critique
    Pass 3 — Final review and polish

    Stops early if score >= 7.5 threshold.
    Returns full optimization history for transparency.
    """
    history = []
    current_content = initial_content
    final_score = 0

    print(f"Starting recursive optimization for: {content_type}")
    print(f"Max passes: {MAX_PASSES}, Threshold: {IMPROVEMENT_THRESHOLD}")

    for pass_num in range(1, MAX_PASSES + 1):
        print(f"\nPass {pass_num}/{MAX_PASSES}...")

        # Self review current content
        review = self_review(current_content, content_type)

        if not review:
            print(f"Pass {pass_num}: Review failed, stopping.")
            break

        score = review.get("score", 0)
        passes = review.get("passes_threshold", False)
        weaknesses = review.get("weaknesses", [])
        improvements = review.get("specific_improvements", [])
        final_score = score

        history.append({
            "pass": pass_num,
            "content": current_content,
            "score": score,
            "passes_threshold": passes,
            "weaknesses": weaknesses,
            "improvements_suggested": improvements
        })

        print(f"Pass {pass_num} score: {score}/10")

        # Stop if threshold met
        if passes or score >= IMPROVEMENT_THRESHOLD:
            print(f"Threshold met at pass {pass_num}. Stopping.")
            break

        # Stop if last pass
        if pass_num == MAX_PASSES:
            print("Max passes reached. Using best version.")
            break

        # Generate improvement
        improved = improve_content(
            current_content, weaknesses,
            improvements, content_type, pass_num
        )

        if improved and isinstance(improved, dict):
            new_content = improved.get(
                "improved_content", current_content
            )
            changes = improved.get("changes_made", [])
            history[-1]["changes_made"] = changes
            current_content = new_content
            print(f"Improvements applied: {len(changes)} changes")
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
    """Optimizes a YouTube title through 3-pass loop"""
    return recursive_optimize(title, "youtube_title")


def optimize_description(description):
    """Optimizes a YouTube description through 3-pass loop"""
    return recursive_optimize(description, "youtube_description")


def optimize_hook(hook):
    """Optimizes a video hook through 3-pass loop"""
    return recursive_optimize(hook, "youtube_hook")


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