from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Repository(Base):
    __tablename__ = "repositories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner: Mapped[str] = mapped_column(String(120), index=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    default_branch: Mapped[str] = mapped_column(String(120), default="main")
    analyzed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    decisions: Mapped[list["Decision"]] = relationship(cascade="all, delete-orphan")
    ownership: Mapped[list["KnowledgeOwner"]] = relationship(cascade="all, delete-orphan")
    ghost_code: Mapped[list["GhostCodeFinding"]] = relationship(cascade="all, delete-orphan")


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
