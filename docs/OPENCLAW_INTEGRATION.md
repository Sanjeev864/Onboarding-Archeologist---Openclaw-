# OpenClaw Integration Guide

## Onboarding Archaeologist × OpenClaw Gateway

This guide covers installing the Onboarding Archaeologist skill into OpenClaw, running it via Telegram, and verifying the full integration end-to-end.

---

## Overview

The integration works in three layers:

```
Telegram User
    ↓  sends command
OpenClaw Gateway   (reads openclaw.config.yaml)
    ↓  routes command
OpenClaw Skill     (openclaw/skills/archaeologist/)
    ↓  calls backend
FastAPI Backend    (localhost:8000 or Render/Railway)
    ↓  runs agents
7 Autonomous Agents
```

---

## Prerequisites

- Python 3.10 or later
- Node.js 18+ (for frontend, optional)
- Docker and Docker Compose (recommended)
- A Telegram bot token from [@BotFather](https://t.me/BotFather)
- OpenClaw Gateway installed (`pip install openclaw` or from [openclaw.dev](https://openclaw.dev))
- A GitHub personal access token (optional, needed for private repos)

---

## Environment Variables

Copy `.env.example` to `.env` and fill in:

```bash
cp .env.example .env
```

Required:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
```

Optional but recommended:

```env
GITHUB_TOKEN=your_github_pat_here
ARCHAEOLOGIST_API_URL=http://localhost:8000
OPENCLAW_TELEGRAM_WEBHOOK_URL=https://your-render-url.onrender.com/webhook/telegram
```

---

## Step 1: Start the Backend

### Option A: Docker (Recommended)

```bash
docker-compose up -d --build
```

This starts:
- FastAPI backend at `http://localhost:8000`
- React frontend at `http://localhost:3000`

Verify:
```bash
curl http://localhost:8000/health
# Expected: {"status":"ok","time":"..."}
```

### Option B: Manual

```bash
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Step 2: Install the OpenClaw Skill

### Linux / macOS

```bash
chmod +x scripts/install-openclaw-skill.sh
./scripts/install-openclaw-skill.sh
```

Or with a custom backend URL:
```bash
./scripts/install-openclaw-skill.sh http://localhost:8000
```

### Windows (PowerShell)

```powershell
.\scripts\install-openclaw-skill.ps1
```

Or with a custom backend URL:
```powershell
.\scripts\install-openclaw-skill.ps1 -ApiUrl "http://localhost:8000"
```

Both scripts:
1. Create `~/.openclaw/skills/archaeologist/`
2. Copy `skill.yaml`, `handlers.py`, and `system_prompt.md`
3. Verify the backend is reachable
4. Print next steps

---

## Step 3: Start OpenClaw Gateway

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export ARCHAEOLOGIST_API_URL="http://localhost:8000"

openclaw run --config openclaw.config.yaml
```

You should see:
```
✓ Skill loaded: archaeologist (6 tools)
✓ Telegram channel connected (polling mode)
✓ OpenClaw Gateway running
```

---

## Step 4: Smoke Tests via Telegram

Open Telegram, find your bot, and send these commands in order:

### Test 1 — Agent Status (fastest check)
```
/agent-status
```
Expected: List of all 7 agents with state and execution counts.

### Test 2 — Analyze a Repository
```
/analyze-autonomous torvalds/linux
```
Expected: Analysis summary with agent results and decision traces.
This may take 30–120 seconds depending on repo size.

### Test 3 — View Agent Reasoning
```
/agent-trace bus_factor
```
Expected: Decision trace showing how the bus factor agent reasoned.

### Test 4 — Onboarding Path
```
/onboarding junior 40
```
Expected: Personalized 5-day learning path for a junior engineer.

### Test 5 — Submit Feedback
```
/agent-feedback ghost_code 0.9 Great findings on stale files
```
Expected: Confirmation that feedback was recorded and agent adapted.

---

## Step 5: Backend API Smoke Tests (Optional)

Run these directly to verify each endpoint works before using Telegram:

```bash
# Health check
curl http://localhost:8000/health

# Agent status
curl http://localhost:8000/api/v2/agent-status

# Analyze a small public repo (takes ~30s)
curl -X POST "http://localhost:8000/api/v2/analyze-autonomous?owner=tiangolo&repo=fastapi"

# Decision trace after analysis
curl http://localhost:8000/api/v2/agent-decision-trace/perception

# Latest analyzed repo
curl http://localhost:8000/api/openclaw/repositories/latest

# Onboarding path (replace 1 with actual repo_id from above)
curl -X POST "http://localhost:8000/api/v2/onboarding-autonomous?repo_id=1&level=junior"

# Submit feedback
curl -X POST "http://localhost:8000/api/v2/submit-agent-feedback?agent_id=ghost_code&execution_id=test-001&feedback_type=positive&feedback_text=Good+analysis&rating=0.9"
```

---

## Available Commands

| Command | Usage | What it does |
|---------|-------|--------------|
| `/analyze-autonomous` | `/analyze-autonomous owner/repo` | Runs all 6 agents on the repository |
| `/agent-trace` | `/agent-trace agent_name` | Shows reasoning trace for one agent |
| `/onboarding` | `/onboarding junior\|mid\|senior [hours]` | Generates a personalized onboarding plan |
| `/agent-feedback` | `/agent-feedback agent_id rating comment` | Sends feedback to train an agent |
| `/agent-status` | `/agent-status` | Shows system health for all 7 agents |

Valid agent names: `perception`, `decisions`, `ownership`, `ghost_code`, `bus_factor`, `scar_tissue`, `onboarding`

---

## Deployment to Render / Railway

### Backend on Render

1. Connect your GitHub repo to Render
2. Create a new **Web Service**
3. Set build command: `pip install -r backend/requirements.txt`
4. Set start command: `uvicorn backend.app.main:app --host 0.0.0.0 --port 10000`
5. Add environment variables:
   - `TELEGRAM_BOT_TOKEN`
   - `GITHUB_TOKEN`
   - `DATABASE_URL=sqlite:///./data/archaeologist.db`
6. After deploy, set `ARCHAEOLOGIST_API_URL` to your Render URL

### OpenClaw in Webhook Mode

Once the backend is deployed, switch from polling to webhook in `openclaw.config.yaml`:

```yaml
channels:
  telegram:
    mode: webhook
    webhook:
      enabled: true
      url: https://your-app.onrender.com/webhook/telegram
```

Register the webhook:
```bash
curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" \
  -d '{"url":"https://your-app.onrender.com/webhook/telegram"}'
```

---

## Troubleshooting

### "I could not reach the analysis backend"
- Check FastAPI is running: `curl http://localhost:8000/health`
- Check `ARCHAEOLOGIST_API_URL` matches the actual backend URL
- Check Docker containers are up: `docker-compose ps`

### "No repository found" on `/onboarding` or `/agent-trace`
- Run `/analyze-autonomous owner/repo` first
- Analysis must complete before trace or onboarding commands work

### Telegram bot not responding
- Verify `TELEGRAM_BOT_TOKEN` is correct
- Check OpenClaw Gateway is running
- Only one process can poll Telegram at a time — stop any other bots using the same token

### Analysis takes too long / times out
- Large repos (e.g. linux kernel) take 2–3 minutes
- Handlers use a 180s timeout by default
- For Render free tier, backend may cold-start; send `/agent-status` first to wake it up

### "Agent not found" error
- Use underscore format: `ghost_code` not `ghost-code`
- The handlers normalize hyphens to underscores automatically

---

## File Reference

```
openclaw/
├── skills/
│   └── archaeologist/
│       ├── SKILL.md            # Human-readable skill overview
│       ├── skill.yaml          # Machine-readable tool definitions
│       ├── handlers.py         # Python command handlers
│       └── system_prompt.md    # LLM routing instructions
├── openclaw.config.yaml        # Gateway configuration
└── openclaw.example.json       # Minimal example config

scripts/
├── install-openclaw-skill.sh   # Linux/macOS installer
└── install-openclaw-skill.ps1  # Windows installer
```

---

## Support

- Backend API docs: `http://localhost:8000/docs`
- OpenClaw docs: https://openclaw.dev/docs
- Telegram bot API: https://core.telegram.org/bots/api
