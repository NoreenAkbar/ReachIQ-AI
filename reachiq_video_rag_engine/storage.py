from supabase import create_client
from reachiq_video_rag_engine.config import SUPABASE_URL, SUPABASE_SERVICE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def insert_video(video_url, title, channel_name, niche, duration_seconds, views):
    result = supabase.table("videos").insert({
        "video_url": video_url,
        "title": title,
        "channel_name": channel_name,
        "niche": niche,
        "duration_seconds": duration_seconds,
        "views": views
    }).execute()
    return result.data[0]["id"]


def insert_transcript(video_id, full_text):
    supabase.table("transcripts").insert({
        "video_id": video_id,
        "full_text": full_text
    }).execute()


def insert_chunk(video_id, chunk_text, start_time, end_time, chunk_type):
    result = supabase.table("chunks").insert({
        "video_id": video_id,
        "chunk_text": chunk_text,
        "start_time": start_time,
        "end_time": end_time,
        "chunk_type": chunk_type
    }).execute()
    return result.data[0]["id"]


def insert_embedding(chunk_id, embedding):
    supabase.table("embeddings").insert({
        "chunk_id": chunk_id,
        "embedding": embedding
    }).execute()


def insert_scene(video_id, scene_index, start_time, end_time, description):
    supabase.table("scene_analysis").insert({
        "video_id": video_id,
        "scene_index": scene_index,
        "start_time": start_time,
        "end_time": end_time,
        "description": description
    }).execute()


def insert_thumbnail_analysis(video_id, ocr_text, visual_description):
    supabase.table("thumbnail_analysis").insert({
        "video_id": video_id,
        "ocr_text": ocr_text,
        "visual_description": visual_description
    }).execute()


def insert_competitor_insight(
    video_id,
    niche,
    hook_pattern,
    cta_pattern,
    pacing_notes,
    viral_score,
    strategic_report
):

    supabase.table("competitor_insights").insert({

        "video_id": video_id,
        "niche": niche,
        "hook_pattern": hook_pattern,
        "cta_pattern": cta_pattern,
        "pacing_notes": pacing_notes,
        "viral_score": viral_score,
        "strategic_report": strategic_report

    }).execute()


def get_videos_by_niche(niche, limit=10):
    result = supabase.table("videos").select("*").eq("niche", niche).limit(limit).execute()
    return result.data
