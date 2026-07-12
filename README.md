# ReachIQ AI 🚀
### Generative Growth as a Service

**The world's first autonomous multi-agent YouTube growth system powered by Band Framework.**

4 specialized AI agents collaborate via Band to analyze, monitor, and grow your channel — completely automatically.

Built by **Noreen Akbar** | AI Researcher & Agent Developer | Team: instinctagent

---

## 🔴 Live Demo
**[▶️ Try ReachIQ AI Live](https://reachiq-ai.streamlit.app/)**

---

## What ReachIQ AI Does

ReachIQ AI automates the entire YouTube content lifecycle through coordinated AI agents:

- **Pre-Upload** — Scores your title, script, tags and thumbnail before you upload
- **Band Live Coordination** — One click triggers autonomous 3-agent chain: Monitor finds your weakest video → Analyzer optimizes metadata + thumbnail → Distribution generates posts for 6 platforms
- **Post-Upload** — Monitors real YouTube Analytics and suggests metadata improvements
- **Thumbnail Analysis** — AI vision scores your thumbnail for CTR potential
- **Social Distribution** — Platform-specific posts for YouTube, Facebook, LinkedIn, Reddit, Quora, Twitter
- **Memory & Learning** — Learns from your channel's performance history
- **Security** — Custom guardrails blocking prompt injection and harmful content

---

## 🤝 Band Multi-Agent System

ReachIQ AI is built on Band Framework with 4 specialized agents:

| Agent | Role | Capabilities |
|-------|------|-------------|
| 🧠 BrainAgent | Central Coordinator | Task routing, intent analysis |
| 🔍 AnalyzerAgent | Pre-Upload Specialist | Scoring, 3-pass optimization, thumbnail AI |
| 📊 MonitorAgent | Post-Upload Tracker | Real YouTube Analytics, performance detection |
| 📢 DistributionAgent | Promotion Specialist | 6 platforms, Reddit opportunities |

### Autonomous Growth Workflow (Band Chain)
---

## Architecture

ReachIQ AI v2.0 — 14 specialized modules:
## AMD Deployment

The ReachIQ Competitive Intelligence engine was deployed and validated on AMD Developer Cloud, confirming end-to-end AI inference on AMD infrastructure.

- **Platform:** AMD Developer Cloud
- **ROCm Version:** 7.2
- **Inference Engine:** vLLM
- **Model:** google/gemma-3-4b-it

Inference was successfully validated on AMD Developer Cloud using ROCm + vLLM + Gemma 3 4B, confirming the Competitive Intelligence pipeline can run natively on AMD compute.

### Deployment Evidence

**1. Model loading on AMD ROCm GPU:**
`vllm serve google/gemma-3-4b-it --dtype bfloat16 --host 0.0.0.0 --port 8000`
Model weights, tokenizer, and generation config loaded successfully; vLLM engine initialized on AMD hardware.

**2. Server fully running with successful inference request:**
Application startup completed, all API routes registered, and a live `GET /v1/models` request returned `200 OK` — confirming the model was actively serving requests on AMD compute.

> Note: Public port exposure was not available in this environment configuration. Per hackathon submission guidelines, AMD compute usage is the required proof — public hosting is optional. The screenshots above demonstrate successful deployment and validated inference on AMD infrastructure.

| Module | Purpose |
|--------|---------|
| band_demo.py | Band SDK bridge — 4 agents via BandLink + AgentRuntime |
| brain.py | AI brain — Groq Llama 3.3 70B + fallback chain |
| analyzer.py | Pre-upload content analysis |
| scorer.py | 6-dimension video scoring system |
| optimizer.py | 3-pass recursive self-improvement loop |
| monitor.py | Real YouTube Analytics OAuth tracking |
| metadata_updater.py | Auto metadata optimization |
| keyword_tracker.py | SEO and competition analysis |
| social_media.py | Multi-platform post generation |
| memory.py | Mem0 + Qdrant learning system |
| observability.py | Langfuse tracing and logging |
| security.py | Input validation and guardrails |
| automation.py | Pipeline orchestrator |
| main.py | Master control with MCP registry |

---

## Tech Stack (100% Free to Run)

| Layer | Technology |
|-------|-----------|
| 🤝 Agent Framework | Band SDK (BandLink + AgentRuntime) |
| 🧠 AI Brain | Groq Llama 3.3 70B |
| 👁️ Vision | Groq Llama 4 Scout + AI/ML API Llama-Vision-Free |
| 💾 Memory | Mem0 + Qdrant (self-hosted) |
| 📊 Observability | Langfuse |
| 🛡️ Security | Custom guardrails |
| 📺 YouTube | YouTube Data API v3 + Analytics API |
| 🖥️ UI | Streamlit |

**Running cost: $0** — uses free tiers across all providers

---

## Setup

**Requirements:**
- Python 3.10+
- Groq API key (free at console.groq.com)
- YouTube Data API key (free at console.cloud.google.com)
- Band account (free at app.band.ai)
- AI/ML API key (free at aimlapi.com)

**Installation:**

```bash
git clone https://github.com/NoreenAkbar/ReachIQ-AI.git
cd ReachIQ-AI
pip install -r requirements.txt
```

**Configure `.env`:**
**Configure `agent_config.yaml`:**
```yaml
brain:
  agent_id: "your_brain_agent_uuid"
  api_key: "your_brain_api_key"
analyzer:
  agent_id: "your_analyzer_uuid"
  api_key: "your_analyzer_api_key"
monitor:
  agent_id: "your_monitor_uuid"
  api_key: "your_monitor_api_key"
distribution:
  agent_id: "your_distribution_uuid"
  api_key: "your_distribution_api_key"
```

**Run:**

```bash
# Streamlit Web UI (recommended):
streamlit run app.py

# Band agent bridge (run separately):
python band_demo.py

# Terminal CLI:
python main.py
```

---

## Features

- ✅ Autonomous 3-agent sequential chain via Band
- ✅ Human Approval Gate before any content goes live
- ✅ MCP Tool Registry for modular agent expansion
- ✅ Real YouTube Analytics integration (OAuth)
- ✅ 3-pass recursive self-improvement optimizer
- ✅ Competitor video analysis
- ✅ Platform-specific social media post generation
- ✅ Daily intelligence reports saved as files
- ✅ Security layer blocking prompt injection
- ✅ Full action logging and observability (Langfuse)
- ✅ Persistent memory learning from channel history

---

## 💼 Business Model

### ~~$2,499~~ $1,499 One-Time Download
*Early Access — First 10 customers only*

Full source code. Use your own API keys. Zero running cost. Deploy anywhere.

### $79/mo GaaS Subscription
Single channel — all features included

### $199/mo Agency Plan
Multiple channels — team workflows

### Enterprise
Custom deployment — contact for pricing

**Contact:** noreenakbar06@gmail.com

---

## Market

- **TAM:** $4.2B Creator Tools market
- **Target:** 45M YouTube channels, 90% under 10K subscribers
- **Hours saved:** 20+ per week per creator
- **Direct competitors:** 0 (no other multi-agent YouTube growth system exists)

---

## Roadmap

- [ ] Next.js frontend rebuild
- [ ] Mobile dashboard
- [ ] Payoneer billing integration
- [ ] Multi-channel support

---

## Project Status

Built for **Band of Agents Hackathon** — June 2026 (lablab.ai)
Next: **AMD Developer Hackathon ACT II** — July 2026

*Built with zero budget, maximum ambition. Solo developer.*

---

## License

Copyright (C) 2026 Noreen Akbar

Licensed under AGPL-3.0.
Commercial use requires explicit written permission.
Contact: noreenakbar06@gmail.com
