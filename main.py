import os
os.environ["HF_HOME"] = "E:/Developer_Space/huggingface_cache"
os.environ["TRANSFORMERS_CACHE"] = "E:/Developer_Space/huggingface_cache"
os.environ["HF_HUB_VERBOSITY"] = "error"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import sys
import time
import datetime
import json
import importlib

os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.makedirs("reports", exist_ok=True)
os.makedirs("logs", exist_ok=True)

# ─────────────────────────────────────────────
# REACHIQ AI — MAIN ORCHESTRATOR v2.0
# Brain: Groq Llama 3.3 70B + Llava via OpenRouter
# vector_storery: Mem0 + Qdrant
# Observability: Langfuse
# Security: Custom guardrails
# ─────────────────────────────────────────────

from config import YOUTUBE_API_KEY, GROQ_API_KEY, CHANNEL_ID
from brain import ask_brain, ask_with_fallback
from memory import (store_video_performance, get_channel_patterns,
                    get_smart_suggestions, view_memory_stats)
from observability import (trace_agent_action, measure_and_trace,
                           get_daily_performance_summary,
                           view_recent_traces)
from security import (secure_input, validate_youtube_metadata,
                      validate_social_media_post, get_security_report)


# ─────────────────────────────────────────────
# MCP TOOL REGISTRY
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
    "store_video_performance": {
        "module": "memory",
        "function": "store_video_performance",
        "description": "Stores video performance in memory"
    },
    "get_channel_patterns": {
        "module": "memory",
        "function": "get_channel_patterns",
        "description": "Gets learned channel patterns from memory"
    },
    "get_smart_suggestions": {
        "module": "memory",
        "function": "get_smart_suggestions",
        "description": "Gets AI suggestions based on memory"
    },
    "secure_input": {
        "module": "security",
        "function": "secure_input",
        "description": "Validates and secures user input"
    },
    "validate_youtube_metadata": {
        "module": "security",
        "function": "validate_youtube_metadata",
        "description": "Validates metadata before publishing"
    }
}


def use_tool(tool_name, **kwargs):
    """
    MCP style tool caller.
    All modules called through here.
    """
    if tool_name not in MCP_TOOLS:
        print(f"Tool {tool_name} not found.")
        return None

    tool = MCP_TOOLS[tool_name]

    try:
        module = importlib.import_module(tool["module"])
        func = getattr(module, tool["function"])
        trace_agent_action(
            f"tool_call_{tool_name}", tool_name, "called"
        )
        return func(**kwargs)

    except Exception as e:
        trace_agent_action(
            f"tool_call_{tool_name}", tool_name, f"failed: {e}"
        )
        print(f"Tool {tool_name} failed: {e}")
        return None


# ─────────────────────────────────────────────
# HUMAN APPROVAL + SAFETY GATE
# ─────────────────────────────────────────────

def human_approval_gate(action_name, details):
    """
    Pauses execution and waits for your approval.
    Nothing goes live without your confirmation.
    """
    print("\n" + "=" * 55)
    print("HUMAN APPROVAL + SAFETY GATE")
    print("=" * 55)
    print(f"Action: {action_name}")
    print(f"Details: {details}")
    print("=" * 55)

    while True:
        choice = input("Approve? (y/n): ").strip().lower()
        if choice == "y":
            log_action(action_name, "APPROVED", details)
            print("Approved.")
            return True
        elif choice == "n":
            log_action(action_name, "REJECTED", details)
            print("Rejected.")
            return False
        else:
            print("Enter y or n.")


# ─────────────────────────────────────────────
# VISION ROUTER — Thumbnail Analysis
# ─────────────────────────────────────────────

def analyze_thumbnail(image_path):
    """
    Routes thumbnail to Ollama LLaVA:7b.
    Vision model for thumbnail scoring.
    """
    try:
        import ollama
        print("Analyzing thumbnail with LLaVA:7b...")

        response = ollama.chat(
            model="llava:7b",
            options={
                "num_predict": 200,
                "temperature": 0.1
            },
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
            return {
                "visibility_score": 7,
                "text_readability": result[:200] if result else "",
                "emotional_impact": "See full analysis",
                "color_contrast": "",
                "suggested_improvements": [result[:300]] if result else [],
                "ctr_prediction": "Requires manual review"
            }

    except Exception as e:
        print(f"Thumbnail analysis failed: {e}")
        print("Run: ollama pull llava:7b")
        return None
# ─────────────────────────────────────────────
# ACTION LOGGER
# ─────────────────────────────────────────────

def log_action(action, status, details=""):
    log_file = os.path.join(
        "logs",
        f"reachiq_log_{datetime.date.today()}.txt"
    )
    timestamp = datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {status} | {action}\n")
        if details:
            f.write(f"  Details: {str(details)[:200]}\n")


# ─────────────────────────────────────────────
# MENU
# ─────────────────────────────────────────────

def render_menu():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 55)
    print("  ReachIQ AI — MAIN CONTROL PANEL v2.0")
    print(f"  {datetime.date.today()}")
    print("=" * 55)
    print("  1. Pre-Upload Analysis")
    print("  2. Post-Upload Monitoring")
    print("  3. Daily Intelligence Report")
    print("  4. Thumbnail Analysis (Vision)")
    print("  5. Channel Memory and Patterns")
    print("  6. List MCP Tools")
    print("  7. View Action Log")
    print("  8. Security Report")
    print("  9. System Diagnostics")
    print("  10. Shutdown")
    print("=" * 55)


