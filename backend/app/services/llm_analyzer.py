from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

import httpx

from ..config import get_settings


class LLMAnalyzer:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.cache_dir = Path(self.settings.cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def extract_decision_signals(self, commits: list[dict[str, Any]]) -> list[dict[str, Any]]:
        prompt = {
            "task": "Rank architectural decision signals for developer onboarding.",
            "commits": commits[:80],
        }
        return self._cached_json("decision-signals", prompt, default=[])

    def analyze_code_patterns(self, repo_path: str, file_contents: dict[str, str]) -> list[dict[str, Any]]:
        prompt = {
            "task": "Identify defensive code, technology choices, and risky patterns.",
            "repo_path": repo_path,
            "files": file_contents,
        }
        return self._cached_json("code-patterns", prompt, default=[])

    def generate_knowledge_summary(self, path: str, commits: list[dict[str, Any]]) -> str:
        prompt = {"task": "Summarize why this area matters.", "path": path, "commits": commits[:40]}
        result = self._cached_json("knowledge-summary", prompt, default={"summary": ""})
        return result.get("summary", "") if isinstance(result, dict) else ""

    def rank_by_importance(self, signals: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return sorted(signals, key=lambda item: item.get("confidence", 0), reverse=True)

    def _cached_json(self, namespace: str, payload: dict[str, Any], default: Any) -> Any:
        key = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        cache_file = self.cache_dir / f"{namespace}-{key}.json"
        if cache_file.exists():
            return json.loads(cache_file.read_text())
        if not self.settings.enable_llm_analysis:
            return default
        try:
            result = self._provider_json(payload)
        except Exception:
            return default
        cache_file.write_text(json.dumps(result, indent=2))
        return result

    def _provider_json(self, payload: dict[str, Any]) -> Any:
        provider = self.settings.llm_provider.lower().strip()
        providers: dict[str, Callable[[dict[str, Any]], Any]] = {
            "ollama": self._ollama_json,
            "local": self._ollama_json,
            "anthropic": self._anthropic_json,
            "claude": self._anthropic_json,
        }
        if provider not in providers:
            raise ValueError(f"Unsupported LLM_PROVIDER: {self.settings.llm_provider}")
        return providers[provider](payload)

    def _ollama_json(self, payload: dict[str, Any]) -> Any:
        body = {
            "model": self.settings.llm_model,
            "stream": False,
            "format": "json",
            "prompt": (
                "You are the repository analysis enrichment model for Onboarding Archaeologist. "
                "Return only valid JSON with no markdown fences or commentary.\n\n"
                f"{json.dumps(payload, indent=2)}"
            ),
        }
        url = f"{self.settings.ollama_api_url.rstrip('/')}/api/generate"
        with httpx.Client(timeout=self.settings.analysis_timeout) as client:
            response = client.post(url, json=body)
            response.raise_for_status()
        return self._parse_json_text(response.json().get("response", ""))

    def _anthropic_json(self, payload: dict[str, Any]) -> Any:
        if not self.settings.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is required when LLM_PROVIDER=anthropic")
        headers = {
            "x-api-key": self.settings.anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        body = {
            "model": self.settings.anthropic_model,
            "max_tokens": 1200,
            "messages": [
                {
                    "role": "user",
                    "content": "Return only JSON for this codebase intelligence task:\n"
                    + json.dumps(payload, indent=2),
                }
            ],
        }
        with httpx.Client(timeout=self.settings.analysis_timeout) as client:
            response = client.post("https://api.anthropic.com/v1/messages", headers=headers, json=body)
            response.raise_for_status()
        text = response.json()["content"][0]["text"]
        return self._parse_json_text(text)

    def _parse_json_text(self, text: str) -> Any:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`").strip()
            if cleaned.startswith("json"):
                cleaned = cleaned[4:].strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            start = min((idx for idx in (cleaned.find("{"), cleaned.find("[")) if idx >= 0), default=-1)
            end = max(cleaned.rfind("}"), cleaned.rfind("]"))
            if start >= 0 and end > start:
                return json.loads(cleaned[start : end + 1])
            raise
