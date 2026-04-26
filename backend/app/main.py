import json
import secrets
from datetime import datetime
from typing import Any

from fastapi import Depends, Header, HTTPException, Request, Response
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import Base, engine, ensure_sqlite_schema, get_db
from .config import get_settings
from .middleware.error_handler import install_error_handlers
from .middleware.logging import configure_logging, install_request_logging
from .models.analysis import (
    AnalysisJob,
    BusFactorAlert,
    Decision,
    GhostCodeFinding,
    KnowledgeOwner,
    OnboardingPath,
    Repository,
    ScarTissuePattern,
    WebhookLog,
)
from .schemas import AnalyzeRequest, AnalysisOut, AnswerOut, JobOut, QuestionRequest, RepositoryWebhookRequest
from .services.analyzer import RepositoryAnalyzer, scar_to_model
from .services.github_client import GitHubClientEnhanced
from .services.onboarding_journey_generator import OnboardingJourneyGenerator
from .services.openclaw_formatter import (
    format_analysis,
    format_answer,
    format_bus_factor,
    format_decisions,
    format_ghost_code,
    format_onboarding,
)
from .services.oracle import Oracle

Base.metadata.create_all(bind=engine)
ensure_sqlite_schema()
settings = get_settings()
logger = configure_logging(settings.log_level)

app = FastAPI(
    title="Onboarding Archaeologist",
    description="Evidence-backed codebase intelligence from git history.",
    version="0.1.0",
)
install_error_handlers(app)
install_request_logging(app, logger)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}


@app.post("/api/analyze", response_model=AnalysisOut)
def analyze(request: AnalyzeRequest, db: Session = Depends(get_db)):
    return _run_analysis(request, db)


@app.post("/api/analyze/advanced", response_model=AnalysisOut)
def analyze_advanced(request: AnalyzeRequest, db: Session = Depends(get_db)):
    return _run_analysis(request, db, create_job=True)


def _run_analysis(request: AnalyzeRequest, db: Session, create_job: bool = False) -> AnalysisOut:
    job: AnalysisJob | None = None
    existing = (
        db.query(Repository)
        .filter(Repository.owner == request.owner, Repository.name == request.repo)
        .first()
    )
    if create_job and existing:
        job = AnalysisJob(repository_id=existing.id, status="processing", started_at=datetime.utcnow(), progress=10)
        db.add(job)
        db.commit()
    try:
        result = RepositoryAnalyzer().analyze(request.owner, request.repo, request.branch)
    except Exception as exc:
        if job:
            job.status = "failed"
            job.completed_at = datetime.utcnow()
            job.error_message = str(exc)
            db.commit()
        raise HTTPException(status_code=422, detail=f"Unable to analyze repository: {exc}") from exc

    if existing:
        db.delete(existing)
        db.flush()

    repository = Repository(
        owner=request.owner,
        name=request.repo,
        default_branch=result.default_branch,
        total_commits_analyzed=result.total_commits_analyzed,
        coverage_percentage=result.coverage_percentage,
    )
    db.add(repository)
    db.flush()

    db.add_all(
        Decision(repository_id=repository.id, **signal.__dict__)
        for signal in result.decisions
    )
    db.add_all(
        KnowledgeOwner(repository_id=repository.id, **signal.__dict__)
        for signal in result.ownership
    )
    db.add_all(
        GhostCodeFinding(repository_id=repository.id, **signal.__dict__)
        for signal in result.ghost_code
    )
    db.add_all(
        ScarTissuePattern(repository_id=repository.id, **scar_to_model(signal))
        for signal in result.scar_tissue
    )
    db.add_all(
        BusFactorAlert(
            repository_id=repository.id,
            critical_person=signal.critical_person,
            areas_affected=json.dumps(signal.areas_affected),
            concentration=signal.concentration_percentage / 100,
            risk_level=signal.risk_level,
            last_triggered=datetime.utcnow(),
        )
        for signal in result.bus_factor_alerts
    )
    db.add_all(
        OnboardingPath(
            repository_id=repository.id,
            experience_level="all",
            role="all",
            day_number=signal.day_number,
            focus_area=signal.focus_area,
            resources=json.dumps(
                {
                    "key_concepts": signal.key_concepts,
                    "locations": signal.code_locations,
                    "learning_resources": signal.learning_resources,
                }
            ),
            estimated_hours=signal.estimated_hours,
        )
        for signal in result.onboarding_paths
    )
    if create_job:
        db.add(AnalysisJob(repository_id=repository.id, status="complete", started_at=datetime.utcnow(), completed_at=datetime.utcnow(), progress=100))
    db.commit()
    db.refresh(repository)
    return _analysis_out(db, repository)


