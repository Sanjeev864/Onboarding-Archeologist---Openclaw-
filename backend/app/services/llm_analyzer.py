from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

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
        if not self.settings.enable_llm_analysis or not self.settings.anthropic_api_key:
            return default
        try:
            result = self._anthropic_json(payload)
        except Exception:
            return default
        cache_file.write_text(json.dumps(result, indent=2))
        return result

    def _anthropic_json(self, payload: dict[str, Any]) -> Any:
        headers = {
            "x-api-key": self.settings.anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        body = {
            "model": "claude-3-haiku-20240307",
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
        return json.loads(text)
