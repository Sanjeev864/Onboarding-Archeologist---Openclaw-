from __future__ import annotations

import json

from sqlalchemy.orm import Session

from ..models.analysis import KnowledgeOwner, OnboardingPath


class OnboardingJourneyGenerator:
    def generate_journey(self, db: Session, repository_id: int, experience_level: str, role: str) -> list[OnboardingPath]:
        existing = (
            db.query(OnboardingPath)
            .filter(
                OnboardingPath.repository_id == repository_id,
                OnboardingPath.experience_level == experience_level,
                OnboardingPath.role == role,
            )
            .order_by(OnboardingPath.day_number)
            .all()
        )
        if existing:
            return existing

        owners = db.query(KnowledgeOwner).filter(KnowledgeOwner.repository_id == repository_id).limit(8).all()
        paths = [owner.path for owner in owners]
        hours = 2.5 if experience_level == "senior" else 3.5 if experience_level == "mid" else 4.5
        days = [
            ("Architecture overview", ["layout", "runtime", role], paths[:3]),
            ("Critical paths", ["core modules", "integration points"], paths[:5]),
            ("Knowledge ownership", ["maintainers", "bus factor"], [owner.author for owner in owners[:5]]),
            ("Defensive patterns", ["error handling", "reliability"], paths[:4]),
            ("First contribution", ["tests", "small PR"], paths[:2]),
        ]
        created: list[OnboardingPath] = []
        for index, (focus, concepts, resources) in enumerate(days, start=1):
            row = OnboardingPath(
                repository_id=repository_id,
                experience_level=experience_level,
                role=role,
                day_number=index,
                focus_area=focus,
                resources=json.dumps({"key_concepts": concepts, "locations": resources}),
                estimated_hours=hours,
            )
            db.add(row)
            created.append(row)
        db.commit()
        return created
