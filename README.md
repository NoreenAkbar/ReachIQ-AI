# ReachIQ AI 🚀
### AI-Powered Competitive Intelligence for YouTube Creators


**The world's first autonomous multi-agent YouTube growth system powered by Band Framework.**

4 specialized AI agents collaborate via Band to analyze, monitor, and grow your channel — completely automatically.

Built by **Noreen Akbar** | AI Researcher & Agent Developer | Team: instinctagent

---

## 🔴 Live Demo
**[▶️ Try ReachIQ AI Live](https://reachiq-ai.streamlit.app/)**

---
## 🚀 AMD Deployment

ReachIQ's Competitive Intelligence engine was successfully deployed and validated on **AMD Developer Cloud**.

### AMD Stack

- AMD Developer Cloud
- ROCm 7.2
- vLLM
- Google Gemma 3 4B (`google/gemma-3-4b-it`)

### Validation

- ✅ Gemma model successfully loaded on AMD GPU
- ✅ vLLM inference server started successfully
- ✅ OpenAI-compatible `/v1/models` endpoint validated
- ✅ Competitive Intelligence pipeline verified on AMD compute

> Public endpoint exposure was unavailable in the managed notebook environment. AMD compute usage was successfully demonstrated using ROCm, vLLM and Gemma 3 running on AMD Developer Cloud.

## Project Pipline
Competitor Videos
        ↓
Whisper + OCR
        ↓
Embedding Generation
        ↓
Supabase pgvector
        ↓
Semantic Retrieval (RAG)
        ↓
Gemma 3 4B (AMD ROCm + vLLM)
        ↓
Executive Competitive Intelligence Report

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

ReachIQ AI v2.0 —  specialized modules:

| Module | Purpose |
|--------|---------|
| competitive_engine.py | Generates AI-powered competitive intelligence reports from competitor videos |
| query.py | Retrieves relevant competitor knowledge using semantic search and generates insights |
| storage.py | Handles Supabase storage, embeddings, transcripts and vector retrieval |
| ingest.py | Downloads, transcribes, OCRs and indexes competitor YouTube videos into the RAG knowledge base | 
| llm_provider.py | Unified LLM layer supporting AMD Gemma (vLLM), Groq and future providers |
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
| -------------- | ------------------------------------ |
| 🚀 AMD Compute | AMD Developer Cloud + ROCm 7.2       |
| 🤖 LLM         | Gemma 3 4B (AMD) + Groq GPT-OSS 120B |
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
- **Competitive Intelligence** — AI-powered analysis of competitor videos using Video RAG running on AMD compute
- ✅ Video RAG
- ✅ Competitive Intelligence
- ✅ AMD-powered Gemma inference
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
- **Direct competitors:** Differentiator: First AI-powered YouTube Competitive Intelligence platform combining Video RAG, autonomous agents, and AMD-accelerated inference.

---

## Roadmap

- [ ] Next.js frontend rebuild
- [ ] Mobile dashboard
- [ ] Payoneer billing integration
- [ ] Multi-channel support

---

## Project Status

✅ Band of Agents Hackathon

✅ AMD Developer Hackathon ACT II

*Built with zero budget, maximum ambition. Solo developer.*

---

## License

Copyright (C) 2026 Noreen Akbar

Licensed under AGPL-3.0.
Commercial use requires explicit written permission.
Contact: noreenakbar06@gmail.com
