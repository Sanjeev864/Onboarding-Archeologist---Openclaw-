from sqlalchemy.orm import Session

from ..models.analysis import Decision, GhostCodeFinding, KnowledgeOwner, Repository


class Oracle:
    def answer(self, db: Session, repository_id: int, question: str) -> tuple[str, list[str]]:
        repo = db.get(Repository, repository_id)
        if not repo:
            return "I could not find that repository analysis yet.", []

        q = question.lower()
        evidence: list[str] = []

        if any(term in q for term in ("why", "decision", "decide", "architecture")):
            decisions = (
                db.query(Decision)
                .filter(Decision.repository_id == repository_id)
                .order_by(Decision.confidence.desc())
                .limit(5)
                .all()
            )
            evidence = [item.evidence for item in decisions]
            answer = self._decision_answer(repo, decisions)
        elif any(term in q for term in ("owner", "owns", "bus", "expert", "knowledge")):
            owners = (
                db.query(KnowledgeOwner)
                .filter(KnowledgeOwner.repository_id == repository_id)
                .order_by(KnowledgeOwner.commits.desc())
                .limit(8)
                .all()
            )
            evidence = [f"{item.path}: {item.author} made {item.commits} recent commits ({item.risk} risk)" for item in owners]
            answer = "Ownership is concentrated in the paths listed below. High risk means recent history depends heavily on one person."
        elif any(term in q for term in ("dead", "ghost", "remove", "unused", "legacy")):
            ghosts = (
                db.query(GhostCodeFinding)
                .filter(GhostCodeFinding.repository_id == repository_id)
                .order_by(GhostCodeFinding.confidence.desc())
                .limit(8)
                .all()
            )
            evidence = [f"{item.path}: {item.reason}, last touched {item.last_touched_days} days ago" for item in ghosts]
            answer = "These files are removal-review candidates, not automatic deletes. Confirm runtime references and tests before removing them."
        else:
            decisions = db.query(Decision).filter(Decision.repository_id == repository_id).limit(3).all()
            owners = db.query(KnowledgeOwner).filter(KnowledgeOwner.repository_id == repository_id).limit(3).all()
            evidence = [item.evidence for item in decisions] + [
                f"{item.path}: strongest owner is {item.author}" for item in owners
            ]
            answer = "I found the closest historical evidence across decisions and ownership. Ask about decisions, owners, or ghost code for a sharper answer."

        if not evidence:
            answer = "The analysis completed, but there is not enough evidence yet to answer that confidently."
        return answer, evidence

    def _decision_answer(self, repo: Repository, decisions: list[Decision]) -> str:
        if not decisions:
            return "I did not find commit messages with clear decision language in this analysis window."
        top = decisions[0]
        return (
            f"For {repo.owner}/{repo.name}, the strongest decision signal is '{top.title}'. "
            "The confidence comes from explicit rationale terms in the commit history."
        )
