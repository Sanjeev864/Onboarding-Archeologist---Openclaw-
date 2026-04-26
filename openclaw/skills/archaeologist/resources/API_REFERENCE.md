# Archaeologist OpenClaw API Reference

Default base URL: `http://localhost:8000`

Set `ARCHAEOLOGIST_API_URL` to override it.

## POST `/api/openclaw/analyze`

Request:

```json
{
  "owner": "anthropics",
  "repo": "claude-code",
  "branch": ""
}
```

Response:

```json
{
  "repository_id": 1,
  "text": "Analysis complete..."
}
```

## POST `/api/openclaw/ask`

Request:

```json
{
  "repository_id": 1,
  "question": "What are the main security decisions?"
}
```

Response:

```json
{
  "text": "Oracle Answer..."
}
```

## GET `/api/openclaw/repositories/latest`

Returns the most recently analyzed repository.

## GET `/api/openclaw/repositories/{repository_id}/decisions`

Returns formatted architectural decisions.

## GET `/api/openclaw/repositories/{repository_id}/bus-factor`

Returns formatted bus-factor analysis.

## GET `/api/openclaw/repositories/{repository_id}/ghost-code`

Returns formatted ghost-code candidates.

## GET `/api/openclaw/repositories/{repository_id}/onboarding/{level}`

Returns formatted onboarding path.
