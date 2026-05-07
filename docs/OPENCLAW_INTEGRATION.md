# OpenClaw Integration

This project ships a ready-to-install OpenClaw skill at:

```text
openclaw/skills/archaeologist
```

The skill connects OpenClaw to the local Onboarding Archaeologist API and exposes:

- `/analyze-autonomous <owner>/<repo>`
- `/agent-trace <agent_name>`
- `/onboarding <junior|mid|senior> [hours]`
- `/agent-feedback <agent_id> <rating> <comment>`
- `/agent-status`
- `/ask <question>`

## What OpenClaw Means In This Project

OpenClaw is the command-and-automation layer around the Archaeologist backend.
The backend does the repository ingestion, analysis, evidence formatting, and
agent orchestration. The OpenClaw skill in this repository packages those
capabilities as commands that an OpenClaw gateway can expose through a channel
such as Telegram.

In other words:

- FastAPI is the analysis engine.
- `openclaw/skills/archaeologist` is the OpenClaw skill.
- Telegram is the chat surface when OpenClaw Gateway is configured with a Telegram bot.

## What Was Implemented

- OpenClaw-ready `skill.yaml`, `system_prompt.md`, `handlers.py`, and `SKILL.md`
- PowerShell and bash helper scripts
- OpenClaw API formatter endpoints under `/api/openclaw/*`
- Local install scripts
- Gateway config in `openclaw/openclaw.config.yaml`

## Install The Skill

PowerShell:

```powershell
.\scripts\install-openclaw-skill.ps1
```

Bash:

```bash
./scripts/install-openclaw-skill.sh
```

This copies the skill into `~/.openclaw/skills/archaeologist`.

## Enable The Skill

If OpenClaw does not auto-load local skills, add this to `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "archaeologist": {
        "enabled": true,
        "env": {
          "ARCHAEOLOGIST_API_URL": "http://localhost:8000"
        }
      }
    }
  }
}
```

## Start Services

```bash
docker-compose up -d backend
openclaw gateway
```

Then send a command to your OpenClaw channel:

```text
/analyze-autonomous anthropics/claude-code
```

## Telegram Automation

OpenClaw does not become Telegram automatically just because a skill exists.
You need a Telegram bot token and an OpenClaw gateway config that loads this
skill and binds the Telegram channel.

1. Create a bot with BotFather and copy its token.
2. Install the skill with `.\scripts\install-openclaw-skill.ps1`.
3. Copy `openclaw/openclaw.example.json` to your OpenClaw config location.
4. Set `TELEGRAM_BOT_TOKEN` in your environment or secret manager.
5. Start the app API, then run `openclaw gateway`.

Recommended BotFather command list:

```text
analyze - Analyze a GitHub repository
analyze_autonomous - Run autonomous multi-agent analysis
ask - Ask a question about the latest analyzed repository
bus_factor - Show bus factor risks
decisions - Show architectural decisions
ghost_code - Show stale or risky cleanup candidates
onboarding - Generate an onboarding path
agent_status - Show autonomous agent health
agent_trace - Show one agent's reasoning trace
```

## Direct API Smoke Test

```powershell
Invoke-RestMethod -Uri http://localhost:8000/api/openclaw/analyze `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"owner":"octocat","repo":"Hello-World","branch":""}'
```

Autonomous-agent endpoint smoke test:

```bash
curl -X POST "http://localhost:8000/api/v2/analyze-autonomous?owner=octocat&repo=Hello-World"
curl http://localhost:8000/api/v2/agent-status
```

The OpenClaw handlers call the `/api/v2/*` autonomous endpoints for agent
analysis, traces, onboarding, feedback, and status. They use `/api/openclaw/*`
where the backend already provides Telegram-ready formatted text.

## Notes

- Public repositories work without `GITHUB_TOKEN`.
- Private repositories require `GITHUB_TOKEN` in `.env`.
- LLM enrichment is free/local by default: set `ENABLE_LLM_ANALYSIS=true`, `LLM_PROVIDER=ollama`, and run Ollama with the configured `LLM_MODEL`.
- `ANTHROPIC_API_KEY` is optional and only used when `LLM_PROVIDER=anthropic`.
- Ghost-code output is intentionally phrased as cleanup review guidance, not deletion approval.
