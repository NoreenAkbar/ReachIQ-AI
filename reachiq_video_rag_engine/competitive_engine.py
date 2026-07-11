from reachiq_video_rag_engine.query import (
    retrieve_hook_chunks,
    retrieve_cta_chunks,
    retrieve_structure_chunks,
    retrieve_thumbnail_chunks,
    retrieve_trend_chunks,
)

from reachiq_video_rag_engine.llm_provider import ask_llm
from reachiq_video_rag_engine.query import extract_primary_niche
niche = extract_primary_niche(niche)
import json


class CompetitiveIntelligenceEngine:

    def __init__(self):
        pass

    def analyze(self, niche: str, video_id=None):

        hook_chunks = retrieve_hook_chunks(niche)

        cta_chunks = retrieve_cta_chunks(niche)

        structure_chunks = retrieve_structure_chunks(niche)

        thumbnail_chunks = retrieve_thumbnail_chunks(niche)

        trend_chunks = retrieve_trend_chunks(niche)
        
        def format_evidence(chunks):
            formatted = []
            for c in chunks:
                formatted.append(f"""
====================================

Video Title:
{c.get("title")}

Channel:
{c.get("channel_name")}

Views:
{c.get("views")}

Duration:
{round(c.get("duration_seconds",0)/60,1)} minutes

Similarity:
{round(c.get("similarity",0),3)}

Transcript Evidence:

{c.get("chunk_text")}

====================================
""")
            return "\n".join(formatted)

        prompt = f"""
You are the world's best YouTube Competitive Intelligence Strategist.

Your job is NOT to summarize.

Your job is to reverse-engineer why videos succeed.

You are given raw evidence retrieved from semantically similar high-performing competitor videos.

These are NOT summaries.

Each evidence block includes:

• Video title

• Channel

• View count

• Video duration

• Semantic similarity

• Transcript evidence

You MUST use ALL metadata.

High-view videos deserve higher analytical weight.

If multiple high-performing videos agree on the same pattern, treat it as a high-confidence market signal.

If only low-view videos show a pattern, mention that confidence is lower.

Always explain WHY a pattern works using psychology, not observation alone.
Think like McKinsey + YouTube Growth Engineer + Consumer Psychologist.

Never summarize.

Reverse engineer.

Infer.

Generalize.

Find hidden patterns.

Rank evidence by strength.

Ignore weak evidence.

Only use patterns supported by multiple videos unless explicitly stated.

First infer patterns from the evidence.

Then combine all evidence into one coherent market intelligence report.

Never analyze each evidence source independently.

Think globally across every retrieved chunk.

========================

HOOK EVIDENCE

{format_evidence(hook_chunks)}

========================

CTA EVIDENCE

{format_evidence(cta_chunks)}

========================

STRUCTURE EVIDENCE

{format_evidence(structure_chunks)}

========================

THUMBNAIL EVIDENCE

{thumbnail_chunks}

========================

TREND EVIDENCE

{trend_chunks}

========================

Your task:

1. Explain WHY these videos succeed.

2. Discover hidden psychological patterns.

3. Discover recurring storytelling frameworks.

4. Identify retention techniques.

5. Identify thumbnail psychology.

6. Identify emotional triggers.

7. Identify audience expectations.

8. Predict what type of future videos will likely outperform.

9. Recommend how ReachIQ should optimize future videos.

Return ONLY JSON.

{{
    "executive_summary": "",
    "hook_intelligence": {{}},
    "structure_intelligence": {{}},
    "cta_intelligence": {{}},
    "thumbnail_intelligence": {{}},
    "trend_intelligence": {{}},
    "viewer_psychology": {{}},
    "content_gaps": [],
    "competitive_advantages": [],
    "future_opportunities": [],
    "recommended_video_blueprint": {{
        "title_style": "",
        "opening_strategy": "",
        "content_structure": "",
        "thumbnail_strategy": "",
        "cta_strategy": ""
    }},
    "confidence_score": 0
}}
"""

        response = ask_llm(prompt)

        try:
            intelligence = json.loads(response)

            strategic = self.strategic_reasoning(intelligence)

            try:
                intelligence["strategic_reasoning"] = json.loads(strategic)
            except Exception:
                intelligence["strategic_reasoning"] = strategic

            # --------------------------
            # Summary fields
            # --------------------------

            hook_pattern = str(intelligence.get("hook_intelligence", ""))

            cta_pattern = str(intelligence.get("cta_intelligence", ""))

            pacing_notes = str(intelligence.get("structure_intelligence", ""))

            # --------------------------
            # Viral Score
            # --------------------------

            viral_score = 0

            if intelligence.get("hook_intelligence"):
                viral_score += 20

            if intelligence.get("thumbnail_intelligence"):
                viral_score += 20

            if intelligence.get("trend_intelligence"):
                viral_score += 20

            if intelligence.get("structure_intelligence"):
                viral_score += 20

            if intelligence.get("strategic_reasoning"):
                viral_score += 20
            if video_id:
                from reachiq_video_rag_engine.storage import insert_competitor_insight

                insert_competitor_insight(
                    video_id=video_id,
                    niche=niche,
                    hook_pattern=hook_pattern,
                    cta_pattern=cta_pattern,
                    pacing_notes=pacing_notes,
                    viral_score=viral_score,
                    strategic_report=intelligence
            )

            return intelligence

        except Exception:
            return {
                "raw_response": response
            }

    def strategic_reasoning(self, intelligence):

        prompt = f"""
You are ReachIQ's Chief Competitive Intelligence Strategist.

Below is structured intelligence extracted from multiple successful competitors.

Your task is NOT to summarize.

Think like a YouTube growth consultant hired for $100,000.

Produce strategic recommendations.

Answer these:

1. What invisible patterns separate winners from average creators?

2. Which psychological triggers repeatedly appear?

3. Which content structures outperform?

4. Which thumbnail philosophy wins?

5. Which CTA philosophy wins?

6. Which opportunities are still underserved?

7. What mistakes should creators avoid?

8. If you had to build ONE viral video tomorrow,
describe it in complete detail.

Return ONLY JSON.

{{
    "market_summary":"",
    "hidden_patterns":[],
    "psychological_principles":[],
    "winning_framework":[],
    "thumbnail_formula":[],
    "hook_formula":[],
    "content_formula":[],
    "cta_formula":[],
    "market_gaps":[],
    "high_confidence_predictions":[],
    "viral_video_blueprint":{{
        "title":"",
        "thumbnail":"",
        "opening":"",
        "storytelling":"",
        "cta":""
    }}
}}

INTELLIGENCE

{intelligence}
"""

        return ask_llm(prompt)