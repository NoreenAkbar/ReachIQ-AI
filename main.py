import os
import sys
import time
import datetime
import json
import importlib

os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.makedirs("reports", exist_ok=True)
os.makedirs("logs", exist_ok=True)

# ─────────────────────────────────────────────
# REACHIQ AI — MAIN ORCHESTRATOR
# Version 1.0
# Brain: Groq llama-3.3-70b-versatile
# Fallback: Ollama llama3.2:1b
# Vision: Ollama moondream (thumbnail analysis)
# ─────────────────────────────────────────────

from config import YOUTUBE_API_KEY, GROQ_API_KEY, CHANNEL_ID
from brain import ask_brain


# ─────────────────────────────────────────────
# HUMAN APPROVAL + SAFETY GATE
# Every action passes through this before
# executing. You approve or reject.
# ─────────────────────────────────────────────

def human_approval_gate(action_name, details):
    """
    Pauses execution and waits for human approval.
    Nothing gets posted or updated without your
    explicit confirmation.
    """
    print("\n" + "=" * 55)
    print("HUMAN APPROVAL + SAFETY GATE")
    print("=" * 55)
    print(f"Action: {action_name}")
    print(f"Details: {details}")
    print("=" * 55)

    while True:
        choice = input("Approve this action? (y/n): ").strip().lower()
        if choice == "y":
            log_action(action_name, "APPROVED", details)
            print("Approved. Executing...")
            return True
        elif choice == "n":
            log_action(action_name, "REJECTED", details)
            print("Rejected. Skipping this action.")
            return False
        else:
            print("Please enter y or n.")


# ─────────────────────────────────────────────
# VISION ROUTER
# Routes thumbnail analysis to Ollama moondream
# since Groq does not support vision.
# ─────────────────────────────────────────────

def analyze_thumbnail(image_path):
    """
    Routes thumbnail analysis to Ollama moondream.
    Lightweight vision model, runs on CPU.
    """
    try:
        import ollama
        print("Analyzing thumbnail with moondream (lightweight vision)...")

        response = ollama.chat(
            model="moondream",
            messages=[{
                "role": "user",
                "content": """Analyze this YouTube thumbnail.
                    
Return ONLY valid JSON, no extra text.

FORMAT:
{
  "visibility_score": 0,
  "text_readability": "",
  "emotional_impact": "",
  "color_contrast": "",
  "suggested_improvements": [],
  "ctr_prediction": ""
}""",
                "images": [image_path]
            }]
        )
        result = response["message"]["content"]
        try:
            clean = result.strip()
            if "```" in clean:
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            return json.loads(clean)
        except:
            return result

    except ollama.ResponseError as e:
        if "not found" in str(e).lower():
            print("moondream not installed yet.")
            print("Run this in Terminal 1: ollama pull moondream")
            print("Then try thumbnail analysis again.")
        else:
            print(f"Vision model error: {e}")
        return None

    except Exception as e:
        print(f"Thumbnail analysis failed: {e}")
        return None


# ─────────────────────────────────────────────
# ACTION LOGGER
# Logs every action ReachIQ AI takes.
# ─────────────────────────────────────────────

