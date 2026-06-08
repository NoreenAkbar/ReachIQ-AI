import os
import datetime
import json
import time

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ─────────────────────────────────────────────
# REACHIQ AI — DISTRIBUTION AGENT
# Role: Content distribution and promotion specialist
# Receives tasks from BrainAgent via Band
# Handles: social media, keywords, opportunities
# ─────────────────────────────────────────────

from social_media import (generate_platform_posts,
                          find_reddit_opportunities,
                          find_quora_opportunities)
from keyword_tracker import (extract_keywords,
                             find_competing_videos,
                             find_distribution_opportunities)
from observability import trace_agent_action
from security import validate_social_media_post

AGENT_ID = "distribution_agent"
AGENT_NAME = "DistributionAgent"
AGENT_ROLE = "Content distribution and promotion specialist"
AGENT_VERSION = "1.0"

AGENT_CAPABILITIES = [
    "generate_social_posts",
    "find_reddit_opportunities",
    "find_quora_opportunities",
    "find_youtube_opportunities",
    "extract_distribution_keywords",
    "validate_posts_before_publish"
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


def prepare_distribution_package(video_title,
                                  video_url, keywords):
    """
    Creates complete distribution package for a video.
    All platforms, all opportunities, ready to publish.
    """
    print(f"[{AGENT_NAME}] Preparing distribution for: "
          f"{video_title[:40]}")

    package = {
        "video_title": video_title,
        "video_url": video_url,
        "generated_at": datetime.datetime.now().isoformat(),
        "platforms": {},
        "opportunities": {},
        "validated": {}
    }

    # Generate platform posts
    print(f"[{AGENT_NAME}] Generating platform posts...")
    posts = generate_platform_posts(
        video_title=video_title,
        video_url=video_url,
        keywords=keywords
    )

    if posts and isinstance(posts, dict):
        package["platforms"] = posts

        # Validate each post
        print(f"[{AGENT_NAME}] Validating posts...")
        for platform, content in posts.items():
            if isinstance(content, dict):
                post_text = content.get("post", "")
                if post_text:
                    validation = validate_social_media_post(
                        platform, post_text
                    )
                    package["validated"][platform] = validation
                    status = "VALID" if validation.get(
                        "is_valid") else "INVALID"
                    print(f"[{AGENT_NAME}] {platform}: {status}")

    time.sleep(2)

    # Find Reddit opportunities
    print(f"[{AGENT_NAME}] Finding Reddit opportunities...")
    reddit = find_reddit_opportunities(keywords[:3])
    if reddit and isinstance(reddit, dict):
        subs = reddit.get("subreddits", [])
        package["opportunities"]["reddit"] = subs
        print(f"[{AGENT_NAME}] Found {len(subs)} subreddits")

    time.sleep(2)

    # Find Quora opportunities
    print(f"[{AGENT_NAME}] Finding Quora opportunities...")
    quora = find_quora_opportunities(keywords[:3])
    if quora and isinstance(quora, dict):
        questions = quora.get("questions", [])
        package["opportunities"]["quora"] = questions
        print(f"[{AGENT_NAME}] Found "
              f"{len(questions)} Quora questions")

    time.sleep(2)

    # Find YouTube distribution opportunities
    print(f"[{AGENT_NAME}] Finding YouTube opportunities...")
    yt_opps = find_distribution_opportunities(keywords[:3])
    package["opportunities"]["youtube"] = yt_opps
    print(f"[{AGENT_NAME}] Found "
          f"{len(yt_opps)} YouTube opportunities")

    return package


def save_distribution_report(package, video_id):
    """
    Saves complete distribution package to file.
    Ready for you to copy paste and post.
    """
    os.makedirs("reports", exist_ok=True)
    timestamp = datetime.datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )
    filename = os.path.join(
        "reports",
        f"distribution_{video_id}_{timestamp}.txt"
    )

    with open(filename, "w", encoding="utf-8") as f:
        f.write("ReachIQ AI — Distribution Report\n")
        f.write(f"Generated: {datetime.datetime.now()}\n")
        f.write(f"Video: {package.get('video_title', '')}\n")
        f.write(f"URL: {package.get('video_url', '')}\n")
        f.write("=" * 55 + "\n\n")

        platforms = package.get("platforms", {})
        if platforms:
            f.write("SOCIAL MEDIA POSTS:\n")
            f.write("-" * 30 + "\n")

            for platform, content in platforms.items():
                f.write(f"\n{platform.upper()}:\n")
                if isinstance(content, dict):
                    post = content.get("post", "")
                    if post:
                        f.write(f"{post}\n")
                    validated = package.get(
                        "validated", {}
                    ).get(platform, {})
                    if validated:
                        status = "VALID" if validated.get(
                            "is_valid") else "CHECK NEEDED"
                        f.write(f"Status: {status}\n")
                f.write("-" * 30 + "\n")

        opps = package.get("opportunities", {})
        reddit_opps = opps.get("reddit", [])
        if reddit_opps:
            f.write("\nREDDIT OPPORTUNITIES:\n")
            f.write("-" * 30 + "\n")
            for sub in reddit_opps[:5]:
                if isinstance(sub, dict):
                    name = sub.get("name", "").replace(
                        "r/", ""
                    ).strip()
                    f.write(f"r/{name}\n")
                    comment = sub.get("sample_comment", "")
                    if comment:
                        f.write(f"Comment: {comment}\n\n")

        quora_opps = opps.get("quora", [])
        if quora_opps:
            f.write("\nQUORA OPPORTUNITIES:\n")
            f.write("-" * 30 + "\n")
            for q in quora_opps[:5]:
                if isinstance(q, dict):
                    question = q.get("question", "")
                    answer = q.get("sample_answer", "")
                    if question:
                        f.write(f"Q: {question}\n")
                    if answer:
                        f.write(f"A: {answer}\n\n")

    print(f"[{AGENT_NAME}] Report saved: {filename}")
    return filename


