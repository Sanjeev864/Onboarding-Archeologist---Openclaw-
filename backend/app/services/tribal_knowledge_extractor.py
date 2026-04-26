from __future__ import annotations

from .analyzer import BusFactorSignal, OwnerSignal, RepositoryAnalyzer


class TribalKnowledgeExtractor:
    def __init__(self) -> None:
        self.base = RepositoryAnalyzer()

    def extract_knowledge_map(self, commits) -> tuple[list[OwnerSignal], list[BusFactorSignal]]:
        owners = self.base._ownership(commits)
        return owners, self.base._bus_factor_alerts(owners)
