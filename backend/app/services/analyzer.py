from __future__ import annotations

import json
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
class ScarTissueSignal:
    pattern_type: str
    file_path: str
    line_numbers: list[int]
    incident_summary: str
    severity: str
    confidence: float
    explanation: str


@dataclass
class BusFactorSignal:
    critical_person: str
    areas_affected: list[str]
    concentration_percentage: float
    risk_level: str
    recommendation: str


@dataclass
class OnboardingDaySignal:
    day_number: int
    focus_area: str
    key_concepts: list[str]
    code_locations: list[str]
    estimated_hours: float
    learning_resources: list[str]


@dataclass
class AnalysisResult:
    default_branch: str
    decisions: list[DecisionSignal]
    ownership: list[OwnerSignal]
    ghost_code: list[GhostCodeSignal]
    scar_tissue: list[ScarTissueSignal]
    bus_factor_alerts: list[BusFactorSignal]
    onboarding_paths: list[OnboardingDaySignal]
    total_commits_analyzed: int
    coverage_percentage: float


class RepositoryAnalyzer:
    def analyze(self, owner: str, repo_name: str, branch: str | None = None) -> AnalysisResult:
        tmp = Path(tempfile.mkdtemp(prefix="archaeologist-"))
        try:
            token = get_settings().github_token
            if token and token != "your_github_token_here":
                repo_url = f"https://{token}:x-oauth-basic@github.com/{owner}/{repo_name}.git"
            else:
                repo_url = f"https://github.com/{owner}/{repo_name}.git"
            clone_args = ["--single-branch"]
            if branch:
                clone_args.extend(["--branch", branch])
            repo = Repo.clone_from(repo_url, tmp, multi_options=clone_args)
            max_count = min(get_settings().max_commit_depth, 500)
            commits = list(repo.iter_commits(branch or "HEAD", max_count=max_count))
            ownership = self._ownership(commits)
            scar_tissue = self._scar_tissue_detection(repo, commits)
            return AnalysisResult(
                default_branch=branch or repo.active_branch.name if not repo.head.is_detached else branch or "HEAD",
                decisions=self._decisions(commits),
                ownership=ownership,
                ghost_code=self._ghost_code(repo, commits),
                scar_tissue=scar_tissue,
                bus_factor_alerts=self._bus_factor_alerts(ownership),
                onboarding_paths=self._onboarding_path(ownership, scar_tissue),
                total_commits_analyzed=len(commits),
                coverage_percentage=100.0 if commits else 0.0,
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

    def _scar_tissue_detection(self, repo: Repo, commits) -> list[ScarTissueSignal]:
        incidents = self._incident_correlation([commit.message for commit in commits])
        findings: list[ScarTissueSignal] = []
        root = Path(repo.working_tree_dir or "")
        for path in root.rglob("*"):
            if not path.is_file() or not self._is_source_path(str(path.relative_to(root)).replace("\\", "/")):
                continue
            if path.stat().st_size > 250_000:
                continue
            relative = str(path.relative_to(root)).replace("\\", "/")
            lines = path.read_text(errors="ignore").splitlines()
            for idx, line in enumerate(lines, start=1):
                lower = line.lower()
                pattern = None
                if "retry" in lower or "backoff" in lower:
                    pattern = "retry_loop"
                elif "fallback" in lower or "failover" in lower:
                    pattern = "fallback"
                elif "except" in lower or "catch" in lower:
                    pattern = "defensive_check"
                elif "validate" in lower and ("if " in lower or "throw" in lower or "raise" in lower):
                    pattern = "defensive_check"
                if not pattern:
                    continue
                incident = incidents.get(pattern, "No directly linked incident found; pattern inferred from defensive source code.")
                severity = "high" if pattern in {"retry_loop", "fallback"} else "medium"
                findings.append(
                    ScarTissueSignal(
                        pattern_type=pattern,
                        file_path=relative,
                        line_numbers=[idx],
                        incident_summary=incident,
                        severity=severity,
                        confidence=0.72 if incident.startswith("Related") else 0.55,
                        explanation=f"{pattern.replace('_', ' ').title()} detected in source; review history before simplifying.",
                    )
                )
        return sorted(findings, key=lambda item: item.confidence, reverse=True)[:25]

    def _incident_correlation(self, commit_messages: list[str]) -> dict[str, str]:
        incident_terms = ("incident", "outage", "crash", "hotfix", "bug", "regression", "timeout", "flaky")
        incidents: dict[str, str] = {}
        for message in commit_messages:
            first_line = message.strip().splitlines()[0][:220] if message.strip() else ""
            lower = first_line.lower()
            if not any(term in lower for term in incident_terms):
                continue
            key = "retry_loop" if any(term in lower for term in ("timeout", "flaky")) else "defensive_check"
            incidents.setdefault(key, f"Related incident-like commit: {first_line}")
        return incidents

    def _bus_factor_alerts(self, ownership: list[OwnerSignal]) -> list[BusFactorSignal]:
        by_person: dict[str, list[OwnerSignal]] = defaultdict(list)
        for owner in ownership:
            if owner.risk in {"high", "medium"}:
                by_person[owner.author].append(owner)

        alerts: list[BusFactorSignal] = []
        for person, areas in by_person.items():
            high_count = sum(1 for area in areas if area.risk == "high")
            concentration = min(1.0, sum(area.commits for area in areas) / max(1, sum(item.commits for item in ownership)))
            risk = "critical" if high_count >= 2 else "high" if high_count == 1 else "medium"
            alerts.append(
                BusFactorSignal(
                    critical_person=person,
                    areas_affected=[area.path for area in areas[:8]],
                    concentration_percentage=round(concentration * 100, 1),
                    risk_level=risk,
                    recommendation="Pair on these areas and capture rationale in docs or review notes.",
                )
            )
        return sorted(alerts, key=lambda item: (item.risk_level == "critical", item.concentration_percentage), reverse=True)[:10]

    def _onboarding_path(self, ownership: list[OwnerSignal], scar_tissue: list[ScarTissueSignal]) -> list[OnboardingDaySignal]:
        critical_paths = [item.path for item in ownership[:5]]
        scar_paths = [item.file_path for item in scar_tissue[:5]]
        return [
            OnboardingDaySignal(1, "Architecture overview", ["Repository layout", "Primary components"], critical_paths[:3], 3.0, critical_paths[:3]),
            OnboardingDaySignal(2, "Critical paths", ["Frequently changed modules", "Integration points"], critical_paths, 4.0, critical_paths),
            OnboardingDaySignal(3, "Knowledge ownership", ["Bus factor", "Primary maintainers"], critical_paths, 2.5, [item.author for item in ownership[:5]]),
            OnboardingDaySignal(4, "Defensive patterns", ["Reliability history", "Scar tissue"], scar_paths, 3.0, scar_paths),
            OnboardingDaySignal(5, "First contribution", ["Tests", "Small reviewable change"], critical_paths[:2], 4.0, critical_paths[:2]),
        ]

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


def scar_to_model(signal: ScarTissueSignal) -> dict:
    return {
        "pattern_type": signal.pattern_type,
        "file_path": signal.file_path,
        "line_numbers": json.dumps(signal.line_numbers),
        "incident_date": datetime.now(timezone.utc),
        "related_incident": signal.incident_summary,
        "severity": signal.severity,
        "confidence": signal.confidence,
    }
