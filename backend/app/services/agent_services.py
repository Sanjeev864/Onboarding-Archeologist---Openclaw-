"""
agent_services.py - Integration layer between agents and existing services.

These wrappers let the autonomous agents call the real project services while
still falling back to deterministic demo data when an integration is unavailable.
"""

from __future__ import annotations

import logging
from dataclasses import asdict, is_dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AnalyzerServiceWrapper:
    """Wraps the repository analyzer for agent use."""

    def __init__(self) -> None:
        try:
            from .analyzer import RepositoryAnalyzer

            self.analyzer = RepositoryAnalyzer()
            self.available = True
        except ImportError:
            logger.warning("RepositoryAnalyzer not available, using mock")
            self.available = False

    async def analyze_repository(
        self,
        owner: str,
        repo: str,
        path: Optional[str] = None,
        deep: bool = True,
    ) -> Dict[str, Any]:
        """Analyze a GitHub repository and return structured data for agents."""
        if not self.available:
            return self._mock_analysis(owner, repo)

        try:
            analysis = self.analyzer.analyze(owner=owner, repo_name=repo, branch=path)
            logger.info("Real analysis completed: %s/%s", owner, repo)
            return self._json_safe(self._analysis_to_dict(owner, repo, analysis))
        except Exception as exc:
            logger.error("Analysis failed: %s, using mock data", exc)
            return self._mock_analysis(owner, repo)

    async def extract_decisions(self, code_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract architectural decisions from prior analysis output."""
        decisions = code_data.get("decisions", [])
        logger.info("Extracted %s decisions", len(decisions))
        return decisions or self._mock_decisions()

    async def analyze_ownership(self, code_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze code ownership and concentration from prior analysis output."""
        ownership = code_data.get("ownership", [])
        logger.info("Analyzed ownership patterns")
        return ownership or self._mock_ownership()

    async def detect_ghost_code(self, code_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect unused or stale code from prior analysis output."""
        ghost_code = code_data.get("ghost_code", [])
        logger.info("Detected %s ghost code candidates", len(ghost_code))
        return ghost_code or self._mock_ghost_code()

    async def evaluate_bus_factor(self, code_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evaluate bus factor and single points of failure."""
        alerts = code_data.get("bus_factor_alerts", []) if isinstance(code_data, dict) else []
        logger.info("Evaluated bus factor: %s alerts", len(alerts))
        return alerts or self._mock_bus_factor()

    @staticmethod
    def _analysis_to_dict(owner: str, repo: str, analysis: Any) -> Dict[str, Any]:
        if is_dataclass(analysis):
            data = asdict(analysis)
        elif isinstance(analysis, dict):
            data = dict(analysis)
        else:
            data = dict(getattr(analysis, "__dict__", {}))

        data.setdefault("owner", owner)
        data.setdefault("repo", repo)
        data.setdefault("timestamp", datetime.now().isoformat())
        data.setdefault(
            "metadata",
            {
                "mode": "real",
                "default_branch": data.get("default_branch"),
                "total_commits_analyzed": data.get("total_commits_analyzed", 0),
                "coverage_percentage": data.get("coverage_percentage", 0.0),
            },
        )
        return data

    @classmethod
    def _json_safe(cls, value: Any) -> Any:
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, dict):
            return {key: cls._json_safe(item) for key, item in value.items()}
        if isinstance(value, list):
            return [cls._json_safe(item) for item in value]
        return value

    @staticmethod
    def _mock_analysis(owner: str, repo: str) -> Dict[str, Any]:
        return {
            "owner": owner,
            "repo": repo,
            "timestamp": datetime.now().isoformat(),
            "decisions": [],
            "ownership": [],
            "ghost_code": [],
            "bus_factor_alerts": [],
            "scar_tissue": [],
            "metadata": {"mode": "mock", "note": "Real analyzer not available"},
        }

    @staticmethod
    def _mock_decisions() -> List[Dict[str, Any]]:
        return [
            {
                "type": "architecture",
                "description": "Move to microservices",
                "confidence": 0.85,
                "date": "2024-06-15",
            }
        ]

    @staticmethod
    def _mock_ownership() -> List[Dict[str, Any]]:
        return [
            {
                "path": "src/core",
                "owner": "alice",
                "concentration_percentage": 65,
                "risk": "high",
                "commit_count": 234,
            }
        ]

    @staticmethod
    def _mock_ghost_code() -> List[Dict[str, Any]]:
        return [
            {
                "file": "src/legacy/old_module.py",
                "type": "unused_import",
                "last_touched_days": 390,
                "confidence": 0.92,
            }
        ]

    @staticmethod
    def _mock_bus_factor() -> List[Dict[str, Any]]:
        return [
            {
                "area": "Authentication System",
                "owner": "bob",
                "concentration_percentage": 87,
                "risk_level": "CRITICAL",
            }
        ]


class OracleServiceWrapper:
    """Wraps oracle.py for knowledge queries."""

    def __init__(self) -> None:
        try:
            from .oracle import Oracle

            self.oracle = Oracle()
            self.available = True
        except ImportError:
            logger.warning("Oracle not available, using mock")
            self.available = False

    async def query_knowledge(self, question: str) -> str:
        """Query oracle for contextual knowledge."""
        if not self.available:
            return f"[Mock Response] Context for: {question}"

        try:
            if hasattr(self.oracle, "query"):
                response = self.oracle.query(question)
            else:
                response = "Oracle queries require a repository id through the REST API. Run analysis first, then use /ask."
            logger.info("Oracle query completed")
            return response
        except Exception as exc:
            logger.error("Oracle query failed: %s", exc)
            return f"[Error] Could not retrieve knowledge: {exc}"


class GitHubIntegrationWrapper:
    """Wraps the GitHub integration for agent use."""

    def __init__(self) -> None:
        try:
            from .github_client import GitHubClientEnhanced

            self.client = GitHubClientEnhanced()
            self.available = True
        except ImportError:
            logger.warning("GitHub client not available")
            self.available = False

    async def get_repository_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get repository information from GitHub."""
        if not self.available:
            return self._mock_repo_info(owner, repo)

        try:
            repository = self.client.github.get_repo(f"{owner}/{repo}")
            info = {
                "owner": owner,
                "name": repo,
                "url": repository.html_url,
                "stars": repository.stargazers_count,
                "contributors": repository.get_contributors().totalCount,
                "commits": repository.get_commits().totalCount,
                "language": repository.language,
                "default_branch": repository.default_branch,
                "mode": "real",
            }
            logger.info("Retrieved repo info: %s/%s", owner, repo)
            return info
        except Exception as exc:
            logger.error("GitHub fetch failed: %s", exc)
            return self._mock_repo_info(owner, repo)

    async def get_commit_history(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """Get recent commit history."""
        if not self.available:
            return self._mock_commits()

        try:
            repository = self.client.github.get_repo(f"{owner}/{repo}")
            commits = [
                {
                    "sha": commit.sha,
                    "message": commit.commit.message,
                    "author": commit.commit.author.name if commit.commit.author else "unknown",
                    "date": commit.commit.author.date.isoformat() if commit.commit.author else None,
                }
                for commit in repository.get_commits()[:50]
            ]
            logger.info("Retrieved %s commits", len(commits))
            return commits
        except Exception as exc:
            logger.error("Commit fetch failed: %s", exc)
            return self._mock_commits()

    @staticmethod
    def _mock_repo_info(owner: str, repo: str) -> Dict[str, Any]:
        return {
            "owner": owner,
            "name": repo,
            "url": f"https://github.com/{owner}/{repo}",
            "stars": 1250,
            "contributors": 24,
            "commits": 2834,
            "language": "Python",
            "mode": "mock",
        }

    @staticmethod
    def _mock_commits() -> List[Dict[str, Any]]:
        return [
            {
                "sha": "abc123",
                "message": "Refactor authentication module",
                "author": "alice",
                "date": "2024-06-15",
            }
        ]


analyzer_service = AnalyzerServiceWrapper()
oracle_service = OracleServiceWrapper()
github_service = GitHubIntegrationWrapper()
