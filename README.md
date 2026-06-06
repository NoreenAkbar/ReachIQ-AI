# ReachIQ AI 🚀
### Generative Growth as a Service

An intelligent multi-agent YouTube growth optimization system that analyzes, monitors, and distributes your content automatically.

Built by **Noreen Akbar** | AI Researcher & Agent Developer

---

## What ReachIQ AI Does

ReachIQ AI is a fully automated YouTube growth agent that works across the entire content lifecycle:

- **Pre-Upload** — Scores your title, script, tags and thumbnail before you upload. Tells you exactly what to fix.
- **Post-Upload** — Monitors real YouTube Analytics daily and suggests metadata improvements automatically.
- **Distribution** — Finds relevant Reddit, Quora, LinkedIn and Facebook discussions and drafts ready-to-post comments with your video link.
- **Competition Intelligence** — Analyzes top performing videos in your niche and tells you exactly how to outperform them.
- **Memory & Learning** — Learns from your channel's performance history and gives smarter suggestions over time.

---

## Architecture

ReachIQ AI is built as a multi-agent system with 14 specialized modules:

| Module | Purpose |
|--------|---------|
| brain.py | AI brain with Groq Llama 3.3 70B, Ollama fallback |
| analyzer.py | Pre-upload content analysis |
| scorer.py | 6-dimension video scoring system |
| monitor.py | Real YouTube Analytics tracking |
| metadata_updater.py | Auto metadata optimization |
| keyword_tracker.py | SEO and competition analysis |
| social_media.py | Multi-platform post generation |
| memory.py | Mem0 + Qdrant learning system |
| observability.py | Langfuse tracing and logging |
| security.py | Input validation and guardrails |
| automation.py | Pipeline orchestrator |
| main.py | Master control with MCP registry |

---

## Tech Stack (100% Free)

- **AI Brain** — Groq Llama 3.3 70B (primary), Ollama llama3.2:1b (fallback)
- **Agent Framework** — LangGraph compatible architecture
- **Memory** — Mem0 self-hosted + Qdrant vector database
- **Observability** — Langfuse tracing
- **Security** — Custom guardrails with prompt injection protection
- **YouTube** — YouTube Data API v3 + YouTube Analytics API
- **Automation** — n8n self-hosted (coming)

---

## Setup

**Requirements:**
- Python 3.14+
- Ollama installed locally
- Groq API key (free at console.groq.com)
- YouTube Data API key (free at console.cloud.google.com)

**Installation:**

```bash
git clone https://github.com/NoreenAkbar/ReachIQ-AI.git
cd ReachIQ-AI
pip install -r requirements.txt
```

**Configure .env:**
**Run:**

```bash
python main.py
```

---

## Features

- Human Approval Gate before any content goes live
- MCP Tool Registry for modular agent expansion
- Real YouTube Analytics integration (OAuth)
- Competitor video analysis
- Platform-specific social media post generation
- Daily intelligence reports saved as files
- Security layer blocking prompt injection and harmful content
- Full action logging and observability

---

## License

Copyright (C) 2026 Noreen Akbar

This project is licensed under AGPL-3.0.
Commercial use requires explicit written permission from the author.
Contact: noreenakbar438@gmail.com

---

## Project Status

Currently in active development as part of:
- Band of Agents Hackathon (lablab.ai) — June 2026
- AMD Developer Hackathon ACT II — July 2026

*Built with zero budget, maximum ambition.*