import os
os.environ["HF_HOME"] = "E:/Developer_Space/huggingface_cache"
os.environ["TRANSFORMERS_CACHE"] = "E:/Developer_Space/huggingface_cache"
import os
import json
import datetime
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from mem0 import Memory
from brain import ask_brain
from config import GROQ_API_KEY

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ─────────────────────────────────────────────
# REACHIQ AI — MEMORY SYSTEM
# Mem0 handles conversational memory
# Qdrant handles vector search and patterns
# Together they make the agent learn over time
# ─────────────────────────────────────────────

# Initialize Qdrant locally — no server needed
qdrant_client = QdrantClient(path="E:/Developer_Space/youtube-ai-agent/qdrant_storage")

# Collection names
PERFORMANCE_COLLECTION = "video_performance"
PATTERNS_COLLECTION = "channel_patterns"
KEYWORDS_COLLECTION = "keyword_history"

# Initialize Mem0 with Groq
mem0_config = {
    "llm": {
        "provider": "groq",
        "config": {
            "model": "llama-3.3-70b-versatile",
            "api_key": GROQ_API_KEY,
            "temperature": 0.1,
            "max_tokens": 2000
        }
    },
    "embedder": {
        "provider": "huggingface",
        "config": {
            "model": "multi-qa-MiniLM-L6-cos-v1"
        }
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": "reachiq_memory",
            "path": "E:/Developer_Space/youtube-ai-agent/qdrant_storage"
        }
    }
}

try:
    memory = Memory.from_config(mem0_config)
    print("Mem0 initialized successfully.")
except Exception as e:
    print(f"Mem0 init note: {e}")
    memory = None


def setup_collections():
    """
    Creates Qdrant collections if they dont exist.
    Run once on first setup.
    """
    collections = [
        PERFORMANCE_COLLECTION,
        PATTERNS_COLLECTION,
        KEYWORDS_COLLECTION
    ]

    existing = [c.name for c in
                qdrant_client.get_collections().collections]

    for col in collections:
        if col not in existing:
            qdrant_client.create_collection(
                collection_name=col,
                vectors_config=VectorParams(
                    size=384,
                    distance=Distance.COSINE
                )
            )
            print(f"Created collection: {col}")
        else:
            print(f"Collection exists: {col}")


