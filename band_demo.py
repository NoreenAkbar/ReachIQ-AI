"""
ReachIQ AI — Band Live Coordination Bridge
============================================
Connects BrainAgent, AnalyzerAgent, MonitorAgent, DistributionAgent
to the Band platform using the real Band SDK (BandLink + AgentRuntime).

Design goals:
- ISOLATED file: does not modify agent_brain.py / agent_analyzer.py / etc.
- Calls EXISTING, already-working functions (process_task, delegate_task)
  from your real agent modules — Band is just the transport/coordination layer.
- Runnable standalone (python band_demo.py) for terminal/Band-chatroom demo.
- Importable from Streamlit: start_band_bridge() runs everything in a
  background thread + its own asyncio loop, and pushes status/messages
  into a thread-safe queue that the Streamlit UI can poll.

Setup required before running:
1. pip install band-sdk
2. agent_config.yaml in project root with 4 blocks:

   brain:
     agent_id: "<uuid>"
     api_key: "<key>"
   analyzer:
     agent_id: "<uuid>"
     api_key: "<key>"
   monitor:
     agent_id: "<uuid>"
     api_key: "<key>"
   distribution:
     agent_id: "<uuid>"
     api_key: "<key>"

3. On app.band.ai create ONE chat room and add all 4 agents as participants.
4. Set ROOM_ID below (or pass via env var BAND_ROOM_ID) — the room UUID is
   visible in the room URL / room settings on Band.
"""
#print(">>> band_demo.py: module load START")
import os
import json
import yaml
import asyncio
import logging
import threading
import datetime
import queue as queue_module
import threading
_chain_state = {}
_chain_lock = threading.Lock()
#print(">>> band_demo.py: stdlib imports done")

from band import BandLink, AgentRuntime, AgentTools
#print(">>> band_demo.py: band import done")
from band.platform import PlatformEvent
from band.platform.event import MessageEvent
#print(">>> band_demo.py: band.platform import done")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("band_demo")

os.chdir(os.path.dirname(os.path.abspath(__file__)))
#print(">>> band_demo.py: chdir done")

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

CONFIG_FILE = "agent_config.yaml"
ROOM_ID = os.getenv("BAND_ROOM_ID", "941c0c36-5b15-4595-a058-1667f654012c")  # fill in or set env var

WS_URL = "wss://app.band.ai/api/v1/socket/websocket"
REST_URL = "https://app.band.ai"


def load_agent_config(name):
    """Load agent_id/api_key for a given agent block from agent_config.yaml"""
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    block = cfg.get(name)
    if not block:
        raise ValueError(f"Agent '{name}' not found in {CONFIG_FILE}")
    return block["agent_id"], block["api_key"]


# ─────────────────────────────────────────────
# THREAD-SAFE OUTBOX — Streamlit polls this
# ─────────────────────────────────────────────

EVENT_QUEUE: "queue_module.Queue" = queue_module.Queue()


def _emit(agent_name, text):
    """Push a status/message update for the Streamlit UI."""
    EVENT_QUEUE.put({
        "agent": agent_name,
        "text": text,
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    })
    logger.info(f"[{agent_name}] {text}")


# ─────────────────────────────────────────────
# AGENT HANDLERS
# Each wraps your EXISTING process_task() / delegate_task() logic.
# ─────────────────────────────────────────────

# ─────────────────────────────────────────────
# SHARED CHAIN STATE (thread-safe)
# ─────────────────────────────────────────────
import threading
_chain_state = {}
_chain_lock = threading.Lock()


def make_brain_handler(my_agent_id):
    async def on_execute(ctx, event: PlatformEvent):
        pass  # Brain not used in autonomous chain
    return on_execute


