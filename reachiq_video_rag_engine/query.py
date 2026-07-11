from sentence_transformers import SentenceTransformer
from reachiq_video_rag_engine.storage import supabase
from reachiq_video_rag_engine.llm_provider import ask_llm

embedding_model = SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")

def extract_primary_niche(niche_input):
    """Takes first 1-2 significant words as the primary niche for matching."""
    words = niche_input.strip().split()
    return " ".join(words[:2]) if len(words) > 1 else words[0]

def get_chunks_for_niche(niche, limit=50):
    videos = supabase.table("videos").select("id").ilike("niche", f"%{niche}%").execute().data
    video_ids = [v["id"] for v in videos]
    if not video_ids:
        return []
    chunks = supabase.table("chunks").select("*").in_("video_id", video_ids).limit(limit).execute().data
    return chunks

def semantic_search(query, threshold=0.45, limit=20):

    query_embedding = embedding_model.encode(
        query,
        convert_to_numpy=True
    ).tolist()

    result = (
        supabase.rpc(
            "match_embeddings",
            {
                "query_embedding": query_embedding,
                "match_threshold": threshold,
                "match_count": limit,
            },
        )
        .execute()
    )

    return result.data

def retrieve_hook_chunks(niche):

    hook_chunks = semantic_search(
        f"viral YouTube opening hooks in {niche}",
        limit=25
    )

    return hook_chunks

    prompt = f"""
You are one of the world's best YouTube growth strategists.

Below are the first 15 seconds from high-performing YouTube videos in the niche "{niche}".

Analyze them deeply.

For every hook identify:

1. Psychological trigger
2. Curiosity gap used
3. Emotional trigger
4. Opening sentence pattern
5. Retention strategy
6. Vocabulary patterns
7. Why viewers keep watching

Finally produce a reusable hook framework.

Return ONLY valid JSON.

{{
  "psychological_triggers": [],
  "curiosity_patterns": [],
  "opening_templates": [],
  "retention_strategies": [],
  "common_vocabulary": [],
  "best_examples": [],
  "recommended_hook_framework": ""
}}

HOOKS:
{chr(10).join([x["chunk_text"] for x in hook_chunks])}
"""
    return semantic_search(
        f"opening hook first 30 seconds {niche}",
        limit=20
    )


def retrieve_cta_chunks(niche):
    chunks = get_chunks_for_niche(niche)
    end_chunks = semantic_search(
    f"YouTube subscribe call to action in {niche}"
)
    if not end_chunks:
        return None

    prompt = f"""
You are analyzing high-performing YouTube videos.

Study these ending segments.

Determine:

1. How creators ask for subscribers.
2. Whether they ask for comments.
3. Whether they use urgency.
4. Whether they offer lead magnets.
5. Whether they redirect viewers to another video.
6. Which CTA style appears strongest.

Return ONLY JSON.

{{
  "cta_types": [],
  "subscriber_patterns": [],
  "comment_patterns": [],
  "urgency_patterns": [],
  "lead_magnet_patterns": [],
  "recommended_cta": ""
}}

SEGMENTS

{chr(10).join([x["chunk_text"] for x in end_chunks])}
"""
    return semantic_search(
        f"YouTube subscribe call to action in {niche}",
        limit=20
    )


def retrieve_structure_chunks(niche):
    videos = supabase.table("videos").select("id").ilike("niche", f"%{niche}%").execute().data
    video_ids = [v["id"] for v in videos]
    if not video_ids:
        return None

    scenes = supabase.table("scene_analysis").select("*").in_("video_id", video_ids).execute().data
    scene_counts = {}
    for s in scenes:
        scene_counts[s["video_id"]] = scene_counts.get(s["video_id"], 0) + 1

    prompt = f"""
You are a YouTube retention expert.

These numbers represent scene cuts detected from successful videos.

Infer:

1. Average pacing.
2. Whether pacing is slow, medium or fast.
3. Estimated scene duration.
4. Whether the videos maintain high viewer attention.
5. Recommended pacing for new creators.

Return ONLY JSON.

{{
  "average_scene_changes": 0,
  "pacing": "",
  "estimated_scene_duration_seconds": 0,
  "viewer_retention_style": "",
  "recommendation": ""
}}

SCENE COUNTS

{list(scene_counts.values())}
"""
    return semantic_search(
        f"video structure pacing storytelling {niche}",
        limit=20
    )


def retrieve_thumbnail_chunks(niche):
    videos = supabase.table("videos").select("id").ilike("niche", f"%{niche}%").execute().data
    video_ids = [v["id"] for v in videos]

    if not video_ids:
        return None

    thumbs = (
        supabase.table("thumbnail_analysis")
        .select("*")
        .in_("video_id", video_ids)
        .execute()
        .data
    )

    if not thumbs:
        return None

    prompt = f"""
You are an elite YouTube thumbnail strategist.

Below are OCR results extracted from thumbnails belonging to successful YouTube videos.

Analyze:

1. Common words
2. Average text length
3. Emotional language
4. Curiosity words
5. Call-to-action words
6. Visual messaging strategy
7. Best practices for thumbnails in this niche

Return ONLY JSON.

{{
    "common_words": [],
    "curiosity_words": [],
    "emotional_words": [],
    "average_text_length": 0,
    "thumbnail_strategy": "",
    "recommendation": ""
}}

OCR DATA

{chr(10).join([t["ocr_text"] or "" for t in thumbs])}
"""

    return semantic_search(
        f"YouTube thumbnail title visual strategy {niche}",
        limit=20
    )

def retrieve_trend_chunks(niche):

    trend_chunks = semantic_search(
    f"popular topics and trends in {niche}",
    limit=30
)

    if not trend_chunks:
        return None

    prompt = f"""
You are an AI YouTube Competitive Intelligence system.

Analyze these successful videos.

Identify:

1. Trending topics
2. Repeated title structures
3. Frequently used keywords
4. High-performing content angles
5. Content gaps
6. Opportunities creators are missing

Return ONLY JSON.

{{
    "trending_topics": [],
    "title_patterns": [],
    "high_frequency_keywords": [],
    "content_angles": [],
    "content_gaps": [],
    "opportunities": []
}}

VIDEOS

{chr(10).join([x["chunk_text"] for x in trend_chunks])}
"""

    return semantic_search(
        f"popular trends topics future opportunities {niche}",
        limit=30
    )

def get_niche_intelligence(niche):
    """
    Single entry point combining all query functions.
    Used by Streamlit's final recommendation step.
    Returns None gracefully if no data indexed yet.
    """
    videos = supabase.table("videos").select("id").ilike("niche", f"%{niche}%").execute().data
    if not videos:
        return None

    return {

    "hook_chunks": retrieve_hook_chunks(niche),

    "cta_chunks": retrieve_cta_chunks(niche),

    "structure_chunks": retrieve_structure_chunks(niche),

    "thumbnail_chunks": retrieve_thumbnail_chunks(niche),

    "trend_chunks": retrieve_trend_chunks(niche)

}