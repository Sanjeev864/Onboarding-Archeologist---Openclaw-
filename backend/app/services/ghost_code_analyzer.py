from __future__ import annotations

from git import Repo

from .analyzer import GhostCodeSignal, RepositoryAnalyzer
from .llm_analyzer import LLMAnalyzer


class GhostCodeAnalyzer:
    def __init__(self, llm_analyzer: LLMAnalyzer | None = None) -> None:
        self.llm = llm_analyzer or LLMAnalyzer()
        self.base = RepositoryAnalyzer()

    def find_ghost_code(self, repo: Repo, commits) -> list[GhostCodeSignal]:
        return self.base._ghost_code(repo, commits)

    def find_hidden_references(self, repo: Repo, file_path: str) -> list[str]:
        root = repo.working_tree_dir
        if not root:
            return []
        needle = file_path.rsplit("/", 1)[-1]
        matches: list[str] = []
        for path in repo.git.ls_files().splitlines():
            if path == file_path:
                continue
            full = f"{root}/{path}"
            try:
                if needle in open(full, encoding="utf-8", errors="ignore").read():
                    matches.append(path)
            except OSError:
                continue
        return matches[:25]
