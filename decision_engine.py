import json
from brain import ask_brain
from scorer import score_video
from analyzer import analyze_pre_upload
from keyword_tracker import extract_keywords
from optimizer import optimize_title, optimize_hook
from memory import get_smart_suggestions, store_video_performance


def run_pre_upload_decision(title, description, tags, script=None, niche_context=None):
    """
    Orchestrates all Pre-Upload modules, then synthesizes
    one unified strategic recommendation.
    niche_context=None is a placeholder for future RAG fusion.
    """
    score = score_video(title, description, tags)
    analysis = analyze_pre_upload(title, description, tags, script)
    keywords = extract_keywords(title, description)
    smart_suggestions = get_smart_suggestions(context=title)
    optimizer_result = optimize_title(title)
    hook_result = optimize_hook(script, topic=title) if script else None

    store_video_performance(
        video_id=f"preupload_{title[:30]}",
        title=title,
        stats={},
        suggestions=analysis if isinstance(analysis, dict) else {}
    )

    modules = {
        "score": score,
        "analysis": analysis,
        "keywords": keywords,
        "smart_suggestions": smart_suggestions,
        "optimizer_result": optimizer_result,
        "hook_result": hook_result
    }

    synthesis_prompt = f"""
You are the ReachIQ AI Decision Engine — a senior YouTube growth strategist.
You have outputs from multiple specialist modules for one video. Synthesize them
into ONE unified strategic recommendation. Reference multiple modules together
in your reasoning (e.g. "thumbnail is fine but title is the bottleneck because
channel memory shows similar titles underperformed"). Do not just list scores.
Explicitly cite channel memory history when relevant instead of generic advice.

Return ONLY valid JSON, no extra text, no markdown.

FORMAT:
{{
  "headline_verdict": "",
  "primary_bottleneck": "",
  "reasoning": "",
  "recommended_priority_order": [],
  "channel_memory_context": "",
  "final_action_plan": []
}}

CONTENT SCORE: {json.dumps(score)}
CONTENT ANALYSIS: {json.dumps(analysis) if isinstance(analysis, dict) else str(analysis)[:800]}
KEYWORDS: {json.dumps(keywords) if isinstance(keywords, dict) else str(keywords)[:400]}
CHANNEL MEMORY SUGGESTIONS: {json.dumps(smart_suggestions) if isinstance(smart_suggestions, dict) else str(smart_suggestions)[:800]}
TITLE OPTIMIZER RESULT: {json.dumps(optimizer_result) if isinstance(optimizer_result, dict) else str(optimizer_result)[:500]}
"""

    synthesis_raw = ask_brain(synthesis_prompt)
    strategic_report = None
    if synthesis_raw:
        try:
            clean = synthesis_raw.strip()
            if "```" in clean:
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            strategic_report = json.loads(clean)
        except:
            strategic_report = {"headline_verdict": synthesis_raw}

    return {
        "strategic_report": strategic_report,
        "modules": modules
    }