@app.get("/api/repositories")
def repositories(db: Session = Depends(get_db)):
    rows = db.query(Repository).order_by(Repository.analyzed_at.desc()).all()
    return [
        {
            "id": row.id,
            "owner": row.owner,
            "repo": row.name,
            "analyzed_at": row.analyzed_at,
        }
        for row in rows
    ]


@app.get("/api/repositories/{repository_id}", response_model=AnalysisOut)
def repository(repository_id: int, db: Session = Depends(get_db)):
    row = db.get(Repository, repository_id)
    if not row:
        raise HTTPException(status_code=404, detail="Repository not found")
    return _analysis_out(db, row)


@app.post("/api/oracle", response_model=AnswerOut)
def oracle(request: QuestionRequest, db: Session = Depends(get_db)):
    answer, evidence = Oracle().answer(db, request.repository_id, request.question)
    return AnswerOut(answer=answer, evidence=evidence)


@app.post("/api/oracle/ask", response_model=AnswerOut)
def oracle_ask(request: QuestionRequest, include_evidence: bool = True, db: Session = Depends(get_db)):
    answer, evidence = Oracle().answer(db, request.repository_id, request.question)
    return AnswerOut(answer=answer, evidence=evidence if include_evidence else [])


@app.post("/api/oracle/search")
def oracle_search(repository_id: int, query: str, search_type: str = "keyword", db: Session = Depends(get_db)):
    del search_type
    query_lower = query.lower()
    analysis = _analysis_out(db, _require_repo(db, repository_id))
    matches: list[dict[str, Any]] = []
    for decision in analysis.decisions:
        haystack = f"{decision.title} {decision.summary} {decision.evidence}".lower()
        if query_lower in haystack:
            matches.append({"type": "decision", "title": decision.title, "evidence": decision.evidence})
    for ghost in analysis.ghost_code:
        if query_lower in f"{ghost.path} {ghost.reason}".lower():
            matches.append({"type": "ghost_code", "path": ghost.path, "evidence": ghost.reason})
    return {"repository_id": repository_id, "query": query, "matches": matches[:25]}


@app.get("/api/analysis/{repository_id}/job", response_model=JobOut | None)
def get_analysis_job(repository_id: int, db: Session = Depends(get_db)):
    _require_repo(db, repository_id)
    return (
        db.query(AnalysisJob)
        .filter(AnalysisJob.repository_id == repository_id)
        .order_by(AnalysisJob.id.desc())
        .first()
    )


@app.get("/api/analysis/{repository_id}/scar-tissue")
def get_scar_tissue(repository_id: int, db: Session = Depends(get_db)):
    _require_repo(db, repository_id)
    return _scar_tissue_out(db.query(ScarTissuePattern).filter(ScarTissuePattern.repository_id == repository_id).all())


@app.get("/api/analysis/{repository_id}/bus-factor")
def get_bus_factor(repository_id: int, db: Session = Depends(get_db)):
    _require_repo(db, repository_id)
    return _bus_factor_out(db.query(BusFactorAlert).filter(BusFactorAlert.repository_id == repository_id).all())


@app.get("/api/analysis/{repository_id}/onboarding/{experience_level}/{role}")
def get_onboarding_path(repository_id: int, experience_level: str, role: str, db: Session = Depends(get_db)):
    _require_repo(db, repository_id)
    rows = OnboardingJourneyGenerator().generate_journey(db, repository_id, experience_level, role)
    return _onboarding_out(rows)


