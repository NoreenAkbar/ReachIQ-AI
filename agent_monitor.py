import os
import datetime
import json
import time

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ─────────────────────────────────────────────
# REACHIQ AI — MONITOR AGENT
# Role: Post-upload performance tracking specialist
# Receives tasks from BrainAgent via Band
# Handles: analytics, metadata updates, improvement
# ─────────────────────────────────────────────

from youtube_api import get_videos, get_video_stats
from metadata_updater import generate_updated_metadata
from memory import store_video_performance, get_channel_patterns
from observability import trace_agent_action

AGENT_ID = "monitor_agent"
AGENT_NAME = "MonitorAgent"
AGENT_ROLE = "Post-upload performance tracking specialist"
AGENT_VERSION = "1.0"

AGENT_CAPABILITIES = [
    "track_video_performance",
    "generate_metadata_updates",
    "analyze_watch_time",
    "detect_performance_drops",
    "store_performance_memory",
    "generate_next_video_guide"
]


class BandConnection:
    """
    Placeholder Band connection.
    Replace with real Band SDK on June 12.
    """
    def __init__(self):
        self.connected = False
        self.inbox = []
        self.message_log = []
        print(f"{AGENT_NAME} initialized in local mode.")

    def register(self, agent_id, capabilities):
        print(f"[BAND] {agent_id} registered.")
        self.connected = True
        return True

    def send_message(self, to_agent, message_type, payload):
        message = {
            "from": AGENT_ID,
            "to": to_agent,
            "type": message_type,
            "payload": payload,
            "timestamp": datetime.datetime.now().isoformat()
        }
        self.message_log.append(message)
        _log_message(message)
        return message

    def receive_message(self):
        if self.inbox:
            return self.inbox.pop(0)
        return None

    def simulate_incoming(self, from_agent,
                          task_type, payload):
        message = {
            "from": from_agent,
            "to": AGENT_ID,
            "type": task_type,
            "payload": payload,
            "timestamp": datetime.datetime.now().isoformat()
        }
        self.inbox.append(message)
        return message


def _log_message(message):
    os.makedirs("logs", exist_ok=True)
    log_file = os.path.join(
        "logs",
        f"band_messages_{datetime.date.today()}.json"
    )
    logs = []
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            try:
                logs = json.load(f)
            except:
                logs = []
    logs.append(message)
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)


band = BandConnection()


def initialize():
    return band.register(AGENT_ID, AGENT_CAPABILITIES)


def track_video_performance(video_id, video_title):
    """
    Fetches and analyzes video performance.
    Detects if video is underperforming.
    """
    print(f"[{AGENT_NAME}] Tracking: {video_title[:40]}")

    stats = get_video_stats(video_id)
    if not stats:
        return None

    views = stats.get("views", 0)
    likes = stats.get("likes", 0)

    # Performance assessment
    performance_level = "poor"
    if views > 1000:
        performance_level = "excellent"
    elif views > 500:
        performance_level = "good"
    elif views > 100:
        performance_level = "average"
    elif views > 50:
        performance_level = "below_average"

    like_ratio = (likes / views * 100) if views > 0 else 0

    assessment = {
        "video_id": video_id,
        "title": video_title,
        "stats": stats,
        "performance_level": performance_level,
        "like_ratio_percent": round(like_ratio, 2),
        "needs_metadata_update": views < 100,
        "needs_promotion": views < 50,
        "date_checked": datetime.date.today().isoformat()
    }

    # Store in memory
    try:
        store_video_performance(
            video_id=video_id,
            title=video_title,
            stats=stats,
            suggestions=assessment
        )
        print(f"[{AGENT_NAME}] Performance stored in memory.")
    except Exception as e:
        print(f"[{AGENT_NAME}] Memory storage note: {e}")

    return assessment


def generate_improvement_plan(video_id, video_title, stats):
    """
    Generates specific improvement plan
    based on current performance data.
    """
    print(f"[{AGENT_NAME}] Generating improvement plan...")

    metadata = generate_updated_metadata(
        video_title=video_title,
        current_description="",
        current_tags="",
        analytics_data=stats if isinstance(stats, dict) else {}
    )

    return metadata


