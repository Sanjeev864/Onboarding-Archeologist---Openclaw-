"""OpenClaw Telegram handlers for the Onboarding Archaeologist skill."""

from __future__ import annotations

import asyncio
import json
import os
import re
import time
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Iterable

import httpx


API_URL = os.getenv("ARCHAEOLOGIST_API_URL", "http://localhost:8000").rstrip("/")
MAX_TELEGRAM_MESSAGE = 4096
DEFAULT_TIMEOUT = httpx.Timeout(180.0, connect=10.0, read=180.0, write=30.0, pool=10.0)
VALID_AGENTS = {"perception", "decisions", "ownership", "ghost_code", "bus_factor", "scar_tissue", "onboarding"}
VALID_LEVELS = {"junior", "mid", "senior"}


class SkillError(RuntimeError):
    """User-facing skill error."""


@dataclass(frozen=True)
class CommandRequest:
    command: str
    args: list[str]
    chat_id: int | str | None = None
    user_id: int | str | None = None
    message_id: int | str | None = None
    context: dict[str, Any] | None = None


def normalize_agent_name(name: str) -> str:
    return name.strip().lower().replace("-", "_")


def infer_feedback_type(rating: float) -> str:
    if rating >= 0.7:
        return "positive"
    if rating <= 0.3:
        return "negative"
    return "partial"


def parse_repo(value: str) -> tuple[str, str]:
    cleaned = value.strip().removeprefix("https://github.com/").removesuffix(".git").strip("/")
    parts = cleaned.split("/")
    if len(parts) != 2 or not all(parts):
        raise SkillError("Use `owner/repo`, for example `/analyze-autonomous tiangolo/fastapi`.")
    return parts[0], parts[1]


def chunk_message(text: str, max_length: int = MAX_TELEGRAM_MESSAGE) -> list[str]:
    if not text:
        return [""]
    if len(text) <= max_length:
        return [text]
    chunks: list[str] = []
    current = ""
    for line in text.splitlines():
        candidate = f"{current}\n{line}" if current else line
        if len(candidate) <= max_length:
            current = candidate
            continue
        if current:
            chunks.append(current)
            current = ""
        while len(line) > max_length:
            split_at = line.rfind(" ", 0, max_length)
            if split_at < max_length // 2:
                split_at = max_length
            chunks.append(line[:split_at].rstrip())
            line = line[split_at:].lstrip()
        current = line
    if current:
        chunks.append(current)
    return chunks


async def _request(method: str, path: str, **kwargs: Any) -> dict[str, Any]:
    timeout = kwargs.pop("timeout", DEFAULT_TIMEOUT)
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.request(method, f"{API_URL}{path}", **kwargs)
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise SkillError("The analysis service took too long to respond. Try again, or check that the backend is healthy.") from exc
        except httpx.ConnectError as exc:
            raise SkillError(f"I could not reach the analysis backend at `{API_URL}`. Start FastAPI and try again.") from exc
        except httpx.HTTPStatusError as exc:
            detail = _extract_error_detail(exc.response)
            raise SkillError(f"The analysis backend returned {exc.response.status_code}: {detail}") from exc
        except httpx.HTTPError as exc:
            raise SkillError(f"The analysis backend request failed: {exc}") from exc
    try:
        payload = response.json()
    except json.JSONDecodeError as exc:
        raise SkillError("The analysis backend returned a non-JSON response.") from exc
    if isinstance(payload, dict) and payload.get("status") == "error":
        raise SkillError(str(payload.get("error") or "The backend reported an error."))
    return payload


