# OpenClaw Integration

This project ships a ready-to-install OpenClaw skill at:

```text
openclaw/skills/archaeologist
```

The skill connects OpenClaw to the local Onboarding Archaeologist API and exposes:

- `/analyze <owner>/<repo>`
- `/ask <question>`
- `/bus-factor`
- `/decisions`
- `/ghost-code`
- `/onboarding <junior|mid|senior>`

## What Was Implemented

- OpenClaw-ready `SKILL.md`
- PowerShell and bash helper scripts
- OpenClaw API formatter endpoints under `/api/openclaw/*`
- Local install scripts
- Skill API reference

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
/analyze anthropics/claude-code
```

## Direct API Smoke Test

```powershell
Invoke-RestMethod -Uri http://localhost:8000/api/openclaw/analyze `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"owner":"octocat","repo":"Hello-World","branch":""}'
```

## Windows Script Wrappers

Windows may block direct `.ps1` execution. Use the `.cmd` wrappers from the
skill scripts directory instead:

```cmd
openclaw\skills\archaeologist\scripts\oracle.cmd 3 "What security decisions are important?"
```

## Notes

- Public repositories work without `GITHUB_TOKEN`.
- Private repositories require `GITHUB_TOKEN` in `.env`.
- `ANTHROPIC_API_KEY` is optional for the current local analyzer; when set with `ENABLE_LLM_ANALYSIS=true`, LLM enrichment can use the configured Anthropic API.
- Ghost-code output is intentionally phrased as cleanup review guidance, not deletion approval.
