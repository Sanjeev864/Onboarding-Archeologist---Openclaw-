from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Repository(Base):
    __tablename__ = "repositories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner: Mapped[str] = mapped_column(String(120), index=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    default_branch: Mapped[str] = mapped_column(String(120), default="main")
    analyzed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_webhook_received: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    webhook_secret: Mapped[str | None] = mapped_column(String(200), unique=True, nullable=True)
    auto_reanalyze: Mapped[bool] = mapped_column(Boolean, default=False)
    total_commits_analyzed: Mapped[int] = mapped_column(Integer, default=0)
    coverage_percentage: Mapped[float] = mapped_column(Float, default=0.0)

    decisions: Mapped[list["Decision"]] = relationship(cascade="all, delete-orphan")
    ownership: Mapped[list["KnowledgeOwner"]] = relationship(cascade="all, delete-orphan")
    ghost_code: Mapped[list["GhostCodeFinding"]] = relationship(cascade="all, delete-orphan")
    scar_tissue: Mapped[list["ScarTissuePattern"]] = relationship(cascade="all, delete-orphan")
    bus_factor_alerts: Mapped[list["BusFactorAlert"]] = relationship(cascade="all, delete-orphan")
    analysis_jobs: Mapped[list["AnalysisJob"]] = relationship(cascade="all, delete-orphan")
    onboarding_paths: Mapped[list["OnboardingPath"]] = relationship(cascade="all, delete-orphan")
    webhook_logs: Mapped[list["WebhookLog"]] = relationship(cascade="all, delete-orphan")


class Decision(Base):
    __tablename__ = "decisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    repository_id: Mapped[int] = mapped_column(ForeignKey("repositories.id"))
    title: Mapped[str] = mapped_column(String(240))
    summary: Mapped[str] = mapped_column(Text)
    evidence: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    commit_sha: Mapped[str] = mapped_column(String(80))
    committed_at: Mapped[datetime] = mapped_column(DateTime)
    author: Mapped[str] = mapped_column(String(160))


class KnowledgeOwner(Base):
    __tablename__ = "knowledge_owners"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    repository_id: Mapped[int] = mapped_column(ForeignKey("repositories.id"))
    path: Mapped[str] = mapped_column(String(500))
    author: Mapped[str] = mapped_column(String(160))
    commits: Mapped[int] = mapped_column(Integer)
    risk: Mapped[str] = mapped_column(String(40))


class GhostCodeFinding(Base):
    __tablename__ = "ghost_code_findings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    repository_id: Mapped[int] = mapped_column(ForeignKey("repositories.id"))
    path: Mapped[str] = mapped_column(String(500))
    reason: Mapped[str] = mapped_column(Text)
    last_touched_days: Mapped[int] = mapped_column(Integer)
    confidence: Mapped[float] = mapped_column(Float)


class ScarTissuePattern(Base):
    __tablename__ = "scar_tissue_patterns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    repository_id: Mapped[int] = mapped_column(ForeignKey("repositories.id"))
    pattern_type: Mapped[str] = mapped_column(String(100))
    file_path: Mapped[str] = mapped_column(String(500))
    line_numbers: Mapped[str] = mapped_column(Text)
    incident_date: Mapped[datetime] = mapped_column(DateTime)
    related_incident: Mapped[str] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(20))
    confidence: Mapped[float] = mapped_column(Float)


class BusFactorAlert(Base):
    __tablename__ = "bus_factor_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    repository_id: Mapped[int] = mapped_column(ForeignKey("repositories.id"))
    critical_person: Mapped[str] = mapped_column(String(160))
    areas_affected: Mapped[str] = mapped_column(Text)
    concentration: Mapped[float] = mapped_column(Float)
    risk_level: Mapped[str] = mapped_column(String(20))
    last_triggered: Mapped[datetime] = mapped_column(DateTime)
    dismissal_reason: Mapped[str | None] = mapped_column(Text, nullable=True)


class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    repository_id: Mapped[int] = mapped_column(ForeignKey("repositories.id"))
    status: Mapped[str] = mapped_column(String(20))
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    progress: Mapped[int] = mapped_column(Integer, default=0)


class OnboardingPath(Base):
    __tablename__ = "onboarding_paths"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    repository_id: Mapped[int] = mapped_column(ForeignKey("repositories.id"))
    experience_level: Mapped[str] = mapped_column(String(50))
    role: Mapped[str] = mapped_column(String(100))
    day_number: Mapped[int] = mapped_column(Integer)
    focus_area: Mapped[str] = mapped_column(String(500))
    resources: Mapped[str] = mapped_column(Text)
    estimated_hours: Mapped[float] = mapped_column(Float)


class WebhookLog(Base):
    __tablename__ = "webhook_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    repository_id: Mapped[int] = mapped_column(ForeignKey("repositories.id"))
    event_type: Mapped[str] = mapped_column(String(100))
    payload: Mapped[str] = mapped_column(Text)
    processed_at: Mapped[datetime] = mapped_column(DateTime)
    success: Mapped[bool] = mapped_column(Boolean, default=True)
