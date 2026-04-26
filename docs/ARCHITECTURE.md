# Architecture Guide

Onboarding Archaeologist is a local-first codebase intelligence platform built around a FastAPI analysis service, SQLite evidence store, and React dashboard.

## Intelligence Layers

1. Decision excavation mines commit history and optional LLM ranking.
2. Ghost code detection flags stale or legacy-marked files for review.
3. Scar tissue detection finds defensive code that may encode incident history.
4. Tribal knowledge extraction maps ownership concentration.
5. The Oracle answers questions with stored evidence.
6. Onboarding journeys turn findings into a five-day learning path.

## Data Flow

GitHub repositories are cloned shallowly, analyzed locally, persisted in SQLite, and returned to the UI through REST endpoints. Anthropic integration is optional and cached under `CACHE_DIR`.
