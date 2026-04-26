from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AnalyzeRequest(BaseModel):
    owner: str = Field(min_length=1)
    repo: str = Field(min_length=1)
    branch: str | None = None


class QuestionRequest(BaseModel):
    repository_id: int
    question: str = Field(min_length=3)
    context: str | None = None


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


class ScarTissueOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pattern_type: str
    file_path: str
    line_numbers: list[int]
    incident_summary: str
    severity: str
    confidence: float
    explanation: str


class BusFactorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    critical_person: str
    areas_affected: list[str]
    concentration_percentage: float
    risk_level: str
    recommendation: str


class OnboardingDayOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    day_number: int
    focus_area: str
    key_concepts: list[str]
    code_locations: list[str]
    estimated_hours: float
    learning_resources: list[str]


class AnalysisOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    repository_id: int
    owner: str
    repo: str
    analyzed_at: datetime
    decisions: list[DecisionOut]
    ownership: list[OwnerOut]
    ghost_code: list[GhostCodeOut]
    scar_tissue: list[ScarTissueOut] = []
    bus_factor_alerts: list[BusFactorOut] = []
    onboarding_paths: list[OnboardingDayOut] = []
    coverage_summary: dict = {}


class AnswerOut(BaseModel):
    answer: str
    evidence: list[str]


class RepositoryWebhookRequest(BaseModel):
    repository_id: int
    webhook_url: str | None = None
    auto_reanalyze: bool = True


class JobOut(BaseModel):
    id: int
    repository_id: int
    status: str
    progress: int
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error_message: str | None = None
