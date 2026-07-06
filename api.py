import os
import json
import datetime
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, BackgroundTasks, UploadFile, File

from social_media import generate_platform_posts

os.chdir(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(title="ReachIQ AI API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
def root():
    return {"status": "ReachIQ AI API running", 
            "version": "1.0"}


@app.get("/health")
def health():
    return {"status": "healthy", 
            "timestamp": datetime.datetime.now().isoformat()}


@app.post("/run-weekly-monitor")
async def run_weekly_monitor(background_tasks: BackgroundTasks,
                              weeks_ago: int = 0):
    """
    Triggered by n8n every 7 days.
    weeks_ago=0 means current week, 1 means last week etc.
    """
    background_tasks.add_task(weekly_monitor_task, weeks_ago)
    return {"status": "started", 
            "weeks_ago": weeks_ago,
            "message": "Weekly monitor running in background"}


def weekly_monitor_task(weeks_ago: int = 0):
    try:
        from youtube_api import get_videos, get_video_stats
        from metadata_updater import generate_updated_metadata
        from memory import store_video_performance

        # Calculate date range
        today = datetime.date.today()
        week_start = today - datetime.timedelta(
            days=today.weekday() + (weeks_ago * 7)
        )
        week_end = week_start + datetime.timedelta(days=6)

        print(f"Running weekly monitor: "
              f"{week_start} to {week_end}")

        videos = get_videos(10)
        results = []

        for video in videos:
            stats = get_video_stats(video["video_id"])
            if not stats:
                continue

            metadata = generate_updated_metadata(
                video_title=video["title"],
                current_description="",
                current_tags="",
                analytics_data=stats
            )

            store_video_performance(
                video_id=video["video_id"],
                title=video["title"],
                stats=stats if isinstance(stats, dict) else {},
                suggestions=metadata if isinstance(
                    metadata, dict) else {}
            )

            results.append({
                "video_id": video["video_id"],
                "title": video["title"],
                "views": stats.get("views", 0) if isinstance(
                    stats, dict) else 0
            })

        # Save weekly report
        os.makedirs("reports", exist_ok=True)
        report_file = os.path.join(
            "reports",
            f"weekly_report_{week_start}.json"
        )
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump({
                "week": str(week_start),
                "videos_processed": len(results),
                "results": results,
                "generated": datetime.datetime.now().isoformat()
            }, f, indent=2)

        print(f"Weekly monitor complete. "
              f"Processed {len(results)} videos.")

    except Exception as e:
        print(f"Weekly monitor error: {e}")


@app.get("/reports")
def get_reports():
    """Returns list of all generated reports"""
    reports_dir = "reports"
    if not os.path.exists(reports_dir):
        return {"reports": []}
    files = os.listdir(reports_dir)
    return {"reports": sorted(files, reverse=True)}


@app.get("/memory/patterns")
def get_patterns():
    """Returns channel patterns from memory"""
    from memory import get_channel_patterns
    patterns = get_channel_patterns()
    return {"patterns": patterns}


@app.get("/memory/suggestions")
def get_suggestions(context: str = "general"):
    """Returns smart suggestions from memory"""
    from memory import get_smart_suggestions
    suggestions = get_smart_suggestions(context)
    return {"suggestions": suggestions}
@app.post("/track-keywords")
async def track_keywords(payload: dict):
    from keyword_tracker import extract_keywords, find_competing_videos
    video_title = payload.get("videoTitle", "")
    keywords = payload.get("keywords", [])
    
    results = {}
    for kw in keywords[:5]:
        competitors = find_competing_videos(kw, max_results=5)
        results[kw] = competitors
    
    extracted = extract_keywords(video_title)
    return {
        "status": "complete",
        "extracted_keywords": extracted,
        "competitor_analysis": results
    }

@app.post("/track-keywords-weekly")
async def track_keywords_weekly(background_tasks: BackgroundTasks):
    background_tasks.add_task(weekly_keyword_task)
    return {"status": "started", "message": "Weekly keyword tracking running"}

def weekly_keyword_task():
    try:
        from youtube_api import get_videos
        from keyword_tracker import extract_keywords, find_competing_videos
        import json, os
        
        videos = get_videos(10)
        all_keywords = {}
        
        for video in videos:
            keywords = extract_keywords(video["title"])
            if keywords and isinstance(keywords, dict):
                primary = keywords.get("primary_keywords", [])
                all_keywords[video["title"]] = primary
        
        os.makedirs("reports", exist_ok=True)
        with open("reports/weekly_keywords.json", "w") as f:
            json.dump({
                "date": datetime.datetime.now().isoformat(),
                "keywords": all_keywords
            }, f, indent=2)
            
        print("Weekly keyword tracking complete.")
    except Exception as e:
        print(f"Keyword tracking error: {e}")
        @app.post("/generate-post-drafts")
        async def generate_post_drafts(payload: dict):
            from social_media import generate_platform_posts
            from keyword_tracker import extract_keywords
    
            video_title = payload.get("videoTitle", "")
            video_url = payload.get("videoUrl", "")
            keywords = payload.get("keywords", [])
    
            if not keywords and video_title:
                extracted = extract_keywords(video_title)
                if extracted and isinstance(extracted, dict):
                    keywords = extracted.get("primary_keywords", [])
    
            posts = generate_platform_posts(
                video_title=video_title,
                video_url=video_url,
                keywords=keywords
    )
    
            return {
        "status": "complete",
        "posts": posts
    }
@app.post("/find-distribution")
async def find_distribution(payload: dict):
    from social_media import find_reddit_opportunities, find_quora_opportunities
    from keyword_tracker import find_distribution_opportunities
    
    video_title = payload.get("videoTitle", "")
    video_url = payload.get("videoUrl", "")
    keywords = payload.get("keywords", [])
    
    reddit = find_reddit_opportunities(keywords[:3])
    quora = find_quora_opportunities(keywords[:3])
    yt_opps = find_distribution_opportunities(keywords[:3])
    
    return {
        "status": "complete",
        "reddit": reddit,
        "quora": quora,
        "youtube_opportunities": yt_opps,
        "video_title": video_title,
        "video_url": video_url
    }

@app.post("/find-distribution-weekly")
async def find_distribution_weekly(background_tasks: BackgroundTasks):
    background_tasks.add_task(weekly_distribution_task)
    return {"status": "started", 
            "message": "Weekly distribution finder running"}

def weekly_distribution_task():
    try:
        from youtube_api import get_videos
        from keyword_tracker import extract_keywords, find_distribution_opportunities
        from social_media import find_reddit_opportunities
        import json, os
        
        videos = get_videos(5)
        all_opportunities = {}
        
        for video in videos:
            keywords = extract_keywords(video["title"])
            if keywords and isinstance(keywords, dict):
                primary = keywords.get("primary_keywords", [])
                reddit = find_reddit_opportunities(primary[:3])
                yt_opps = find_distribution_opportunities(primary[:3])
                all_opportunities[video["title"]] = {
                    "reddit": reddit,
                    "youtube": yt_opps
                }
        
        os.makedirs("reports", exist_ok=True)
        with open("reports/weekly_distribution.json", "w") as f:
            json.dump({
                "date": datetime.datetime.now().isoformat(),
                "opportunities": all_opportunities
            }, f, indent=2)
            
        print("Weekly distribution finder complete.")
    except Exception as e:
        print(f"Distribution finder error: {e}")  
@app.post("/pre-upload")
async def pre_upload_analysis(payload: dict):
    from decision_engine import run_pre_upload_decision

    title = payload.get("title", "")
    description = payload.get("description", "")
    tags = payload.get("tags", "")
    script = payload.get("script", "")
    groq_key = payload.get("groq_key", "")
    niche_context = payload.get("niche_context", None)

    if groq_key:
        os.environ["GROQ_API_KEY"] = groq_key

    result = run_pre_upload_decision(
        title, description, tags,
        script=script or None,
        niche_context=niche_context
    )

    return {
        "status": "complete",
        "strategic_report": result["strategic_report"],
        "modules": result["modules"]
    }
@app.post("/thumbnail-analysis")
async def thumbnail_analysis(file: UploadFile = File(...), title: str = "", description: str = ""):
    import base64
    import json_repair

    img_bytes = await file.read()
    img_b64 = base64.b64encode(img_bytes).decode("utf-8")
    ext = (file.filename or "thumb.jpg").split(".")[-1].lower()
    media_type = f"image/{'jpeg' if ext in ['jpg', 'jpeg'] else 'png'}"
    data_url = f"data:{media_type};base64,{img_b64}"

    thumb_prompt = f"""Analyze this YouTube thumbnail STRICTLY against the video's title and description. Be harsh — do not rationalize unrelated branding/logos as "supporting" the topic.

VIDEO TITLE: {title}
VIDEO DESCRIPTION: {description}

If the thumbnail shows a generic logo, brand mark, or content unrelated to the specific topic in the title, you MUST flag it as a mismatch — do not praise it as "reinforcing brand" instead.

Return ONLY this JSON:
{{"visibility_score": 7, "text_readability": "describe text quality", "emotional_impact": "describe emotion", "color_contrast": "describe colors", "ctr_prediction": "estimated CTR%", "title_thumbnail_match": "state clearly yes/no and why", "mismatch_warning": "if thumbnail does not depict the video's actual topic/subject, state this explicitly here, otherwise empty string", "suggested_improvements": ["improvement 1", "improvement 2", "improvement 3"]}}"""

    raw = None
    try:
        from groq import Groq as _Groq
        from config import GROQ_API_KEY
        _groq = _Groq(api_key=GROQ_API_KEY)
        _resp = _groq.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": data_url}},
                {"type": "text", "text": thumb_prompt}
            ]}],
            max_tokens=1000,
            temperature=0.1
        )
        raw = _resp.choices[0].message.content
    except Exception as e:
        print(f"Groq vision failed: {e}")

    if not raw:
        try:
            import httpx
            from config import AIML_API_KEY
            _resp2 = httpx.post(
                "https://api.aimlapi.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {AIML_API_KEY}",
                         "Content-Type": "application/json"},
                json={"model": "meta-llama/Llama-Vision-Free",
                      "messages": [{"role": "user", "content": [
                          {"type": "image_url", "image_url": {"url": data_url}},
                          {"type": "text", "text": thumb_prompt}
                      ]}], "max_tokens": 1000, "temperature": 0.1},
                timeout=60
            )
            raw = _resp2.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"AI/ML API failed: {e}")

    if not raw:
        from brain import ask_brain
        raw = ask_brain(
            """Return ONLY this JSON for a YouTube thumbnail analysis:
{"visibility_score": 6, "text_readability": "Clear text visible", "emotional_impact": "Neutral to positive", "color_contrast": "Adequate contrast", "ctr_prediction": "5-7% estimated", "suggested_improvements": ["Add human face for higher CTR", "Use bolder contrasting font", "Increase visual hierarchy"]}"""
        )

    try:
        clean = (raw or "").strip()
        for sep in ["```json", "```"]:
            if sep in clean:
                for p in clean.split(sep):
                    p = p.strip().rstrip("`")
                    if p.startswith("{"):
                        clean = p
                        break
        thumb_data = json_repair.loads(clean)
    except Exception:
        thumb_data = {
            "visibility_score": 6,
            "text_readability": (raw or "")[:300],
            "emotional_impact": "Completed",
            "color_contrast": "Check output",
            "ctr_prediction": "4-6% estimated",
            "title_thumbnail_match": "Not analyzed",
            "mismatch_warning": "",
            "suggested_improvements": ["Increase contrast", "Add face element", "Bolder text"]
        }
        from memory import store_video_performance
        store_video_performance(
            video_id=f"thumb_{title[:30]}",
            title=title,
            stats={},
            suggestions={"thumbnail_analysis": thumb_data}
        )

    return {"status": "complete", "analysis": thumb_data}        