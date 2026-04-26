from __future__ import annotations

from .analyzer import DecisionSignal
from .llm_analyzer import LLMAnalyzer


class DecisionExcavationEngine:
    def __init__(self, llm_analyzer: LLMAnalyzer | None = None) -> None:
        self.llm = llm_analyzer or LLMAnalyzer()

    def excavate_decisions(self, owner: str, repo: str, commits: list) -> list[DecisionSignal]:
        del owner, repo
        candidates = []
        for commit in commits:
            message = commit.message.strip()
            if not message:
                continue
            candidates.append(
                {
                    "sha": commit.hexsha,
                    "message": message[:1000],
                    "author": commit.author.name,
                    "date": commit.committed_datetime.isoformat(),
                }
            )
        self.llm.extract_decision_signals(candidates)
        return []
