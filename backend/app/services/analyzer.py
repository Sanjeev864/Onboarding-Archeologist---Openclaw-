from __future__ import annotations

import shutil
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from git import Repo

from ..config import get_settings


DECISION_TERMS = (
    "because",
    "decided",
    "decision",
    "tradeoff",
    "migrate",
    "replace",
    "remove",
    "deprecate",
    "security",
    "performance",
    "refactor",
    "workaround",
    "fix",
)


@dataclass
class DecisionSignal:
    title: str
    summary: str
    evidence: str
    confidence: float
    commit_sha: str
    committed_at: datetime
    author: str


@dataclass
class OwnerSignal:
    path: str
    author: str
    commits: int
    risk: str


@dataclass
class GhostCodeSignal:
    path: str
    reason: str
    last_touched_days: int
    confidence: float


@dataclass
class AnalysisResult:
    default_branch: str
    decisions: list[DecisionSignal]
    ownership: list[OwnerSignal]
    ghost_code: list[GhostCodeSignal]


class RepositoryAnalyzer:
    def analyze(self, owner: str, repo_name: str, branch: str | None = None) -> AnalysisResult:
        tmp = Path(tempfile.mkdtemp(prefix="archaeologist-"))
        try:
            token = get_settings().github_token
            if token and token != "your_github_token_here":
                repo_url = f"https://{token}:x-oauth-basic@github.com/{owner}/{repo_name}.git"
            else:
                repo_url = f"https://github.com/{owner}/{repo_name}.git"
            clone_args = ["--depth", "200"]
            if branch:
                clone_args.extend(["--branch", branch])
            repo = Repo.clone_from(repo_url, tmp, multi_options=clone_args)
            commits = list(repo.iter_commits(branch or "HEAD", max_count=200))
            return AnalysisResult(
                default_branch=branch or repo.active_branch.name if not repo.head.is_detached else branch or "HEAD",
                decisions=self._decisions(commits),
                ownership=self._ownership(commits),
                ghost_code=self._ghost_code(repo, commits),
            )
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def _decisions(self, commits) -> list[DecisionSignal]:
        signals: list[DecisionSignal] = []
        for commit in commits:
            message = commit.message.strip().replace("\n\n", "\n")
            lower = message.lower()
            score = sum(1 for term in DECISION_TERMS if term in lower)
            if score == 0:
                continue
            first_line = message.splitlines()[0][:220]
            signals.append(
                DecisionSignal(
                    title=first_line,
                    summary=self._summarize_commit_message(message),
                    evidence=f"Commit {commit.hexsha[:10]} by {commit.author.name}: {first_line}",
                    confidence=min(0.95, 0.35 + (score * 0.12)),
                    commit_sha=commit.hexsha,
                    committed_at=datetime.fromtimestamp(commit.committed_date, tz=timezone.utc),
                    author=commit.author.name,
                )
            )
        return sorted(signals, key=lambda item: item.confidence, reverse=True)[:20]

    def _ownership(self, commits) -> list[OwnerSignal]:
        by_path: dict[str, Counter[str]] = defaultdict(Counter)
        for commit in commits:
            for path in commit.stats.files:
                if self._is_source_path(path):
                    by_path[self._bucket_path(path)][commit.author.name] += 1

        owners: list[OwnerSignal] = []
        for path, counts in by_path.items():
            author, count = counts.most_common(1)[0]
            total = sum(counts.values())
            concentration = count / total if total else 0
            risk = "high" if concentration >= 0.75 and total >= 4 else "medium" if concentration >= 0.55 else "low"
            owners.append(OwnerSignal(path=path, author=author, commits=count, risk=risk))
        return sorted(owners, key=lambda item: (item.risk == "high", item.commits), reverse=True)[:30]

    def _ghost_code(self, repo: Repo, commits) -> list[GhostCodeSignal]:
        latest_by_path: dict[str, int] = {}
        now = datetime.now(timezone.utc)
        for commit in commits:
            for path in commit.stats.files:
                if self._is_source_path(path) and path not in latest_by_path:
                    latest_by_path[path] = commit.committed_date

        findings: list[GhostCodeSignal] = []
        for path, timestamp in latest_by_path.items():
            full_path = Path(repo.working_tree_dir or "") / path
            if not full_path.exists() or full_path.stat().st_size > 250_000:
                continue
            days = (now - datetime.fromtimestamp(timestamp, tz=timezone.utc)).days
            text = full_path.read_text(errors="ignore")
            markers = sum(text.lower().count(term) for term in ("todo", "deprecated", "unused", "legacy", "dead code"))
            if days > 540 or markers > 0:
                reason = "Old source file with little recent churn"
                if markers:
                    reason = "Contains legacy/deprecated/unused markers"
                findings.append(
                    GhostCodeSignal(
                        path=path,
                        reason=reason,
                        last_touched_days=days,
                        confidence=min(0.9, 0.4 + markers * 0.1 + (0.25 if days > 540 else 0)),
                    )
                )
        return sorted(findings, key=lambda item: item.confidence, reverse=True)[:25]

    def _summarize_commit_message(self, message: str) -> str:
        lines = [line.strip() for line in message.splitlines() if line.strip()]
        if len(lines) == 1:
            return f"History suggests this change mattered because the commit explicitly says: {lines[0]}"
        return " ".join(lines[:3])[:600]

    def _bucket_path(self, path: str) -> str:
        parts = Path(path).parts
        if len(parts) <= 2:
            return path
        return str(Path(parts[0]) / parts[1])

    def _is_source_path(self, path: str) -> bool:
        ignored = ("node_modules/", "dist/", "build/", "vendor/", ".git/")
        return not path.startswith(ignored) and Path(path).suffix.lower() in {
            ".py",
            ".js",
            ".jsx",
            ".ts",
            ".tsx",
            ".go",
            ".rs",
            ".java",
            ".kt",
            ".cs",
            ".rb",
            ".php",
            ".c",
            ".cpp",
            ".h",
            ".hpp",
            ".css",
            ".scss",
        }
