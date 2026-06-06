import os
import datetime
import json
import time

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ─────────────────────────────────────────────
# REACHIQ AI — OBSERVABILITY
# Langfuse v4 API
# ─────────────────────────────────────────────

# Initialize Langfuse v4
try:
    from langfuse import get_client
    langfuse = get_client()
    LANGFUSE_ENABLED = True
    print("Langfuse observability enabled.")
except Exception as e:
    print(f"Langfuse init note: {e}")
    LANGFUSE_ENABLED = False


def log_locally(action, input_data,
                output_data, duration_ms, status):
    """
    Local logging as backup.
    Always runs regardless of Langfuse status.
    """
    os.makedirs("logs", exist_ok=True)
    log_file = os.path.join(
        "logs",
        f"observability_{datetime.date.today()}.json"
    )

    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "action": action,
        "input": str(input_data)[:300],
        "output": str(output_data)[:300],
        "duration_ms": duration_ms,
        "status": status
    }

    logs = []
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            try:
                logs = json.load(f)
            except:
                logs = []

    logs.append(entry)

    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)


def trace_agent_action(action_name, input_data,
                        output_data, duration_ms=0,
                        status="success", metadata=None):
    """
    Traces every agent action to Langfuse v4.
    """
    log_locally(action_name, input_data,
                output_data, duration_ms, status)

    if not LANGFUSE_ENABLED:
        return None

    try:
        with langfuse.start_as_current_observation(
            as_type="span",
            name=f"reachiq_{action_name}",
            input=str(input_data)[:500],
            output=str(output_data)[:500],
            metadata={
                "duration_ms": duration_ms,
                "status": status,
                "date": datetime.date.today().isoformat(),
                **(metadata or {})
            }
        ):
            pass
        return True

    except Exception as e:
        print(f"Trace note: {e}")
        return None


def trace_brain_call(prompt, response,
                     duration_ms=0, tokens_used=0):
    """
    Traces every AI brain call in Langfuse v4.
    """
    log_locally(
        "brain_call",
        prompt[:200],
        response[:200] if response else "None",
        duration_ms,
        "success" if response else "failed"
    )

    if not LANGFUSE_ENABLED:
        return None

    try:
        with langfuse.start_as_current_observation(
            as_type="generation",
            name="groq_llama_call",
            input=prompt[:500],
            output=response[:500] if response else "",
            model="llama-3.3-70b-versatile",
            metadata={
                "duration_ms": duration_ms,
                "tokens_used": tokens_used,
                "date": datetime.date.today().isoformat()
            }
        ):
            pass
        return True

    except Exception as e:
        print(f"Generation trace note: {e}")
        return None


def measure_and_trace(action_name, func, *args, **kwargs):
    """
    Wrapper that measures time and traces any function.
    """
    start = time.time()
    status = "success"
    result = None

    try:
        result = func(*args, **kwargs)
    except Exception as e:
        status = "failed"
        print(f"{action_name} failed: {e}")

    duration_ms = int((time.time() - start) * 1000)

    trace_agent_action(
        action_name=action_name,
        input_data=str(args)[:200],
        output_data=str(result)[:200],
        duration_ms=duration_ms,
        status=status
    )

    return result


def get_daily_performance_summary():
    """
    Reads today's log and generates a summary.
    """
    log_file = os.path.join(
        "logs",
        f"observability_{datetime.date.today()}.json"
    )

    if not os.path.exists(log_file):
        return "No activity logged today."

    with open(log_file, "r", encoding="utf-8") as f:
        try:
            logs = json.load(f)
        except:
            return "Could not read log file."

    if not logs:
        return "No activity logged today."

    total_actions = len(logs)
    successful = sum(1 for l in logs
                     if l.get("status") == "success")
    failed = total_actions - successful
    avg_duration = sum(l.get("duration_ms", 0)
                       for l in logs) / total_actions

    actions_done = list(set(l.get("action", "")
                            for l in logs))

    return {
        "date": datetime.date.today().isoformat(),
        "total_actions": total_actions,
        "successful": successful,
        "failed": failed,
        "success_rate": f"{(successful/total_actions)*100:.1f}%",
        "avg_duration_ms": int(avg_duration),
        "actions_performed": actions_done
    }


def view_recent_traces(limit=10):
    """
    Shows the most recent agent actions.
    """
    log_file = os.path.join(
        "logs",
        f"observability_{datetime.date.today()}.json"
    )

    if not os.path.exists(log_file):
        print("No traces today.")
        return

    with open(log_file, "r", encoding="utf-8") as f:
        try:
            logs = json.load(f)
        except:
            print("Could not read traces.")
            return

    recent = logs[-limit:]
    print(f"\nLast {len(recent)} agent actions:")
    print("-" * 40)
    for log in recent:
        print(f"Time: {log['timestamp'][11:19]}")
        print(f"Action: {log['action']}")
        print(f"Status: {log['status']}")
        print(f"Duration: {log['duration_ms']}ms")
        print("-" * 40)


if __name__ == "__main__":
    from brain import ask_brain

    print("=" * 55)
    print("ReachIQ AI — Observability System Test")
    print("=" * 55)

    print("\nTesting action trace...")
    trace_agent_action(
        action_name="test_action",
        input_data="test input",
        output_data="test output",
        duration_ms=150,
        status="success"
    )
    print("Action traced.")

    print("\nTesting brain call trace...")
    start = time.time()
    response = ask_brain("Say one word.")
    duration = int((time.time() - start) * 1000)
    trace_brain_call(
        prompt="Say one word.",
        response=response,
        duration_ms=duration
    )
    print(f"Brain response: {response}")
    print(f"Duration: {duration}ms")

    print("\nTesting measure and trace wrapper...")
    result = measure_and_trace(
        "test_brain",
        ask_brain,
        "What is AI in one sentence?"
    )
    print(f"Result: {result[:100] if result else 'None'}")

    print("\nDaily performance summary:")
    summary = get_daily_performance_summary()
    if isinstance(summary, dict):
        print(json.dumps(summary, indent=2))
    else:
        print(summary)

    view_recent_traces(5)
    print("\nObservability system ready.")