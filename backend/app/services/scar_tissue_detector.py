from __future__ import annotations

from git import Repo

from .analyzer import RepositoryAnalyzer, ScarTissueSignal
from .llm_analyzer import LLMAnalyzer


class ScarTissueDetector:
    def __init__(self, llm_analyzer: LLMAnalyzer | None = None) -> None:
        self.llm = llm_analyzer or LLMAnalyzer()
        self.base = RepositoryAnalyzer()

    def detect_scar_tissue(self, repo: Repo, commits) -> list[ScarTissueSignal]:
        return self.base._scar_tissue_detection(repo, commits)
