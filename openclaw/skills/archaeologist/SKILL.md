---
name: "Code Archaeologist"
description: >
  Excavates git history to reveal architectural decisions, knowledge ownership,
  ghost code, scar tissue patterns, onboarding paths, and bus-factor risks.
  Use when a developer asks why code exists, who owns an area, what is safe to
  review for cleanup, or how to onboard into a repository.
version: "1.0.0"
author: "Onboarding Archaeologist Project"
tools:
  - exec
  - browser
  - fetch
tags:
  - codebase-intelligence
  - git-history
  - architecture
  - developer-onboarding
  - risk-assessment
skill-invocation: true
disable-model-invocation: false
---

# Code Archaeologist

## Purpose

Code Archaeologist connects OpenClaw to the local Onboarding Archaeologist API.
It analyzes GitHub repositories and returns evidence-backed findings for
developer onboarding, architectural review, bus-factor planning, and cleanup
triage.

## Analyzer Dependency

The local analyzer must be running before commands are used:

```bash
docker-compose up -d backend
curl http://localhost:8000/health
```

The API base URL defaults to `http://localhost:8000`. Override it by setting
`ARCHAEOLOGIST_API_URL`.

## Commands

### `/analyze <owner>/<repo>`

Run full analysis.

Implementation:

```bash
scripts/analyze.sh owner repo
```

Windows:

```powershell
scripts/analyze.cmd owner repo
```

Present the returned `text` field to the user. Keep the returned
`repository_id` as conversation context for follow-up commands.

### `/ask <question>`

Ask about the last analyzed repository. If no repository ID is known, call
`scripts/latest.ps1` or `scripts/latest.sh` first.

Implementation:

```bash
scripts/oracle.sh <repository_id> "question"
```

Windows:

```powershell
scripts/oracle.cmd <repository_id> "question"
```

### `/bus-factor`

Show knowledge concentration risks.

```powershell
scripts/bus-factor.cmd <repository_id>
```

### `/decisions`

Show architectural decisions only.

```powershell
scripts/decisions.cmd <repository_id>
```

### `/ghost-code`

Show stale or legacy-marked code candidates. These are review candidates, not
automatic deletion recommendations.

```powershell
scripts/ghost-code.cmd <repository_id>
```

### `/onboarding <junior|mid|senior>`

Create a five-day onboarding path from the stored analysis.

```powershell
scripts/onboarding.cmd <repository_id> junior
```

## Response Rules

- Always cite the evidence returned by the analyzer.
- Never claim ghost code is safe to delete without human review.
- Treat bus-factor alerts as risk signals, not personnel judgments.
- If the analyzer is unavailable, tell the user to start the backend.
- If a private repository fails, ask the user to configure `GITHUB_TOKEN`.

## Good Examples

- `/analyze anthropics/claude-code`
- `/ask "What security decisions show up in this repository?"`
- `/bus-factor`
- `/ghost-code`
- `/onboarding junior`

## API Reference

See `resources/API_REFERENCE.md`.
