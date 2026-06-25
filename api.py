import os
import json
import datetime
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

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