# ─────────────────────────────────────────────
# OPTION HANDLERS
# ─────────────────────────────────────────────

def handle_pre_upload_main():
    print("\nPRE-UPLOAD ANALYSIS")
    print("=" * 55)

    raw_title = input("Video Title: ").strip()
    title = secure_input(raw_title, "title")
    if not title:
        print("Title blocked by security. Please try again.")
        return

    description = input("Description: ").strip()
    tags = input("Tags (comma separated): ").strip()
    script = input("First 3 lines of script "
                   "(or Enter to skip): ").strip()

    # Validate metadata
    validation = validate_youtube_metadata(
        title, description, tags.split(",")
    )
    if not validation.get("is_valid"):
        print("Metadata issues found:")
        for issue in validation.get("issues", []):
            print(f"  - {issue}")

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
        print(f"Upload Ready: "
              f"{analysis.get('upload_ready', False)}")
        print(f"Hook: {analysis.get('hook_suggestion', '')}")
        print(f"Thumbnail: {analysis.get('thumbnail_text', '')}")
        print("\nTop 3 Actions:")
        for action in analysis.get("top_3_actions", []):
            print(f"  - {action}")

    time.sleep(2)

    # Check memory for smart suggestions
    print("\nChecking channel memory for smart suggestions...")
    suggestions = use_tool("get_smart_suggestions",
                           context=title)
    if suggestions and isinstance(suggestions, dict):
        print("Smart suggestions from memory:")
        for s in suggestions.get("smart_suggestions", [])[:3]:
            print(f"  - {s}")

    # Save report
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(
        "reports", f"pre_upload_{timestamp}.txt"
    )
    with open(filename, "w", encoding="utf-8") as f:
        f.write("ReachIQ AI — Pre Upload Report\n")
        f.write(f"Date: {datetime.datetime.now()}\n")
        f.write(f"Title: {title}\n\n")
        if score and isinstance(score, dict):
            f.write(f"SCORE: {score.get('total_score', 0)}/100\n")
            f.write(f"GRADE: {score.get('grade', '')}\n")
            f.write(f"PRIORITY FIX: "
                    f"{score.get('priority_fix', '')}\n\n")
        if analysis and isinstance(analysis, dict):
            f.write(f"HOOK: "
                    f"{analysis.get('hook_suggestion', '')}\n")
            f.write(f"THUMBNAIL: "
                    f"{analysis.get('thumbnail_text', '')}\n")

    print(f"\nReport saved: {filename}")
    log_action("PRE_UPLOAD_ANALYSIS", "COMPLETED", title)


def handle_thumbnail_analysis():
    print("\nTHUMBNAIL ANALYSIS")
    print("=" * 55)
    print("Place thumbnail image in project folder.")
    image_path = input("Image filename "
                       "(e.g. thumbnail.jpg): ").strip()

    if not os.path.exists(image_path):
        print(f"File not found: {image_path}")
        return

    result = analyze_thumbnail(image_path)
    if result and isinstance(result, dict):
        print(f"\nVisibility: "
              f"{result.get('visibility_score', 0)}/10")
        print(f"Readability: "
              f"{result.get('text_readability', '')}")
        print(f"CTR Prediction: "
              f"{result.get('ctr_prediction', '')}")
        print("\nImprovements:")
        for imp in result.get("suggested_improvements", []):
            print(f"  - {imp}")
    elif result:
        print(result)

    log_action("THUMBNAIL_ANALYSIS", "COMPLETED", image_path)


def handle_memory_patterns():
    print("\nCHANNEL MEMORY AND PATTERNS")
    print("=" * 55)

    print("\n1. Memory Statistics:")
    view_memory_stats()

    print("\n2. Channel Patterns from History:")
    patterns = use_tool("get_channel_patterns")
    if patterns and isinstance(patterns, dict):
        print(f"\nBest Topics: "
              f"{patterns.get('best_performing_topics', [])}")
        print(f"Recommended Next: "
              f"{patterns.get('recommended_next_topics', [])}")
        print(f"Key Learning: "
              f"{patterns.get('key_learning', '')}")
    else:
        print("Not enough data yet. "
              "Run more videos through the agent to build memory.")

    log_action("MEMORY_PATTERNS", "VIEWED")


