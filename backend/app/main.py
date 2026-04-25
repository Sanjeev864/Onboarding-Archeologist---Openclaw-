from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models.analysis import Decision, GhostCodeFinding, KnowledgeOwner, Repository
from .schemas import AnalyzeRequest, AnalysisOut, AnswerOut, QuestionRequest
from .services.analyzer import RepositoryAnalyzer
from .services.oracle import Oracle

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Onboarding Archaeologist",
    description="Evidence-backed codebase intelligence from git history.",
    version="0.1.0",
)

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
    try:
        result = RepositoryAnalyzer().analyze(request.owner, request.repo, request.branch)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Unable to analyze repository: {exc}") from exc

    existing = (
        db.query(Repository)
        .filter(Repository.owner == request.owner, Repository.name == request.repo)
        .first()
    )
    if existing:
        db.delete(existing)
        db.flush()

    repository = Repository(owner=request.owner, name=request.repo, default_branch=result.default_branch)
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


def _analysis_out(db: Session, repository: Repository) -> AnalysisOut:
    decisions = db.query(Decision).filter(Decision.repository_id == repository.id).all()
    ownership = db.query(KnowledgeOwner).filter(KnowledgeOwner.repository_id == repository.id).all()
    ghost_code = db.query(GhostCodeFinding).filter(GhostCodeFinding.repository_id == repository.id).all()
    return AnalysisOut(
        repository_id=repository.id,
        owner=repository.owner,
        repo=repository.name,
        analyzed_at=repository.analyzed_at,
        decisions=decisions,
        ownership=ownership,
        ghost_code=ghost_code,
    )
