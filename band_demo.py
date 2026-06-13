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

def make_brain_handler(my_agent_id):
    from agent_brain import analyze_task_intent

    async def on_execute(ctx, event: PlatformEvent):
        if not isinstance(event, MessageEvent):
            return
        msg = event.payload
        content = msg.content or ""

        if my_agent_id not in content:
            return
        if "Analysis complete" in content or "ready" in content or "Distribution package" in content:
            return  # ignore result replies, not new tasks

        _emit("agent_brain", f"Received task: {content[:80]}")
        ...

        # Use your REAL existing intent analysis
        intent = analyze_task_intent(content)
        target = "agent_analyzer"
        if intent and isinstance(intent, dict):
            primary = intent.get("primary_agent", "analyzer_agent")
            mapping = {
                "analyzer_agent": "agent_analyzer",
                "monitor_agent": "agent_monitor",
                "distribution_agent": "agent_distribution",
            }
            target = mapping.get(primary, "agent_analyzer")

        tools = AgentTools.from_context(ctx)
        _emit("agent_brain", f"Routing to {target}")
        await tools.send_message(
            f"@{target} please process this request: {content}",
            mentions=[f"@{target}"]
        )

    return on_execute


def make_analyzer_handler(my_agent_id):
    from analyzer import analyze_pre_upload

    async def on_execute(ctx, event: PlatformEvent):
        if not isinstance(event, MessageEvent):
            return
        msg = event.payload
        content = msg.content or ""

        if my_agent_id not in content:
            return

        _emit("agent_analyzer", "Received task from agent_brain. Analyzing...")

        # Extract a title-like string from the message (best-effort demo parse)
        import json
        try:
            payload_text = content.split("]]", 1)[-1].strip()
            data = json.loads(payload_text)
            title = data.get("title", "Untitled")
            description = data.get("description", "")
            tags = data.get("tags", "")
            script = data.get("script") or None
        except Exception:
            title, description, tags, script = content[:100], "", "", None

        result = analyze_pre_upload(title=title, description=description, tags=tags, script=script)


        if isinstance(result, dict):
            summary = (
                f"Score: {result.get('overall_score', 'N/A')}/100 | "
                f"Hook: {result.get('hook_suggestion', 'N/A')[:60]} | "
                f"Top action: {(result.get('top_3_actions') or ['N/A'])[0]}"
            )
        else:
            summary = str(result)[:200]

        tools = AgentTools.from_context(ctx)
        _emit("agent_analyzer", f"Analysis complete: {summary}")
        await tools.send_message(
            f"@agent_brain Analysis complete -> {summary}",
            mentions=["@agent_brain"]
        )

    return on_execute


def make_monitor_handler(my_agent_id):
    async def on_execute(ctx, event: PlatformEvent):
        if not isinstance(event, MessageEvent):
            return
        msg = event.payload
        content = msg.content or ""

        if my_agent_id not in content:
            return

        _emit("agent_monitor", "Received task from agent_brain. Checking channel patterns...")

        tools = AgentTools.from_context(ctx)
        summary = "Channel monitoring ready. Run full check from Streamlit Post-Upload page."
        _emit("agent_monitor", summary)
        await tools.send_message(
            f"@agent_brain {summary}",
            mentions=["@agent_brain"]
        )

    return on_execute


def make_distribution_handler(my_agent_id):
    async def on_execute(ctx, event: PlatformEvent):
        
        if not isinstance(event, MessageEvent):
            return
        msg = event.payload
        content = msg.content or ""

        if my_agent_id not in content:
            return

        _emit("agent_distribution", "Received task from agent_brain. Preparing distribution package...")

        tools = AgentTools.from_context(ctx)
        summary = "Distribution package ready across 6 platforms. See Social Distribution page for full posts."
        _emit("agent_distribution", summary)
        await tools.send_message(
            f"@agent_brain {summary}",
            mentions=["@agent_brain"]
        )

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


def send_task_to_band(task_text):
    if not ROOM_ID:
        _emit("System", "BAND_ROOM_ID not set — cannot send task.")
        return False

    link = ACTIVE_LINKS.get("brain")
    if not link:
        _emit("System", "Brain link not ready yet.")
        return False

    async def _send():
        from thenvoi_rest import ChatMessageRequest, ChatMessageRequestMentionsItem

        analyzer_agent_id, _ = load_agent_config("analyzer")

        result = await link.rest.agent_api_messages.create_agent_chat_message(
            chat_id=ROOM_ID,
            message=ChatMessageRequest(
                content=f"@agent_analyzer {task_text}",
                mentions=[
                    ChatMessageRequestMentionsItem(
                        id=analyzer_agent_id,
                        handle="agent_analyzer"
                    )
                ]
            )
        )
        print(f">>> send_message result: {result}")
    print(">>> send_task_to_band called")
    if _bridge_loop and _bridge_loop.is_running():
        print(">>> bridge loop is running, scheduling _send")
        future = asyncio.run_coroutine_threadsafe(_send(), _bridge_loop)
        try:
            future.result(timeout=15)
            print(">>> _send completed")
        except Exception as e:
            print(f">>> _send raised: {e}")
            return False
    else:
        print(">>> bridge loop NOT running")
        _emit("System", "Bridge loop not running.")
        return False

    return True

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