def make_monitor_handler(my_agent_id):
    async def on_execute(ctx, event: PlatformEvent):
        if not isinstance(event, MessageEvent):
            return
        msg = event.payload
        content = msg.content or ""

        if my_agent_id not in content:
            return

        _emit("agent_monitor", "Autonomous workflow started. Fetching real channel data for SmartMind AIverse...")

        try:
            from youtube_api import get_videos, get_video_stats

            # Fetch last 10 videos
            videos = get_videos(10)
            if not videos:
                _emit("agent_monitor", "No videos found on channel.")
                return

            _emit("agent_monitor", f"SmartMind AIverse: Found {len(videos)} videos. Identifying weakest performer...")

            # Find lowest performing by views
            best_candidate = None
            lowest_views = float("inf")

            for v in videos:
                stats = get_video_stats(v["video_id"])
                if stats and isinstance(stats, dict):
                    views = stats.get("views", 0)
                    if views < lowest_views:
                        lowest_views = views
                        best_candidate = {
                            "video_id": v["video_id"],
                            "title": v["title"],
                            "url": v["url"],
                            "stats": stats
                        }

            if not best_candidate:
                _emit("agent_monitor", "Could not determine weakest video.")
                return

            _emit("agent_monitor",
                  f"Weakest video identified: '{best_candidate['title'][:60]}' "
                  f"with {lowest_views} views. Passing to AnalyzerAgent...")

            # Store in chain state
            with _chain_lock:
                _chain_state["monitor_result"] = best_candidate

            # Pass to analyzer
            
            analyzer_id, _ = load_agent_config("analyzer")
            payload = json.dumps({
                "title": best_candidate["title"],
                "description": "",
                "tags": "",
                "views": lowest_views,
                "likes": best_candidate["stats"].get("likes", 0),
                "video_id": best_candidate["video_id"],
                "video_url": best_candidate["url"]
            })

            from thenvoi_rest import ChatMessageRequest, ChatMessageRequestMentionsItem
            brain_link = ACTIVE_LINKS.get("brain")
            if brain_link:
                await brain_link.rest.agent_api_messages.create_agent_chat_message(
                    chat_id=ROOM_ID,
                    message=ChatMessageRequest(
                        content=f"@agent_analyzer {payload}",
                        mentions=[ChatMessageRequestMentionsItem(
                            id=analyzer_id,
                            handle="agent_analyzer"
                        )]
                    )
                )
            else:
                _emit("agent_monitor", "Brain link not ready.")

        except Exception as e:
            _emit("agent_monitor", f"Error: {e}")

    return on_execute


def make_analyzer_handler(my_agent_id):
    async def on_execute(ctx, event: PlatformEvent):
        if not isinstance(event, MessageEvent):
            return
        msg = event.payload
        content = msg.content or ""

        if my_agent_id not in content:
            return

        _emit("agent_analyzer", "Received underperforming video data. Running optimization...")

        try:
            payload_text = content.split("]]", 1)[-1].strip()
            data = json.loads(payload_text)

            title = data.get("title", "Untitled")
            description = data.get("description", "")
            tags = data.get("tags", "")
            video_id = data.get("video_id", "")
            video_url = data.get("video_url", "")
            stats = {
                "views": data.get("views", 0),
                "likes": data.get("likes", 0)
            }

            # Step 1: Score current content
            from scorer import score_video
            score = score_video(title, description, tags)
            if score and isinstance(score, dict):
                _emit("agent_analyzer",
                      f"Current score: {score.get('total_score', 0)}/100 | "
                      f"Grade: {score.get('grade', 'N/A')} | "
                      f"Priority fix: {score.get('priority_fix', 'N/A')}")

            # Step 2: Generate optimized metadata
            from metadata_updater import generate_updated_metadata
            metadata = generate_updated_metadata(
                video_title=title,
                current_description=description,
                current_tags=tags,
                analytics_data=stats
            )

            # Step 3: Optimize title via 3-pass recursive optimizer
            if metadata and isinstance(metadata, dict):
                suggested_title = metadata.get("updated_title", title)
            else:
                suggested_title = title

            _emit("agent_analyzer", "Running 3-pass recursive optimizer on title...")
            from optimizer import optimize_title
            optimized = optimize_title(suggested_title)
            final_title = optimized.get("final_content", suggested_title) if optimized else suggested_title
            final_score = optimized.get("final_score", 0) if optimized else 0

            _emit("agent_analyzer",
                  f"Optimized title: '{final_title}' | "
                  f"Optimizer score: {final_score}/10")

            # Step 4: Thumbnail text from metadata
            thumbnail_text = ""
            if metadata and isinstance(metadata, dict):
                thumbnail_text = metadata.get("thumbnail_text", "")
                if thumbnail_text:
                    _emit("agent_analyzer",
                          f"Thumbnail text suggestion: '{thumbnail_text}'")

            # Step 5: Thumbnail optimization via AI
            _emit("agent_analyzer", "Running thumbnail analysis...")
            thumb_data = {}
            try:
                from brain import ask_brain
                thumb_prompt = f"""
You are ReachIQ AI analyzing thumbnail potential for a YouTube video.
Based on the video title and content, suggest thumbnail optimization.
Return ONLY valid JSON, no extra text.

FORMAT:
{{
  "visibility_score": 0,
  "ctr_prediction": "",
  "emotional_impact": "",
  "color_suggestion": "",
  "text_overlay": "",
  "improvements": []
}}

VIDEO TITLE: {final_title}
THUMBNAIL TEXT: {thumbnail_text}
VIEWS: {data.get('views', 0)}
"""
                thumb_result = ask_brain(thumb_prompt)
                if thumb_result:
                    try:
                        clean = thumb_result.strip()
                        if "```" in clean:
                            clean = clean.split("```")[1]
                            if clean.startswith("json"):
                                clean = clean[4:]
                        thumb_data = json.loads(clean)
                        _emit("agent_analyzer",
                              f"Thumbnail: Score {thumb_data.get('visibility_score', 0)}/10 | "
                              f"CTR: {thumb_data.get('ctr_prediction', 'N/A')} | "
                              f"Overlay: '{thumb_data.get('text_overlay', thumbnail_text)}'")
                    except Exception:
                        _emit("agent_analyzer",
                              f"Thumbnail text confirmed: '{thumbnail_text}'")
            except Exception as e:
                _emit("agent_analyzer", f"Thumbnail analysis note: {e}")

            # Store full results in chain state
            analyzer_result = {
                "original_title": title,
                "optimized_title": final_title,
                "optimizer_score": final_score,
                "updated_description": metadata.get("updated_description", "") if isinstance(metadata, dict) else "",
                "updated_tags": metadata.get("updated_tags", []) if isinstance(metadata, dict) else [],
                "thumbnail_text": thumbnail_text,
                "thumbnail_analysis": thumb_data,
                "video_id": video_id,
                "video_url": video_url,
                "current_score": score.get("total_score", 0) if isinstance(score, dict) else 0
            }

            with _chain_lock:
                _chain_state["analyzer_result"] = analyzer_result

            _emit("agent_analyzer",
                  "Optimization complete. Passing to DistributionAgent...")

            # Step 6: Pass to distribution using ACTIVE_LINKS (not tools._link)
            distribution_id, _ = load_agent_config("distribution")
            dist_payload = json.dumps({
                "video_title": final_title,
                "video_url": video_url,
                "keywords": metadata.get("updated_tags", ["AI", "YouTube"])[:5] if isinstance(metadata, dict) else ["AI", "YouTube"],
                "thumbnail_text": thumbnail_text
            })

            from thenvoi_rest import ChatMessageRequest, ChatMessageRequestMentionsItem
            brain_link = ACTIVE_LINKS.get("brain")
            if brain_link:
                await brain_link.rest.agent_api_messages.create_agent_chat_message(
                    chat_id=ROOM_ID,
                    message=ChatMessageRequest(
                        content=f"@agent_distribution {dist_payload}",
                        mentions=[ChatMessageRequestMentionsItem(
                            id=distribution_id,
                            handle="agent_distribution"
                        )]
                    )
                )
            else:
                _emit("agent_analyzer", "Brain link not ready.")

        except Exception as e:
            _emit("agent_analyzer", f"Error in analyzer: {e}")
            import traceback
            print(traceback.format_exc())

    return on_execute