def generate_daily_report():
    print("=" * 55)
    print("ReachIQ AI — Daily Intelligence Report")
    print(f"Date: {datetime.date.today()}")
    print("=" * 55)

    log_action("DAILY_REPORT", "STARTED")

    videos = use_tool("get_videos", max_results=5)
    if not videos:
        print("Could not fetch videos.")
        return

    print(f"Found {len(videos)} videos.")

    for video in videos[:3]:
        print(f"\nProcessing: {video['title'][:50]}")

        stats = use_tool("get_video_stats",
                         video_id=video["video_id"])
        if stats and isinstance(stats, dict):
            print(f"Views: {stats.get('views', 0)}")

        time.sleep(2)

        keywords = use_tool("extract_keywords",
                            video_title=video["title"])
        if keywords and isinstance(keywords, dict):
            primary = keywords.get("primary_keywords", [])
            print(f"Keywords: {', '.join(primary[:3])}")

        time.sleep(2)

        metadata = use_tool(
            "generate_updated_metadata",
            video_title=video["title"],
            current_description="",
            current_tags="",
            analytics_data=stats if isinstance(
                stats, dict) else {}
        )

        if metadata and isinstance(metadata, dict):
            print(f"Suggested Title: "
                  f"{metadata.get('updated_title', '')}")

            if human_approval_gate(
                "METADATA UPDATE",
                f"Update: {video['title'][:40]}"
            ):
                # Store in memory
                use_tool(
                    "store_video_performance",
                    video_id=video["video_id"],
                    title=video["title"],
                    stats=stats if isinstance(stats, dict) else {},
                    suggestions=metadata if isinstance(
                        metadata, dict) else {}
                )
                print("Stored in memory.")

        time.sleep(2)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(
        "reports",
        f"daily_report_{timestamp}.json"
    )
    with open(filename, "w", encoding="utf-8") as f:
        json.dump({"date": str(datetime.date.today()),
                   "videos_processed": len(videos[:3])},
                  f, indent=2)

    print(f"\nDaily report saved: {filename}")
    log_action("DAILY_REPORT", "COMPLETED")


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
        print("No actions logged today.")


def handle_security_report():
    print("\nSECURITY REPORT")
    print("=" * 55)
    report = get_security_report()
    if isinstance(report, dict):
        print(json.dumps(report, indent=2))
    else:
        print(report)


def handle_diagnostics():
    print("\nSYSTEM DIAGNOSTICS")
    print("=" * 55)
    modules = [
        "config", "brain", "youtube_api",
        "analyzer", "scorer", "monitor",
        "metadata_updater", "keyword_tracker",
        "social_media", "automation",
        "memory", "observability", "security"
    ]
    all_ok = True
    for mod in modules:
        try:
            importlib.import_module(mod)
            print(f"  OK    {mod}.py")
        except Exception as e:
            print(f"  FAIL  {mod}.py — {e}")
            all_ok = False

    print()
    if all_ok:
        print("All 13 modules loaded successfully.")
        print("ReachIQ AI is fully operational.")
    else:
        print("Some modules have issues.")

    # Observability summary
    print("\nObservability Summary:")
    summary = get_daily_performance_summary()
    if isinstance(summary, dict):
        print(f"  Actions today: "
              f"{summary.get('total_actions', 0)}")
        print(f"  Success rate: "
              f"{summary.get('success_rate', '0%')}")

    log_action("DIAGNOSTICS", "COMPLETED")


# ─────────────────────────────────────────────
# MAIN START
# ─────────────────────────────────────────────

def start():
    log_action("SYSTEM", "STARTED")
    print("Starting ReachIQ AI...")

    while True:
        render_menu()
        try:
            choice = input("\nSelect option (1-10): ").strip()

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
                handle_memory_patterns()
                input("\nPress Enter to return to menu...")

            elif choice == "6":
                handle_list_tools()
                input("\nPress Enter to return to menu...")

            elif choice == "7":
                handle_view_log()
                input("\nPress Enter to return to menu...")

            elif choice == "8":
                handle_security_report()
                input("\nPress Enter to return to menu...")

            elif choice == "9":
                handle_diagnostics()
                input("\nPress Enter to return to menu...")

            elif choice == "10":
                print("\nShutting down ReachIQ AI. Goodbye.")
                log_action("SYSTEM", "SHUTDOWN")
                break

            else:
                print("Invalid option. Select 1-10.")
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n\nSession ended.")
            log_action("SYSTEM", "INTERRUPTED")
            break
        except Exception as e:
            print(f"\nError: {e}")
            time.sleep(2)


if __name__ == "__main__":
    start()