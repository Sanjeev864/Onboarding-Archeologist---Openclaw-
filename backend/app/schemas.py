from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AnalyzeRequest(BaseModel):
    owner: str = Field(min_length=1)
    repo: str = Field(min_length=1)
    branch: str | None = None


class QuestionRequest(BaseModel):
    repository_id: int
    question: str = Field(min_length=3)


class DecisionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    summary: str
    evidence: str
    confidence: float
    commit_sha: str
    committed_at: datetime
    author: str


class OwnerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    path: str
    author: str
    commits: int
    risk: str


class GhostCodeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    path: str
    reason: str
    last_touched_days: int
    confidence: float


class AnalysisOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    repository_id: int
    owner: str
    repo: str
    analyzed_at: datetime
    decisions: list[DecisionOut]
    ownership: list[OwnerOut]
    ghost_code: list[GhostCodeOut]


class AnswerOut(BaseModel):
    answer: str
    evidence: list[str]