def make_distribution_handler(my_agent_id):
    async def on_execute(ctx, event: PlatformEvent):
        if not isinstance(event, MessageEvent):
            return
        msg = event.payload
        content = msg.content or ""

        if my_agent_id not in content:
            return

        _emit("agent_distribution", "Received optimized content. Generating promotional strategy...")

        try:
            payload_text = content.split("]]", 1)[-1].strip()
            data = json.loads(payload_text)

            video_title = data.get("video_title", "Untitled")
            video_url = data.get("video_url", "")
            keywords = data.get("keywords", ["AI", "YouTube"])
            thumbnail_text = data.get("thumbnail_text", "")

            from social_media import (generate_platform_posts,
                                       find_reddit_opportunities)

            # Generate platform posts
            posts = generate_platform_posts(
                video_title=video_title,
                video_url=video_url,
                keywords=keywords
            )

            # Find Reddit opportunities
            reddit = find_reddit_opportunities(keywords[:3])

            summary_parts = []
            if posts and isinstance(posts, dict):
                summary_parts.append(f"Posts generated for {len(posts)} platforms")
                yt_post = posts.get("youtube_community", {}).get("post", "")[:80]
                if yt_post:
                    summary_parts.append(f"YouTube: {yt_post}...")

            if reddit and isinstance(reddit, dict):
                subs = reddit.get("subreddits", [])
                sub_names = [s.get("name", "") for s in subs[:3]]
                summary_parts.append(f"Reddit opportunities: {', '.join(sub_names)}")

            if thumbnail_text:
                summary_parts.append(f"Thumbnail text confirmed: '{thumbnail_text}'")

            # Store in chain state
            with _chain_lock:
                _chain_state["distribution_result"] = {
                    "posts": posts,
                    "reddit": reddit,
                    "platforms": list(posts.keys()) if isinstance(posts, dict) else []
                }

            _emit("agent_distribution",
                  f"Distribution complete: {' | '.join(summary_parts)}")
            _emit("agent_distribution", "✅ Autonomous growth workflow complete.")

        except Exception as e:
            _emit("agent_distribution", f"Error: {e}")

    return on_execute