def process_task(task_payload):
    """
    Main task processor.
    Receives distribution tasks from BrainAgent.
    """
    task = task_payload.get("task", "")
    data = task_payload.get("data", {})
    priority = task_payload.get("priority", "medium")

    print(f"\n[{AGENT_NAME}] Processing: {task[:50]}")
    print(f"[{AGENT_NAME}] Priority: {priority}")

    video_title = data.get("video_title", "")
    video_id = data.get("video_id", "")
    video_url = data.get(
        "video_url",
        f"https://youtu.be/{video_id}" if video_id else ""
    )

    # Extract keywords first
    keywords = ["AI", "artificial intelligence",
                "machine learning"]
    if video_title:
        print(f"[{AGENT_NAME}] Extracting keywords...")
        kw_data = extract_keywords(video_title)
        if kw_data and isinstance(kw_data, dict):
            keywords = kw_data.get(
                "primary_keywords", keywords
            )

    # Prepare full distribution package
    package = prepare_distribution_package(
        video_title=video_title,
        video_url=video_url,
        keywords=keywords
    )

    # Save report
    report_file = save_distribution_report(
        package, video_id or "unknown"
    )

    trace_agent_action(
        "distribution_agent_task",
        task[:100],
        f"Distribution package for: {video_title[:40]}",
        status="success"
    )

    # Send results back to BrainAgent
    band.send_message(
        to_agent="brain_agent",
        message_type="task_result",
        payload={
            "agent": AGENT_ID,
            "task": task,
            "report_file": report_file,
            "platforms_covered": list(
                package.get("platforms", {}).keys()
            ),
            "opportunities_found": {
                k: len(v) for k, v in
                package.get("opportunities", {}).items()
            },
            "status": "completed"
        }
    )

    print(f"[{AGENT_NAME}] Results sent to BrainAgent.")
    return package


def handle_band_message(message):
    """
    Handles incoming Band messages.
    On June 12 this gets triggered by Band SDK callbacks.
    """
    message_type = message.get("type", "")
    payload = message.get("payload", {})
    from_agent = message.get("from", "unknown")

    print(f"\n[{AGENT_NAME}] Message from "
          f"{from_agent}: {message_type}")

    if message_type == "task_assignment":
        return process_task(payload)
    else:
        print(f"[{AGENT_NAME}] Unknown: {message_type}")
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
    print("ReachIQ AI — DistributionAgent Test")
    print("=" * 55)

    initialize()

    # Simulate receiving task from BrainAgent
    print("\nSimulating Band message from BrainAgent...")
    band.simulate_incoming(
        from_agent="brain_agent",
        task_type="task_assignment",
        payload={
            "task": "Distribute this video across all platforms",
            "data": {
                "video_title": "The Science Behind AI Hallucination",
                "video_id": "hrVNiuZ0ooc",
                "video_url": "https://youtu.be/hrVNiuZ0ooc"
            },
            "priority": "high"
        }
    )

    message = band.receive_message()
    if message:
        results = handle_band_message(message)
        if results and isinstance(results, dict):
            platforms = results.get("platforms", {})
            print(f"\nPlatforms covered: "
                  f"{list(platforms.keys())}")

    print("\nAgent Status:")
    print(json.dumps(get_agent_status(), indent=2))
    print("\nDistributionAgent ready for Band connection.")