def _extract_error_detail(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except json.JSONDecodeError:
        return response.text[:500] or response.reason_phrase
    if isinstance(payload, dict):
        return str(payload.get("detail") or payload.get("error") or payload)
    return str(payload)


async def analyze_repository(owner: str, repo: str, repo_path: str | None = None, use_cache: bool = True) -> dict[str, Any]:
    params: dict[str, Any] = {"owner": owner, "repo": repo, "use_cache": use_cache}
    if repo_path:
        params["repo_path"] = repo_path
    return await _request("POST", "/api/v2/analyze-autonomous", params=params)


async def get_agent_trace(agent_name: str) -> dict[str, Any]:
    agent = normalize_agent_name(agent_name)
    if agent not in VALID_AGENTS:
        raise SkillError(f"Unknown agent `{agent_name}`. Use one of: {', '.join(sorted(VALID_AGENTS))}.")
    return await _request("GET", f"/api/v2/agent-decision-trace/{agent}")


async def get_onboarding_path(repo_id: int, level: str = "junior", hours: int = 40) -> dict[str, Any]:
    level = level.lower()
    if level not in VALID_LEVELS:
        raise SkillError("Level must be `junior`, `mid`, or `senior`.")
    payload = await _request("POST", "/api/v2/onboarding-autonomous", params={"repo_id": repo_id, "level": level})
    payload["requested_hours"] = hours
    return payload


async def submit_feedback(
    agent_id: str,
    rating: float,
    feedback_text: str,
    feedback_type: str | None = None,
    execution_id: str | None = None,
) -> dict[str, Any]:
    agent = normalize_agent_name(agent_id)
    if agent not in VALID_AGENTS:
        raise SkillError(f"Unknown agent `{agent_id}`. Use one of: {', '.join(sorted(VALID_AGENTS))}.")
    if rating < 0 or rating > 1:
        raise SkillError("Rating must be between 0.0 and 1.0.")
    params = {
        "agent_id": agent,
        "execution_id": execution_id or f"openclaw-{int(time.time())}",
        "feedback_type": feedback_type or infer_feedback_type(rating),
        "feedback_text": feedback_text.strip() or "No comment provided.",
        "rating": rating,
    }
    return await _request("POST", "/api/v2/submit-agent-feedback", params=params)


async def get_agent_status() -> dict[str, Any]:
    return await _request("GET", "/api/v2/agent-status")


async def ask_oracle(repository_id: int, question: str) -> dict[str, Any]:
    return await _request("POST", "/api/openclaw/ask", json={"repository_id": repository_id, "question": question})


async def get_latest_repository() -> dict[str, Any]:
    return await _request("GET", "/api/openclaw/repositories/latest")


async def get_formatted_onboarding(repository_id: int, level: str) -> dict[str, Any]:
    return await _request("GET", f"/api/openclaw/repositories/{repository_id}/onboarding/{level}")


def format_analysis_result(payload: dict[str, Any]) -> str:
    repository = payload.get("repository", "repository")
    summaries = payload.get("agent_summaries") or {}
    results = payload.get("agent_results") or {}
    lines = [
        f"Analysis complete for `{repository}`.",
        "",
        f"Agents executed: {payload.get('agents_executed', len(results) or len(summaries))}",
        f"Mode: {payload.get('analysis_mode', 'autonomous')}",
    ]
    if summaries:
        lines.append("")
        lines.append("Agent summaries:")
        for name in sorted(summaries):
            summary = summaries[name]
            if isinstance(summary, dict):
                state = summary.get("state") or summary.get("status") or "ready"
                count = summary.get("execution_count") or summary.get("cycles_completed") or summary.get("runs")
                suffix = f" ({count} runs)" if count is not None else ""
                lines.append(f"- {name}: {state}{suffix}")
            else:
                lines.append(f"- {name}: {summary}")
    lines.append("")
    lines.append("Use `/agent-trace agent_name` to inspect one agent's reasoning.")
    return "\n".join(lines)


def format_trace_result(payload: dict[str, Any]) -> str:
    if payload.get("error"):
        return f"Could not fetch trace: {payload['error']}"
    agent_name = payload.get("agent_name") or payload.get("agent_id") or "agent"
    decision_trace = payload.get("decision_trace") or []
    execution_trace = payload.get("execution_trace") or []
    summary = payload.get("summary") or {}
    lines = [f"Trace for `{agent_name}`", ""]
    if summary:
        lines.append("Summary:")
        for key, value in list(summary.items())[:8]:
            lines.append(f"- {key}: {_compact(value)}")
        lines.append("")
    if decision_trace:
        lines.append("Recent decisions:")
        for item in decision_trace[-8:]:
            lines.append(f"- {_trace_line(item)}")
    else:
        lines.append("No decision trace is available yet. Run an analysis first.")
    if execution_trace:
        lines.append("")
        lines.append(f"Execution events recorded: {len(execution_trace)}")
    return "\n".join(lines)


def format_onboarding_result(payload: dict[str, Any]) -> str:
    if "text" in payload:
        return str(payload["text"])
    level = payload.get("learner_level", "junior")
    repo_id = payload.get("repository_id", "current")
    hours = payload.get("requested_hours", 40)
    path = payload.get("path_generated") or {}
    lines = [f"Onboarding path for repo `{repo_id}` ({level}, {hours}h requested)", ""]
    if isinstance(path, dict):
        for key, value in list(path.items())[:10]:
            lines.append(f"- {key}: {_compact(value)}")
    else:
        lines.append(_compact(path))
    if not path:
        lines.append("No onboarding steps were returned. Run repository analysis first, then try again.")
    return "\n".join(lines)


def format_feedback_result(payload: dict[str, Any]) -> str:
    if payload.get("status") == "success":
        return f"Feedback recorded for `{payload.get('agent_id', 'agent')}`. The adaptation signal was stored."
    return f"Feedback response: {_compact(payload)}"


def format_status_result(payload: dict[str, Any]) -> str:
    agents = payload.get("agents") or {}
    lines = [f"Agent system status: `{payload.get('status', 'unknown')}`", ""]
    for name in sorted(agents):
        summary = agents[name]
        if isinstance(summary, dict):
            state = summary.get("state") or summary.get("status") or "ready"
            count = summary.get("execution_count") or summary.get("cycles_completed") or summary.get("runs")
            suffix = f", runs: {count}" if count is not None else ""
            lines.append(f"- {name}: {state}{suffix}")
        else:
            lines.append(f"- {name}: {_compact(summary)}")
    if payload.get("timestamp"):
        lines.append("")
        lines.append(f"Timestamp: {payload['timestamp']}")
    return "\n".join(lines)


async def handle_analyze_autonomous(request: CommandRequest) -> list[str]:
    if not request.args:
        raise SkillError("Usage: `/analyze-autonomous owner/repo`")
    owner, repo = parse_repo(request.args[0])
    return chunk_message(format_analysis_result(await analyze_repository(owner, repo)))


async def handle_agent_trace(request: CommandRequest) -> list[str]:
    if not request.args:
        raise SkillError("Usage: `/agent-trace perception`")
    return chunk_message(format_trace_result(await get_agent_trace(request.args[0])))


async def handle_onboarding(request: CommandRequest) -> list[str]:
    level = request.args[0].lower() if request.args else "junior"
    if level not in VALID_LEVELS:
        raise SkillError("Usage: `/onboarding junior|mid|senior [hours]`")
    hours = 40
    if len(request.args) > 1:
        try:
            hours = int(request.args[1])
        except ValueError as exc:
            raise SkillError("Hours must be a number, for example `/onboarding senior 20`.") from exc
    repo_id = _repo_id_from_context(request.context)
    if repo_id is None:
        repo_id = int((await get_latest_repository())["repository_id"])
    try:
        text = format_onboarding_result(await get_formatted_onboarding(repo_id, level))
        if hours != 40:
            text = f"Requested timebox: {hours} hours.\n\n{text}"
    except SkillError:
        text = format_onboarding_result(await get_onboarding_path(repo_id, level, hours))
    return chunk_message(text)


async def handle_agent_feedback(request: CommandRequest) -> list[str]:
    if len(request.args) < 2:
        raise SkillError("Usage: `/agent-feedback agent_id rating comment`")
    try:
        rating = float(request.args[1])
    except ValueError as exc:
        raise SkillError("Rating must be a number between 0.0 and 1.0.") from exc
    comment = " ".join(request.args[2:]).strip() or "No comment provided."
    execution_id = str(request.message_id) if request.message_id is not None else None
    payload = await submit_feedback(request.args[0], rating, comment, execution_id=execution_id)
    return chunk_message(format_feedback_result(payload))


async def handle_agent_status(request: CommandRequest) -> list[str]:
    return chunk_message(format_status_result(await get_agent_status()))


async def handle_ask_oracle(request: CommandRequest) -> list[str]:
    if not request.args:
        raise SkillError("Ask a question after the command, for example `/ask What decisions matter most?`")
    repo_id = _repo_id_from_context(request.context)
    if repo_id is None:
        repo_id = int((await get_latest_repository())["repository_id"])
    payload = await ask_oracle(repo_id, " ".join(request.args))
    return chunk_message(str(payload.get("text") or _compact(payload)))


COMMAND_HANDLERS: dict[str, Callable[[CommandRequest], Awaitable[list[str]]]] = {
    "analyze-autonomous": handle_analyze_autonomous,
    "agent-trace": handle_agent_trace,
    "onboarding": handle_onboarding,
    "agent-feedback": handle_agent_feedback,
    "agent-status": handle_agent_status,
    "ask": handle_ask_oracle,
}


async def dispatch_command(command: str, args: Iterable[str], **metadata: Any) -> list[str]:
    normalized = command.lstrip("/").lower()
    handler = COMMAND_HANDLERS.get(normalized)
    if not handler:
        raise SkillError(f"Unknown command `/{normalized}`.")
    request = CommandRequest(command=normalized, args=list(args), **metadata)
    try:
        return await handler(request)
    except SkillError as exc:
        return chunk_message(f"Sorry, I could not complete that request.\n\n{exc}")


async def handle_telegram_update(update: Any, context: Any) -> None:
    message = getattr(update, "effective_message", None) or getattr(update, "message", None)
    if message is None or not getattr(message, "text", None):
        return
    command, args = _split_command(message.text)
    user = getattr(update, "effective_user", None)
    chat = getattr(update, "effective_chat", None)
    metadata = {
        "chat_id": getattr(chat, "id", None),
        "user_id": getattr(user, "id", None),
        "message_id": getattr(message, "message_id", None),
        "context": getattr(context, "user_data", None) or {},
    }
    for chunk in await dispatch_command(command, args, **metadata):
        await message.reply_text(chunk, parse_mode="Markdown")


def _split_command(text: str) -> tuple[str, list[str]]:
    tokens = text.strip().split()
    if not tokens:
        raise SkillError("No command provided.")
    return tokens[0].split("@", 1)[0], tokens[1:]


def _repo_id_from_context(context: dict[str, Any] | None) -> int | None:
    if not context:
        return None
    for key in ("repository_id", "repo_id", "current_repository_id"):
        value = context.get(key)
        if value is not None:
            try:
                return int(value)
            except (TypeError, ValueError):
                continue
    session = context.get("session")
    if isinstance(session, dict):
        return _repo_id_from_context(session)
    return None


def _trace_line(item: Any) -> str:
    if isinstance(item, dict):
        for key in ("thought", "decision", "action", "result", "message", "description"):
            if item.get(key):
                return _compact(item[key])
        return _compact(item)
    return _compact(item)


def _compact(value: Any, limit: int = 360) -> str:
    text = json.dumps(value, ensure_ascii=True, default=str) if isinstance(value, (dict, list)) else str(value)
    text = re.sub(r"\s+", " ", text).strip()
    return f"{text[: limit - 3]}..." if len(text) > limit else text


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Run an Onboarding Archaeologist OpenClaw command.")
    parser.add_argument("command")
    parser.add_argument("args", nargs="*")
    parsed = parser.parse_args()
    print("\n\n".join(asyncio.run(dispatch_command(parsed.command, parsed.args))))


if __name__ == "__main__":
    main()