def log_action(action, status, details=""):
    """
    Logs every action to a daily log file.
    Builds your agent's history over time.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = os.path.join(
        "logs",
        f"reachiq_log_{datetime.date.today()}.txt"
    )

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {status} | {action}\n")
        if details:
            f.write(f"  Details: {str(details)[:200]}\n")


# ─────────────────────────────────────────────
# MCP TOOL REGISTRY
# Register tools here. Future tools plug in
# without touching any other code.
# ─────────────────────────────────────────────

MCP_TOOLS = {
    "score_video": {
        "module": "scorer",
        "function": "score_video",
        "description": "Scores video content across 6 dimensions"
    },
    "analyze_pre_upload": {
        "module": "analyzer",
        "function": "analyze_pre_upload",
        "description": "Analyzes content before upload"
    },
    "extract_keywords": {
        "module": "keyword_tracker",
        "function": "extract_keywords",
        "description": "Extracts SEO keywords from video content"
    },
    "find_competing_videos": {
        "module": "keyword_tracker",
        "function": "find_competing_videos",
        "description": "Finds competing videos for a keyword"
    },
    "generate_updated_metadata": {
        "module": "metadata_updater",
        "function": "generate_updated_metadata",
        "description": "Generates optimized metadata for a video"
    },
    "generate_platform_posts": {
        "module": "social_media",
        "function": "generate_platform_posts",
        "description": "Generates social media posts for all platforms"
    },
    "get_videos": {
        "module": "youtube_api",
        "function": "get_videos",
        "description": "Fetches videos from YouTube channel"
    },
    "get_video_stats": {
        "module": "youtube_api",
        "function": "get_video_stats",
        "description": "Fetches stats for a specific video"
    },
    "analyze_thumbnail": {
        "module": "main",
        "function": "analyze_thumbnail",
        "description": "Analyzes thumbnail using Ollama moondream vision"
    }
}


def use_tool(tool_name, **kwargs):
    """
    MCP style tool caller.
    Any module can be called through here.
    New tools just need to be registered above.
    """
    if tool_name not in MCP_TOOLS:
        print(f"Tool {tool_name} not found in registry.")
        return None

    tool = MCP_TOOLS[tool_name]

    try:
        if tool["module"] == "main":
            func = globals()[tool["function"]]
        else:
            module = importlib.import_module(tool["module"])
            func = getattr(module, tool["function"])

        log_action(f"TOOL_CALL:{tool_name}", "EXECUTED")
        return func(**kwargs)

    except Exception as e:
        log_action(f"TOOL_CALL:{tool_name}", "FAILED", str(e))
        print(f"Tool {tool_name} failed: {e}")
        return None


# ─────────────────────────────────────────────
# DAILY INTELLIGENCE REPORT
# Runs all modules and compiles one master
# report for the day.
# ─────────────────────────────────────────────

def generate_daily_report():
    """
    Master daily report combining all modules.
    Run this once per day for full channel intelligence.
    """
    print("=" * 55)
    print("ReachIQ AI — Daily Intelligence Report")
    print(f"Date: {datetime.date.today()}")
    print("=" * 55)

    log_action("DAILY_REPORT", "STARTED")
    report_data = {}

    # Fetch videos
    print("\nFetching your channel videos...")
    videos = use_tool("get_videos", max_results=5)
    if not videos:
        print("Could not fetch videos. Check YouTube API.")
        return

    print(f"Found {len(videos)} videos.")

    for video in videos[:3]:
        print(f"\n{'=' * 55}")
        print(f"Processing: {video['title'][:50]}")
        print(f"{'=' * 55}")

        video_data = {"title": video["title"], "url": video["url"]}

        # Get stats
        stats = use_tool("get_video_stats",
                         video_id=video["video_id"])
        if stats:
            video_data["stats"] = stats
            print(f"Views: {stats.get('views', 0)}")
            print(f"Likes: {stats.get('likes', 0)}")

        time.sleep(2)

        # Extract keywords
        print("Extracting keywords...")
        keywords = use_tool("extract_keywords",
                            video_title=video["title"])
        if keywords and isinstance(keywords, dict):
            primary = keywords.get("primary_keywords", [])
            video_data["keywords"] = primary
            print(f"Primary Keywords: {', '.join(primary[:3])}")

        time.sleep(2)

        # Generate metadata update
        print("Generating metadata suggestions...")
        metadata = use_tool(
            "generate_updated_metadata",
            video_title=video["title"],
            current_description="",
            current_tags="",
            analytics_data=stats if isinstance(stats, dict) else {}
        )

        if metadata and isinstance(metadata, dict):
            video_data["metadata"] = metadata
            print(f"Suggested Title: "
                  f"{metadata.get('updated_title', '')}")

            # Human approval before anything gets saved
            if human_approval_gate(
                "METADATA UPDATE",
                f"Update metadata for: {video['title']}"
            ):
                print("Metadata update approved. Saved to report.")
            else:
                print("Metadata update skipped.")

        time.sleep(2)

        # Generate social posts
        print("Generating social media posts...")
        kw_list = video_data.get("keywords", ["AI"])
        posts = use_tool(
            "generate_platform_posts",
            video_title=video["title"],
            video_url=video["url"],
            keywords=kw_list
        )

        if posts and isinstance(posts, dict):
            video_data["posts"] = posts
            print("Social posts generated.")

            # Human approval before posting
            if human_approval_gate(
                "SOCIAL MEDIA POST",
                f"Post content for: {video['title']}"
            ):
                print("Social posts approved. Ready to publish.")
            else:
                print("Social posts skipped.")

        report_data[video["video_id"]] = video_data
        time.sleep(3)

    # Save master report
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(
        "reports",
        f"daily_intelligence_report_{timestamp}.json"
    )

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 55}")
    print(f"Daily report saved: {filename}")
    log_action("DAILY_REPORT", "COMPLETED", filename)
    print(f"{'=' * 55}")


# ─────────────────────────────────────────────
# MAIN MENU
# ─────────────────────────────────────────────

def render_menu():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 55)
    print("  ReachIQ AI — MAIN CONTROL PANEL")
    print(f"  {datetime.date.today()}")
    print("=" * 55)
    print("  1. Pre-Upload Analysis")
    print("  2. Post-Upload Monitoring")
    print("  3. Daily Intelligence Report")
    print("  4. Thumbnail Analysis (Vision)")
    print("  5. List Available Tools (MCP Registry)")
    print("  6. View Today's Action Log")
    print("  7. Run System Diagnostics")
    print("  8. Shutdown")
    print("=" * 55)


def handle_pre_upload_main():
    print("\nPRE-UPLOAD ANALYSIS")
    print("=" * 55)
    title = input("Video Title: ").strip()
    description = input("Description: ").strip()
    tags = input("Tags (comma separated): ").strip()
    script = input("First 3 lines of script "
                   "(or Enter to skip): ").strip()

    print("\nScoring content...")
    score = use_tool("score_video",
                     title=title,
                     description=description,
                     tags=tags)
    if score and isinstance(score, dict):
        print(f"\nScore: {score.get('total_score', 0)}/100")
        print(f"Grade: {score.get('grade', 'N/A')}")
        print(f"Priority Fix: {score.get('priority_fix', 'N/A')}")

    time.sleep(2)

    print("\nAnalyzing content...")
    analysis = use_tool(
        "analyze_pre_upload",
        title=title,
        description=description,
        tags=tags,
        script=script if script else None
    )
    if analysis and isinstance(analysis, dict):
        print(f"Upload Ready: {analysis.get('upload_ready', False)}")
        print(f"Hook: {analysis.get('hook_suggestion', '')}")
        print(f"Thumbnail Text: {analysis.get('thumbnail_text', '')}")
        print("\nTop 3 Actions:")
        for action in analysis.get("top_3_actions", []):
            print(f"  - {action}")

    time.sleep(2)

    print("\nExtracting keywords...")
    keywords = use_tool("extract_keywords",
                        video_title=title,
                        video_description=description)
    if keywords and isinstance(keywords, dict):
        print("Primary Keywords: " +
              ", ".join(keywords.get("primary_keywords", [])))

    # Save report
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(
        "reports",
        f"pre_upload_{timestamp}.txt"
    )
    with open(filename, "w", encoding="utf-8") as f:
        f.write("ReachIQ AI — Pre Upload Report\n")
        f.write(f"Date: {datetime.datetime.now()}\n")
        f.write(f"Title: {title}\n\n")
        if score and isinstance(score, dict):
            f.write(f"SCORE: {score.get('total_score', 0)}/100\n")
            f.write(f"GRADE: {score.get('grade', '')}\n")
            f.write(f"PRIORITY FIX: {score.get('priority_fix', '')}\n\n")
        if analysis and isinstance(analysis, dict):
            f.write(f"HOOK: {analysis.get('hook_suggestion', '')}\n")
            f.write(f"THUMBNAIL: {analysis.get('thumbnail_text', '')}\n")
            f.write("TOP 3 ACTIONS:\n")
            for a in analysis.get("top_3_actions", []):
                f.write(f"  - {a}\n")

    print(f"\nReport saved: {filename}")
    log_action("PRE_UPLOAD_ANALYSIS", "COMPLETED", title)


def handle_thumbnail_analysis():
    print("\nTHUMBNAIL ANALYSIS (Vision)")
    print("=" * 55)
    print("Place your thumbnail image in the project folder.")
    image_path = input("Enter image filename "
                       "(e.g. thumbnail.jpg): ").strip()

    if not os.path.exists(image_path):
        print(f"File not found: {image_path}")
        print("Make sure the image is in your project folder.")
        return

    print("\nAnalyzing thumbnail with Ollama moondream...")
    result = analyze_thumbnail(image_path)

    if result and isinstance(result, dict):
        print(f"\nVisibility Score: "
              f"{result.get('visibility_score', 0)}/10")
        print(f"Text Readability: "
              f"{result.get('text_readability', '')}")
        print(f"Emotional Impact: "
              f"{result.get('emotional_impact', '')}")
        print(f"CTR Prediction: "
              f"{result.get('ctr_prediction', '')}")
        print("\nSuggested Improvements:")
        for imp in result.get("suggested_improvements", []):
            print(f"  - {imp}")
    elif result:
        print(result)

    log_action("THUMBNAIL_ANALYSIS", "COMPLETED", image_path)


def handle_list_tools():
    print("\nMCP TOOL REGISTRY")
    print("=" * 55)
    for name, tool in MCP_TOOLS.items():
        print(f"Tool: {name}")
        print(f"  Module: {tool['module']}")
        print(f"  Description: {tool['description']}")
        print()


def handle_view_log():
    print("\nTODAY'S ACTION LOG")
    print("=" * 55)
    log_file = os.path.join(
        "logs",
        f"reachiq_log_{datetime.date.today()}.txt"
    )
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            print(f.read())
    else:
        print("No actions logged today yet.")


def handle_diagnostics():
    print("\nSYSTEM DIAGNOSTICS")
    print("=" * 55)
    modules = [
        "config", "brain", "youtube_api",
        "analyzer", "scorer", "monitor",
        "metadata_updater", "keyword_tracker",
        "social_media", "automation"
    ]
    all_ok = True
    for mod in modules:
        try:
            importlib.import_module(mod)
            print(f"  OK  {mod}.py")
        except Exception as e:
            print(f"  FAIL  {mod}.py — {e}")
            all_ok = False

    print()
    if all_ok:
        print("All modules loaded successfully.")
    else:
        print("Some modules have issues. Check above.")

    log_action("DIAGNOSTICS", "COMPLETED")


# ─────────────────────────────────────────────
# START REACHIQ AI
# ─────────────────────────────────────────────

def start():
    log_action("SYSTEM", "STARTED")
    print("Starting ReachIQ AI...")

    while True:
        render_menu()
        try:
            choice = input("\nSelect option (1-8): ").strip()

            if choice == "1":
                handle_pre_upload_main()
                input("\nPress Enter to return to menu...")

            elif choice == "2":
                from automation import handle_post_upload
                handle_post_upload()
                input("\nPress Enter to return to menu...")

            elif choice == "3":
                generate_daily_report()
                input("\nPress Enter to return to menu...")

            elif choice == "4":
                handle_thumbnail_analysis()
                input("\nPress Enter to return to menu...")

            elif choice == "5":
                handle_list_tools()
                input("\nPress Enter to return to menu...")

            elif choice == "6":
                handle_view_log()
                input("\nPress Enter to return to menu...")

            elif choice == "7":
                handle_diagnostics()
                input("\nPress Enter to return to menu...")

            elif choice == "8":
                print("\nShutting down ReachIQ AI. Goodbye.")
                log_action("SYSTEM", "SHUTDOWN")
                break

            else:
                print("Invalid option. Select 1-8.")
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n\nSession ended by operator.")
            log_action("SYSTEM", "INTERRUPTED")
            break
        except Exception as e:
            print(f"\nError: {e}")
            time.sleep(2)


if __name__ == "__main__":
    start()