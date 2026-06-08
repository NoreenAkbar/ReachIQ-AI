import os
import datetime
import json

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ─────────────────────────────────────────────
# REACHIQ AI — BRAIN AGENT
# Role: Central intelligence coordinator
# Receives tasks, decides which agent handles them
# Delegates to Analyzer, Monitor, Distribution
# ─────────────────────────────────────────────

from brain import ask_brain, ask_with_fallback
from observability import trace_agent_action
from security import secure_input

# ── AGENT IDENTITY ──
AGENT_ID = "brain_agent"
AGENT_NAME = "BrainAgent"
AGENT_ROLE = "Central coordinator and decision maker"
AGENT_VERSION = "1.0"

AGENT_CAPABILITIES = [
    "route_task",
    "analyze_intent",
    "coordinate_agents",
    "generate_strategy",
    "validate_output"
]


# ── BAND CONNECTION LAYER ──
# These functions will be replaced with real
# Band SDK calls on June 12 hackathon kickoff.
# Structure is already Band-compatible.

class BandConnection:
    """
    Placeholder Band connection.
    Replace with real Band SDK on June 12.

    On June 12 after getting SDK:
    from band_sdk import BandAgent
    self.band = BandAgent(
        agent_id=AGENT_ID,
        api_key=BAND_API_KEY
    )
    """

    def __init__(self):
        self.connected = False
        self.message_log = []
        print(f"{AGENT_NAME} initialized in local mode.")
        print("Connect to Band SDK on June 12.")

    def register(self, agent_id, capabilities):
        """Register agent with Band platform"""
        # Real Band SDK: self.band.register(agent_id, capabilities)
        print(f"[BAND] {agent_id} registered with capabilities:")
        for cap in capabilities:
            print(f"  - {cap}")
        self.connected = True
        return True

    def send_message(self, to_agent, message_type, payload):
        """Send message to another agent through Band"""
        message = {
            "from": AGENT_ID,
            "to": to_agent,
            "type": message_type,
            "payload": payload,
            "timestamp": datetime.datetime.now().isoformat()
        }
        # Real Band SDK: self.band.send(to_agent, message)
        self.message_log.append(message)
        self._log_message(message)
        return message

    def receive_message(self, from_agent=None):
        """Receive message from Band"""
        # Real Band SDK: return self.band.receive()
        if self.message_log:
            return self.message_log[-1]
        return None

    def _log_message(self, message):
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


# Initialize Band connection
band = BandConnection()


# ── BRAIN AGENT CORE FUNCTIONS ──

def initialize():
    """Register BrainAgent with Band"""
    return band.register(AGENT_ID, AGENT_CAPABILITIES)


def analyze_task_intent(task_description):
    """
    Understands what kind of task this is
    and decides which agent should handle it.
    """
    prompt = f"""
You are ReachIQ AI BrainAgent coordinator.

Analyze this task and decide which agent should handle it.

Available agents:
- analyzer_agent: pre-upload content analysis, scoring
- monitor_agent: post-upload tracking, metadata updates
- distribution_agent: social media, keywords, promotion

Return ONLY valid JSON, no extra text.

FORMAT:
{{
  "task_type": "",
  "primary_agent": "",
  "secondary_agent": "",
  "reasoning": "",
  "priority": "high/medium/low",
  "requires_human_approval": false
}}

TASK: {task_description}
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
            return None
    return None


def delegate_task(task_description, task_data=None):
    """
    Main coordination function.
    Analyzes task and delegates to correct agent.
    """
    print(f"\n[{AGENT_NAME}] Received task: {task_description[:50]}")

    # Security check
    safe_task = secure_input(task_description, "task")
    if not safe_task:
        print(f"[{AGENT_NAME}] Task blocked by security.")
        return None

    # Analyze intent
    intent = analyze_task_intent(task_description)
    if not intent:
        print(f"[{AGENT_NAME}] Could not analyze task intent.")
        return None

    print(f"[{AGENT_NAME}] Task type: {intent.get('task_type')}")
    print(f"[{AGENT_NAME}] Routing to: "
          f"{intent.get('primary_agent')}")

    # Send to appropriate agent through Band
    message = band.send_message(
        to_agent=intent.get("primary_agent"),
        message_type="task_assignment",
        payload={
            "task": task_description,
            "data": task_data or {},
            "intent": intent,
            "priority": intent.get("priority", "medium")
        }
    )

    trace_agent_action(
        "brain_agent_delegation",
        task_description[:100],
        f"Delegated to {intent.get('primary_agent')}",
        status="success"
    )

    return {
        "status": "delegated",
        "assigned_to": intent.get("primary_agent"),
        "message_id": message.get("timestamp"),
        "intent": intent
    }


def generate_strategy(channel_context):
    """
    Generates overall growth strategy
    based on channel data and memory.
    """
    prompt = f"""
You are ReachIQ AI BrainAgent generating a YouTube growth strategy.

Based on this channel context create a specific actionable strategy.

Return ONLY valid JSON, no extra text.

FORMAT:
{{
  "immediate_actions": [],
  "this_week_focus": "",
  "content_recommendations": [],
  "optimization_priorities": [],
  "growth_prediction": ""
}}

CHANNEL CONTEXT: {str(channel_context)[:500]}
"""
    result = ask_with_fallback(prompt, task_type="analysis")
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


def get_agent_status():
    """Returns current agent status"""
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
    print("ReachIQ AI — BrainAgent Test")
    print("=" * 55)

    # Initialize
    initialize()

    # Test task routing
    print("\nTest 1 — Route pre-upload task:")
    result = delegate_task(
        "Analyze my new video title before upload",
        {"title": "How AI is Changing Education"}
    )
    if result:
        print(json.dumps(result, indent=2))

    # Test task routing for monitoring
    print("\nTest 2 — Route monitoring task:")
    result = delegate_task(
        "Check my latest video performance and suggest improvements",
        {"video_id": "hrVNiuZ0ooc"}
    )
    if result:
        print(json.dumps(result, indent=2))

    # Test strategy generation
    print("\nTest 3 — Generate channel strategy:")
    strategy = generate_strategy({
        "channel": "SmartMindAIverse",
        "niche": "AI education",
        "recent_views": 146,
        "videos": 10
    })
    if strategy and isinstance(strategy, dict):
        print(json.dumps(strategy, indent=2))

    # Agent status
    print("\nAgent Status:")
    print(json.dumps(get_agent_status(), indent=2))

    print("\nBrainAgent ready for Band connection.")