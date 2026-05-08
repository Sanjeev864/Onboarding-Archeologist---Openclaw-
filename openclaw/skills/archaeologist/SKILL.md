---
name: archaeologist
description: OpenClaw skill for autonomous repository archaeology and onboarding intelligence
author: Onboarding Archaeologist Team
version: 1.0.0
user-invocable: true
---

# Onboarding Archaeologist

This OpenClaw skill exposes the FastAPI backend as Telegram-ready commands and LLM tools. The backend remains the source of truth for analysis, agent reasoning, onboarding generation, oracle Q&A, and feedback learning.

## Commands

- `/analyze-autonomous owner/repo` runs autonomous multi-agent analysis.
- `/agent-trace agent_name` shows reasoning for `perception`, `decisions`, `ownership`, `ghost_code`, `bus_factor`, `scar_tissue`, or `onboarding`.
- `/onboarding junior|mid|senior [hours]` generates a learner-specific onboarding path.
- `/agent-feedback agent_id rating comment` records human feedback for agent adaptation.
- `/agent-status` reports health and summaries for all seven agents.

## Configuration

The skill reads `ARCHAEOLOGIST_API_URL`, defaulting to `http://localhost:8000`. The Telegram Gateway reads `TELEGRAM_BOT_TOKEN` from the environment. Do not store bot tokens directly in repository config.