# ─────────────────────────────────────────────
# RUNTIME WIRING
# ─────────────────────────────────────────────

AGENT_DEFS = {
    "brain": ("agent_brain", make_brain_handler),
    "analyzer": ("agent_analyzer", make_analyzer_handler),
    "monitor": ("agent_monitor", make_monitor_handler),
    "distribution": ("agent_distribution", make_distribution_handler),
}

ACTIVE_LINKS = {}
async def run_all_agents():
    """Connects all 4 agents and runs until cancelled."""
    runtimes = []

    for config_name, (display_name, handler_factory) in AGENT_DEFS.items():
        agent_id, api_key = load_agent_config(config_name)
        link = BandLink(
            agent_id=agent_id,
            api_key=api_key,
            ws_url=WS_URL,
            rest_url=REST_URL,
        )
        runtime = AgentRuntime(link, agent_id=agent_id, on_execute=handler_factory(agent_id))
        runtimes.append((display_name, link, runtime))
        ACTIVE_LINKS[config_name] = link
        _emit(display_name, "Connecting to Band...")

    # Start all runtimes (connects + subscribes to rooms)
    for display_name, link, runtime in runtimes:
        await runtime.start()
        _emit(display_name, "Connected and listening on Band.")

    # Keep all websocket connections alive concurrently
    await asyncio.gather(*[link.run_forever() for _, link, _ in runtimes])


# ─────────────────────────────────────────────
# THREADED ENTRYPOINT FOR STREAMLIT
# ─────────────────────────────────────────────

_bridge_thread = None
_bridge_loop = None


def start_band_bridge():
    """
    Starts the Band bridge in a background thread with its own event loop.
    Safe to call from Streamlit (non-blocking). Call once per session.
    """
    global _bridge_thread, _bridge_loop

    if _bridge_thread and _bridge_thread.is_alive():
        return False  # already running

    def _runner():
        global _bridge_loop
        _bridge_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_bridge_loop)
        try:
            _bridge_loop.run_until_complete(run_all_agents())
        except Exception as e:
            _emit("System", f"Band bridge stopped: {e}")

    _bridge_thread = threading.Thread(target=_runner, daemon=True)
    _bridge_thread.start()
    return True


def is_bridge_running():
    return _bridge_thread is not None and _bridge_thread.is_alive()


def drain_events():
    """Returns all currently queued events (non-blocking)."""
    events = []
    while True:
        try:
            events.append(EVENT_QUEUE.get_nowait())
        except queue_module.Empty:
            break
    return events


def send_task_to_band(task_text="START"):
    if not ROOM_ID:
        _emit("System", "BAND_ROOM_ID not set.")
        return False

    link = ACTIVE_LINKS.get("analyzer")
    if not link:
        _emit("System", "Analyzer link not ready.")
        return False

    # Clear previous chain state
    with _chain_lock:
        _chain_state.clear()

    async def _send():
        from thenvoi_rest import ChatMessageRequest, ChatMessageRequestMentionsItem
        monitor_id, _ = load_agent_config("monitor")
        result = await link.rest.agent_api_messages.create_agent_chat_message(
            chat_id=ROOM_ID,
            message=ChatMessageRequest(
                content=f"@agent_monitor {task_text}",
                mentions=[ChatMessageRequestMentionsItem(
                    id=monitor_id,
                    handle="agent_monitor"
                )]
            )
        )
        print(f">>> chain kickoff sent: {result}")

    if _bridge_loop and _bridge_loop.is_running():
        future = asyncio.run_coroutine_threadsafe(_send(), _bridge_loop)
        try:
            future.result(timeout=15)
        except Exception as e:
            print(f">>> kickoff error: {e}")
            return False
    return True


def get_chain_state():
    with _chain_lock:
        return dict(_chain_state)

# ─────────────────────────────────────────────
# STANDALONE TEST (terminal / Band chatroom demo)
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 55)
    print("ReachIQ AI — Band Live Coordination Bridge")
    print("=" * 55)
    print("Connecting BrainAgent, AnalyzerAgent, MonitorAgent, "
          "DistributionAgent to Band...")
    print("Open your Band chat room and @mention BrainAgent to test.")
    print("Press Ctrl+C to stop.\n")

    try:
        asyncio.run(run_all_agents())
    except KeyboardInterrupt:
        print("\nStopped.")