def store_video_performance(video_id, title, stats, suggestions):
    """
    Stores video performance data and AI suggestions.
    Agent learns what worked and what did not.
    """
    record = {
        "video_id": video_id,
        "title": title,
        "date": datetime.date.today().isoformat(),
        "stats": stats if isinstance(stats, dict) else {},
        "suggestions": suggestions if isinstance(
            suggestions, dict) else {},
        "views": stats.get("views", 0) if isinstance(
            stats, dict) else 0,
        "watch_time": stats.get(
            "watch_time_minutes", 0) if isinstance(
            stats, dict) else 0
    }

    # Save to local JSON database
    db_file = "performance_history.json"
    history = []

    if os.path.exists(db_file):
        with open(db_file, "r", encoding="utf-8") as f:
            try:
                history = json.load(f)
            except:
                history = []

    # Update existing or add new
    updated = False
    for i, item in enumerate(history):
        if item.get("video_id") == video_id:
            history[i] = record
            updated = True
            break

    if not updated:
        history.append(record)

    with open(db_file, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

    # Store in Mem0 for intelligent retrieval
    if memory:
        try:
            memory.add(
                f"Video {title} had {record['views']} views "
                f"and {record['watch_time']} minutes watch time.",
                user_id="reachiq_channel"
            )
        except Exception as e:
            print(f"Mem0 store note: {e}")

    print(f"Performance stored for: {title[:40]}")
    return record


def get_channel_patterns():
    """
    Analyzes stored performance history to find
    what content patterns work best for your channel.
    """
    db_file = "performance_history.json"

    if not os.path.exists(db_file):
        return None

    with open(db_file, "r", encoding="utf-8") as f:
        try:
            history = json.load(f)
        except:
            return None

    if not history:
        return None

    # Build pattern analysis prompt
    history_text = "\n".join([
        f"- {h['title']}: {h['views']} views, "
        f"{h['watch_time']} min watch time"
        for h in history
    ])

    prompt = f"""
You are ReachIQ AI analyzing channel performance history.

Study this performance data and identify what is working.

Return ONLY valid JSON, no extra text, no markdown.

FORMAT:
{{
  "best_performing_topics": [],
  "worst_performing_topics": [],
  "optimal_title_patterns": [],
  "best_upload_insights": [],
  "recommended_next_topics": [],
  "channel_growth_trend": "",
  "key_learning": ""
}}

PERFORMANCE HISTORY:
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


def remember_keyword_performance(keyword, video_id,
                                  views_gained):
    """
    Tracks which keywords actually drove views.
    Agent learns which keywords to prioritize.
    """
    db_file = "keyword_history.json"
    history = []

    if os.path.exists(db_file):
        with open(db_file, "r", encoding="utf-8") as f:
            try:
                history = json.load(f)
            except:
                history = []

    history.append({
        "keyword": keyword,
        "video_id": video_id,
        "views_gained": views_gained,
        "date": datetime.date.today().isoformat()
    })

    with open(db_file, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

    if memory:
        try:
            memory.add(
                f"Keyword '{keyword}' drove {views_gained} "
                f"views for video {video_id}.",
                user_id="reachiq_channel"
            )
        except Exception as e:
            print(f"Mem0 keyword note: {e}")


def get_smart_suggestions(context):
    """
    Uses memory to give smarter suggestions
    based on what has worked before.
    """
    if not memory:
        return None

    try:
        memories = memory.search(
            context,
            user_id="reachiq_channel",
            limit=5
        )

        if memories and memories.get("results"):
            memory_text = "\n".join([
                m.get("memory", "")
                for m in memories["results"]
            ])

            prompt = f"""
Based on this channel history, give smart suggestions.

Return ONLY valid JSON, no extra text, no markdown.

FORMAT:
{{
  "smart_suggestions": [],
  "avoid_these": [],
  "double_down_on": [],
  "predicted_best_topic": ""
}}

CHANNEL MEMORY:
{memory_text}

CURRENT CONTEXT: {context}
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
    except Exception as e:
        print(f"Memory search note: {e}")
    return None


def view_memory_stats():
    """
    Shows current memory statistics.
    """
    print("=" * 55)
    print("ReachIQ AI — Memory Statistics")
    print("=" * 55)

    # Performance history
    if os.path.exists("performance_history.json"):
        with open("performance_history.json",
                  "r", encoding="utf-8") as f:
            try:
                history = json.load(f)
                print(f"Videos tracked: {len(history)}")
                if history:
                    best = max(history,
                               key=lambda x: x.get("views", 0))
                    print(f"Best performer: {best['title'][:40]}")
                    print(f"Best views: {best['views']}")
            except:
                print("Performance history empty.")
    else:
        print("No performance history yet.")

    # Keyword history
    if os.path.exists("keyword_history.json"):
        with open("keyword_history.json",
                  "r", encoding="utf-8") as f:
            try:
                kw_history = json.load(f)
                print(f"Keywords tracked: {len(kw_history)}")
            except:
                print("Keyword history empty.")
    else:
        print("No keyword history yet.")


if __name__ == "__main__":
    print("=" * 55)
    print("ReachIQ AI — Memory System Setup")
    print("=" * 55)

    # Setup collections
    print("\nSetting up Qdrant collections...")
    setup_collections()

    # Test storing performance
    print("\nTesting performance storage...")
    store_video_performance(
        video_id="test123",
        title="Test Video",
        stats={"views": 100, "watch_time_minutes": 50},
        suggestions={"update_title": True}
    )

    # Test pattern analysis
    print("\nTesting pattern analysis...")
    patterns = get_channel_patterns()
    if patterns and isinstance(patterns, dict):
        print("Channel patterns found:")
        print(json.dumps(patterns, indent=2))

    # View stats
    print()
    view_memory_stats()

    print("\nMemory system ready.")