from __future__ import annotations

import hashlib
import hmac
from typing import Any

from github import Github

from ..config import get_settings


class GitHubClientEnhanced:
    def __init__(self, token: str | None = None) -> None:
        configured = token or get_settings().github_token
        self.github = Github(configured) if configured and configured != "your_github_token_here" else Github()

    def get_pr_discussions(self, owner: str, repo: str, limit: int = 50) -> list[dict[str, Any]]:
        repository = self.github.get_repo(f"{owner}/{repo}")
        discussions: list[dict[str, Any]] = []
        for pull in repository.get_pulls(state="all")[:limit]:
            discussions.append({"number": pull.number, "title": pull.title, "body": pull.body or "", "state": pull.state})
        return discussions

    def get_issue_discussions(self, owner: str, repo: str, limit: int = 50) -> list[dict[str, Any]]:
        repository = self.github.get_repo(f"{owner}/{repo}")
        return [
            {"number": issue.number, "title": issue.title, "body": issue.body or "", "state": issue.state}
            for issue in repository.get_issues(state="all")[:limit]
            if not issue.pull_request
        ]

    def register_webhook(self, owner: str, repo: str, webhook_url: str, secret: str) -> dict[str, Any]:
        repository = self.github.get_repo(f"{owner}/{repo}")
        hook = repository.create_hook(
            name="web",
            config={"url": webhook_url, "content_type": "json", "secret": secret},
            events=["push", "pull_request"],
            active=True,
        )
        return {"id": hook.id, "url": webhook_url}

    def validate_webhook_signature(self, payload: bytes, signature: str | None, secret: str) -> bool:
        if not signature or not signature.startswith("sha256="):
            return False
        expected = "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(signature, expected)