def generate_next_video_guide(channel_data):
    """
    Uses channel performance history to guide
    what the next video should be about.
    """
    from brain import ask_brain

    history_text = "\n".join([
        f"- {v['title']}: {v.get('stats', {}).get('views', 0)} views"
        for v in channel_data[:5]
    ]) if channel_data else "No history yet"

    prompt = f"""
You are ReachIQ AI MonitorAgent generating next video guidance.

Based on this channel performance history, guide the creator
on what their next video should focus on for maximum growth.

Return ONLY valid JSON, no extra text, no markdown.

FORMAT:
{{
  "recommended_topic": "",
  "recommended_title_style": "",
  "avoid_these_mistakes": [],
  "best_upload_time": "",
  "target_length_minutes": 0,
  "hook_strategy": "",
  "thumbnail_direction": ""
}}

CHANNEL HISTORY:
{history_text}
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
            return result
    return None


def process_task(task_payload):
    """
    Main task processor.
    Receives monitoring tasks from BrainAgent.
    """
    task = task_payload.get("task", "")
    data = task_payload.get("data", {})
    priority = task_payload.get("priority", "medium")

    print(f"\n[{AGENT_NAME}] Processing: {task[:50]}")
    print(f"[{AGENT_NAME}] Priority: {priority}")

    results = {}

    video_id = data.get("video_id", "")
    video_title = data.get("video_title", "")

    if video_id and video_title:
        # Track performance
        performance = track_video_performance(
            video_id, video_title
        )
        results["performance"] = performance

        if performance:
            print(f"[{AGENT_NAME}] Performance level: "
                  f"{performance.get('performance_level')}")

            # Generate improvement plan if needed
            if performance.get("needs_metadata_update"):
                print(f"[{AGENT_NAME}] "
                      f"Generating improvement plan...")
                improvement = generate_improvement_plan(
                    video_id,
                    video_title,
                    performance.get("stats", {})
                )
                results["improvement_plan"] = improvement

    # Get channel patterns for next video guide
    print(f"[{AGENT_NAME}] Fetching channel patterns...")
    videos = get_videos(5)
    if videos:
        channel_data = []
        for v in videos:
            stats = get_video_stats(v["video_id"])
            channel_data.append({
                "title": v["title"],
                "stats": stats or {}
            })
            time.sleep(1)

        next_guide = generate_next_video_guide(channel_data)
        results["next_video_guide"] = next_guide
        if next_guide and isinstance(next_guide, dict):
            print(f"[{AGENT_NAME}] Next video: "
                  f"{next_guide.get('recommended_topic', '')}")

    trace_agent_action(
        "monitor_agent_task",
        task[:100],
        f"Monitoring complete for: {video_title[:40]}",
        status="success"
    )

    # Send results back to BrainAgent
    band.send_message(
        to_agent="brain_agent",
        message_type="task_result",
        payload={
            "agent": AGENT_ID,
            "task": task,
            "results": {
                k: str(v)[:300] if not isinstance(v, dict)
                else v
                for k, v in results.items()
                if v is not None
            },
            "status": "completed"
        }
    )

    print(f"[{AGENT_NAME}] Results sent to BrainAgent.")
    return results


def handle_band_message(message):
    """
    Handles incoming Band messages.
    On June 12 this gets triggered by Band SDK callbacks.
    """
    message_type = message.get("type", "")
    payload = message.get("payload", {})
    from_agent = message.get("from", "unknown")

    print(f"\n[{AGENT_NAME}] Message from {from_agent}: "
          f"{message_type}")

    if message_type == "task_assignment":
        return process_task(payload)
    else:
        print(f"[{AGENT_NAME}] Unknown message: {message_type}")
        return None


def get_agent_status():
    return {
        "agent_id": AGENT_ID,
        "agent_name": AGENT_NAME,
        "version": AGENT_VERSION,
        "role": AGENT_ROLE,
        "capabilities": AGENT_CAPABILITIES,
        "band_connected": band.connected,
        "messages_sent": len(band.message_log),
        "status": "active"
    }


if __name__ == "__main__":
    print("=" * 55)
    print("ReachIQ AI — MonitorAgent Test")
    print("=" * 55)

    initialize()

    # Simulate receiving task from BrainAgent
    print("\nSimulating Band message from BrainAgent...")
    band.simulate_incoming(
        from_agent="brain_agent",
        task_type="task_assignment",
        payload={
            "task": "Check video performance and suggest improvements",
            "data": {
                "video_id": "hrVNiuZ0ooc",
                "video_title": "The Science Behind AI Hallucination"
            },
            "priority": "medium"
        }
    )

    message = band.receive_message()
    if message:
        results = handle_band_message(message)
        if results:
            print("\nMonitoring Complete.")
            if "performance" in results and isinstance(
                    results["performance"], dict):
                perf = results["performance"]
                print(f"Performance Level: "
                      f"{perf.get('performance_level')}")
                print(f"Needs Update: "
                      f"{perf.get('needs_metadata_update')}")

    print("\nAgent Status:")
    print(json.dumps(get_agent_status(), indent=2))
    print("\nMonitorAgent ready for Band connection.")