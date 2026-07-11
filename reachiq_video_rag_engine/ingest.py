import os
import yt_dlp
import whisper
from scenedetect import detect, ContentDetector
import easyocr
from reachiq_video_rag_engine.storage import (
    insert_video,
    insert_transcript,
    insert_chunk,
    insert_embedding,
    insert_scene,
    insert_thumbnail_analysis,
)
from sentence_transformers import SentenceTransformer

whisper_model = whisper.load_model("base")
ocr_reader = easyocr.Reader(['en'])
embedding_model = SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")

def download_video(video_url, output_dir="downloads"):
    os.makedirs(output_dir, exist_ok=True)
    ydl_opts = {
        "format": "best[height<=480]",
        "outtmpl": f"{output_dir}/%(id)s.%(ext)s",
        "writethumbnail": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)
        return {
            "path": ydl.prepare_filename(info),
            "title": info.get("title"),
            "channel": info.get("channel"),
            "duration": info.get("duration"),
            "views": info.get("view_count"),
            "thumbnail": info.get("thumbnail")
        }


def transcribe(video_path):
    result = whisper_model.transcribe(video_path)
    return result["text"], result["segments"]


def detect_scenes(video_path):
    scene_list = detect(video_path, ContentDetector())
    return [
        {"start": s[0].get_seconds(), "end": s[1].get_seconds()}
        for s in scene_list
    ]


def ocr_thumbnail(thumbnail_path):
    if not os.path.exists(thumbnail_path):
        return ""
    results = ocr_reader.readtext(thumbnail_path, detail=0)
    return " ".join(results)


def run_ingest_pipeline(video_url, niche="general"):
    print(f"Downloading: {video_url}")
    meta = download_video(video_url)

    video_id = insert_video(
        video_url=video_url,
        title=meta["title"],
        channel_name=meta["channel"],
        niche=niche,
        duration_seconds=meta["duration"],
        views=meta["views"]
    )

    print("Transcribing...")
    full_text, segments = transcribe(meta["path"])
    insert_transcript(video_id, full_text)

    for seg in segments:
        chunk_id = insert_chunk(
            video_id=video_id,
            chunk_text=seg["text"],
            start_time=seg["start"],
            end_time=seg["end"],
            chunk_type="body"
        )

        try:
            embedding = embedding_model.encode(
                seg["text"],
                convert_to_numpy=True
            ).tolist()

            insert_embedding(chunk_id, embedding)

        except Exception as e:
            print(f"Embedding failed: {e}")

    print("Detecting scenes...")
    scenes = detect_scenes(meta["path"])
    for i, scene in enumerate(scenes):
        insert_scene(video_id, i, scene["start"], scene["end"], "")

    print("OCR on thumbnail...")
    thumb_path = meta["path"].rsplit(".", 1)[0] + ".jpg"
    ocr_text = ocr_thumbnail(thumb_path)
    insert_thumbnail_analysis(video_id, ocr_text, "")

    print(f"Ingest complete for video_id: {video_id}")
    return video_id


if __name__ == "__main__":
    import sys
    url = sys.argv[1] if len(sys.argv) > 1 else input("YouTube URL: ")
    run_ingest_pipeline(url)