@app.post("/api/webhooks/github/subscribe")
def subscribe_webhook(request: RepositoryWebhookRequest, db: Session = Depends(get_db)):
    repo = _require_repo(db, request.repository_id)
    repo.webhook_secret = repo.webhook_secret or secrets.token_urlsafe(32)
    repo.auto_reanalyze = request.auto_reanalyze
    db.commit()
    registered = None
    if request.webhook_url:
        registered = GitHubClientEnhanced().register_webhook(repo.owner, repo.name, request.webhook_url, repo.webhook_secret)
    return {
        "repository_id": repo.id,
        "webhook_url": request.webhook_url or "/api/webhooks/github/event",
        "secret": repo.webhook_secret,
        "registered": registered,
    }


@app.post("/api/webhooks/github/event")
async def github_webhook(
    request: Request,
    x_github_event: str = Header(default="unknown"),
    x_hub_signature_256: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    payload = await request.body()
    data = json.loads(payload.decode() or "{}")
    repo_data = data.get("repository") or {}
    full_name = repo_data.get("full_name", "/")
    owner, name = full_name.split("/", 1) if "/" in full_name else ("", "")
    repo = db.query(Repository).filter(Repository.owner == owner, Repository.name == name).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not subscribed")
    if repo.webhook_secret and not GitHubClientEnhanced().validate_webhook_signature(payload, x_hub_signature_256, repo.webhook_secret):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    repo.last_webhook_received = datetime.utcnow()
    db.add(WebhookLog(repository_id=repo.id, event_type=x_github_event, payload=payload.decode(), processed_at=datetime.utcnow(), success=True))
    if repo.auto_reanalyze:
        db.add(AnalysisJob(repository_id=repo.id, status="queued", progress=0))
    db.commit()
    return {"status": "accepted", "auto_reanalyze": repo.auto_reanalyze}


@app.post("/api/repositories/{repository_id}/reanalyze", response_model=AnalysisOut)
def reanalyze_repository(repository_id: int, db: Session = Depends(get_db)):
    repo = _require_repo(db, repository_id)
    return _run_analysis(AnalyzeRequest(owner=repo.owner, repo=repo.name, branch=repo.default_branch), db, create_job=True)


@app.delete("/api/repositories/{repository_id}")
def delete_repository(repository_id: int, db: Session = Depends(get_db)):
    repo = _require_repo(db, repository_id)
    db.delete(repo)
    db.commit()
    return {"deleted": repository_id}


@app.get("/api/repositories/{repository_id}/export")
def export_analysis(repository_id: int, format: str = "json", db: Session = Depends(get_db)):
    repo = _require_repo(db, repository_id)
    payload = _analysis_out(db, repo).model_dump(mode="json")
    if format == "html":
        html = f"<html><body><pre>{json.dumps(payload, indent=2)}</pre></body></html>"
        return Response(content=html, media_type="text/html")
    return payload


@app.get("/api/health/detailed")
def health_detailed(db: Session = Depends(get_db)):
    repo_count = db.query(Repository).count()
    last = db.query(Repository).order_by(Repository.analyzed_at.desc()).first()
    return {
        "status": "ok",
        "database": "ok",
        "repositories": repo_count,
        "last_successful_analysis": last.analyzed_at if last else None,
        "llm": "configured" if settings.anthropic_api_key else "optional",
    }


@app.get("/api/metrics")
def get_metrics(db: Session = Depends(get_db)):
    return {
        "repositories": db.query(Repository).count(),
        "decisions": db.query(Decision).count(),
        "ghost_code_findings": db.query(GhostCodeFinding).count(),
        "scar_tissue_patterns": db.query(ScarTissuePattern).count(),
        "bus_factor_alerts": db.query(BusFactorAlert).count(),
    }


@app.post("/api/openclaw/analyze")
def openclaw_analyze(request: AnalyzeRequest, db: Session = Depends(get_db)):
    formatted = format_analysis(_run_analysis(request, db, create_job=True))
    return {"text": formatted.text, "repository_id": formatted.repository_id}


@app.post("/api/openclaw/ask")
def openclaw_ask(request: QuestionRequest, db: Session = Depends(get_db)):
    answer, evidence = Oracle().answer(db, request.repository_id, request.question)
    return {"text": format_answer(AnswerOut(answer=answer, evidence=evidence))}


@app.get("/api/openclaw/repositories/latest")
def openclaw_latest_repository(db: Session = Depends(get_db)):
    row = db.query(Repository).order_by(Repository.analyzed_at.desc()).first()
    if not row:
        raise HTTPException(status_code=404, detail="No analyzed repository found")
    return {"repository_id": row.id, "owner": row.owner, "repo": row.name}


@app.get("/api/openclaw/repositories/{repository_id}/decisions")
def openclaw_decisions(repository_id: int, db: Session = Depends(get_db)):
    return {"text": format_decisions(_analysis_out(db, _require_repo(db, repository_id)))}


@app.get("/api/openclaw/repositories/{repository_id}/bus-factor")
def openclaw_bus_factor(repository_id: int, db: Session = Depends(get_db)):
    return {"text": format_bus_factor(_analysis_out(db, _require_repo(db, repository_id)))}


@app.get("/api/openclaw/repositories/{repository_id}/ghost-code")
def openclaw_ghost_code(repository_id: int, db: Session = Depends(get_db)):
    return {"text": format_ghost_code(_analysis_out(db, _require_repo(db, repository_id)))}


@app.get("/api/openclaw/repositories/{repository_id}/onboarding/{level}")
def openclaw_onboarding(repository_id: int, level: str, db: Session = Depends(get_db)):
    return {"text": format_onboarding(_analysis_out(db, _require_repo(db, repository_id)), level)}


def _analysis_out(db: Session, repository: Repository) -> AnalysisOut:
    decisions = db.query(Decision).filter(Decision.repository_id == repository.id).all()
    ownership = db.query(KnowledgeOwner).filter(KnowledgeOwner.repository_id == repository.id).all()
    ghost_code = db.query(GhostCodeFinding).filter(GhostCodeFinding.repository_id == repository.id).all()
    scar_tissue = db.query(ScarTissuePattern).filter(ScarTissuePattern.repository_id == repository.id).all()
    bus_factor = db.query(BusFactorAlert).filter(BusFactorAlert.repository_id == repository.id).all()
    onboarding = db.query(OnboardingPath).filter(OnboardingPath.repository_id == repository.id).order_by(OnboardingPath.day_number).all()
    return AnalysisOut(
        repository_id=repository.id,
        owner=repository.owner,
        repo=repository.name,
        analyzed_at=repository.analyzed_at,
        decisions=decisions,
        ownership=ownership,
        ghost_code=ghost_code,
        scar_tissue=_scar_tissue_out(scar_tissue),
        bus_factor_alerts=_bus_factor_out(bus_factor),
        onboarding_paths=_onboarding_out(onboarding),
        coverage_summary={
            "total_commits_analyzed": repository.total_commits_analyzed,
            "coverage_percentage": repository.coverage_percentage,
            "default_branch": repository.default_branch,
        },
    )


def _require_repo(db: Session, repository_id: int) -> Repository:
    row = db.get(Repository, repository_id)
    if not row:
        raise HTTPException(status_code=404, detail="Repository not found")
    return row


def _scar_tissue_out(rows: list[ScarTissuePattern]) -> list[dict[str, Any]]:
    return [
        {
            "pattern_type": row.pattern_type,
            "file_path": row.file_path,
            "line_numbers": json.loads(row.line_numbers or "[]"),
            "incident_summary": row.related_incident,
            "severity": row.severity,
            "confidence": row.confidence,
            "explanation": f"{row.pattern_type.replace('_', ' ').title()} found near lines {row.line_numbers}.",
        }
        for row in rows
    ]


def _bus_factor_out(rows: list[BusFactorAlert]) -> list[dict[str, Any]]:
    return [
        {
            "critical_person": row.critical_person,
            "areas_affected": json.loads(row.areas_affected or "[]"),
            "concentration_percentage": round(row.concentration * 100, 1),
            "risk_level": row.risk_level,
            "recommendation": "Pair on this area and document the key decisions.",
        }
        for row in rows
    ]


def _onboarding_out(rows: list[OnboardingPath]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for row in rows:
        resources = json.loads(row.resources or "{}")
        output.append(
            {
                "day_number": row.day_number,
                "focus_area": row.focus_area,
                "key_concepts": resources.get("key_concepts", []),
                "code_locations": resources.get("locations", []),
                "estimated_hours": row.estimated_hours,
                "learning_resources": resources.get("learning_resources", resources.get("locations", [])),
            }
        )
    return output
