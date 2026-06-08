import os
import datetime
import json

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ─────────────────────────────────────────────
# REACHIQ AI — ANALYZER AGENT
# Role: Pre-upload content analysis specialist
# Receives tasks from BrainAgent via Band
# Handles: scoring, analysis, keywords, competition
# ─────────────────────────────────────────────

from analyzer import analyze_pre_upload, analyze_channel_patterns
from scorer import score_video
from keyword_tracker import extract_keywords, find_competing_videos
from observability import trace_agent_action
from security import secure_input, validate_youtube_metadata

AGENT_ID = "analyzer_agent"
AGENT_NAME = "AnalyzerAgent"
AGENT_ROLE = "Pre-upload content analysis specialist"
AGENT_VERSION = "1.0"

AGENT_CAPABILITIES = [
    "score_content",
    "analyze_pre_upload",
    "extract_keywords",
    "analyze_competition",
    "analyze_channel_patterns",
    "validate_metadata"
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

    def simulate_incoming(self, from_agent, task_type, payload):
        """Simulates receiving a message from Band"""
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


def process_task(task_payload):
    """
    Main task processor.
    Receives task from BrainAgent and executes it.
    """
    task = task_payload.get("task", "")
    data = task_payload.get("data", {})
    priority = task_payload.get("priority", "medium")

    print(f"\n[{AGENT_NAME}] Processing: {task[:50]}")
    print(f"[{AGENT_NAME}] Priority: {priority}")

    title = data.get("title", "")
    description = data.get("description", "")
    tags = data.get("tags", "")
    script = data.get("script", None)

    results = {}

    # Security check
    if title:
        safe_title = secure_input(title, "title")
        if not safe_title:
            return {"status": "blocked", "reason": "Security check failed"}

    # Score the content
    if title:
        print(f"[{AGENT_NAME}] Scoring content...")
        score = score_video(title, description, tags)
        results["score"] = score
        if score and isinstance(score, dict):
            print(f"[{AGENT_NAME}] Score: "
                  f"{score.get('total_score', 0)}/100")

    # Full pre-upload analysis
    if title:
        print(f"[{AGENT_NAME}] Running pre-upload analysis...")
        analysis = analyze_pre_upload(
            title, description, tags, script
        )
        results["analysis"] = analysis
        if analysis and isinstance(analysis, dict):
            print(f"[{AGENT_NAME}] Upload ready: "
                  f"{analysis.get('upload_ready', False)}")

    # Extract keywords
    if title:
        print(f"[{AGENT_NAME}] Extracting keywords...")
        keywords = extract_keywords(title, description)
        results["keywords"] = keywords
        if keywords and isinstance(keywords, dict):
            primary = keywords.get("primary_keywords", [])
            print(f"[{AGENT_NAME}] Primary keywords: "
                  f"{', '.join(primary[:3])}")

    # Competition analysis
    if keywords and isinstance(keywords, dict):
        primary_kw = keywords.get("primary_keywords", [])
        if primary_kw:
            print(f"[{AGENT_NAME}] Analyzing competition...")
            competitors = find_competing_videos(
                primary_kw[0], max_results=3
            )
            results["competitors"] = competitors
            print(f"[{AGENT_NAME}] Found "
                  f"{len(competitors)} competitors")

    # Validate metadata
    if title:
        validation = validate_youtube_metadata(
            title, description,
            tags.split(",") if isinstance(tags, str) else tags
        )
        results["validation"] = validation

    trace_agent_action(
        "analyzer_agent_task",
        task[:100],
        f"Completed analysis for: {title[:40]}",
        status="success"
    )

    # Send results back to BrainAgent
    response = band.send_message(
        to_agent="brain_agent",
        message_type="task_result",
        payload={
            "agent": AGENT_ID,
            "task": task,
            "results": {
                k: v for k, v in results.items()
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
    Called when Band delivers a message to this agent.
    On June 12 this gets triggered by Band SDK callbacks.
    """
    message_type = message.get("type", "")
    payload = message.get("payload", {})
    from_agent = message.get("from", "unknown")

    print(f"\n[{AGENT_NAME}] Message from {from_agent}: "
          f"{message_type}")

    if message_type == "task_assignment":
        return process_task(payload)

    elif message_type == "channel_analysis_request":
        print(f"[{AGENT_NAME}] Analyzing channel patterns...")
        patterns = analyze_channel_patterns()
        band.send_message(
            to_agent=from_agent,
            message_type="channel_analysis_result",
            payload={"patterns": patterns}
        )
        return patterns

    else:
        print(f"[{AGENT_NAME}] Unknown message type: {message_type}")
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
    print("ReachIQ AI — AnalyzerAgent Test")
    print("=" * 55)

    initialize()

    # Simulate receiving a task from BrainAgent via Band
    print("\nSimulating Band message from BrainAgent...")
    band.simulate_incoming(
        from_agent="brain_agent",
        task_type="task_assignment",
        payload={
            "task": "Analyze this video before upload",
            "data": {
                "title": "How AI is Changing Education Forever",
                "description": "Exploring AI tools for students",
                "tags": "AI, education, students, tools",
                "script": "Welcome back everyone. Today we explore AI."
            },
            "priority": "high"
        }
    )

    # Process the incoming message
    message = band.receive_message()
    if message:
        results = handle_band_message(message)
        if results and isinstance(results, dict):
            print("\nAnalysis Complete:")
            if "score" in results and isinstance(
                    results["score"], dict):
                print(f"Score: "
                      f"{results['score'].get('total_score', 0)}/100")
                print(f"Grade: "
                      f"{results['score'].get('grade', 'N/A')}")

    print("\nAgent Status:")
    print(json.dumps(get_agent_status(), indent=2))
    print("\nAnalyzerAgent ready for Band connection.")