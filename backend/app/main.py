import json
import secrets
import asyncio
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
from .services.report_formatter import ReportFormatter, HTMLReportFormatter
from dotenv import load_dotenv
load_dotenv()

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

# Telegram Bot Integration
from telegram.ext import Application
from .telegram_bot import setup_telegram_bot
from .telegram_integration import setup_telegram_webhook

# Initialize Telegram Bot
try:
    bot_application = setup_telegram_bot()
    setup_telegram_webhook(app, bot_application)
    logger.info("✅ Telegram bot initialized successfully")
except ValueError as e:
    logger.warning(f"⚠️  Telegram bot not configured: {e}")
    bot_application = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from .agents.orchestrator import AnalysisOrchestrationAgent, OnboardingOrchestrationAgent

# Initialize agents
analysis_orchestrator = AnalysisOrchestrationAgent()
onboarding_orchestrator = OnboardingOrchestrationAgent()

from .agents.evidence_agents import (
    RepositoryPerceptionAgent,
    ArchitecturalDecisionAgent,
    OwnershipAnalysisAgent,
    GhostCodeDetectorAgent,
    BusFactorEvaluatorAgent,
    ScarTissueAnalyzerAgent,
    OnboardingPathGeneratorAgent
)

# Initialize agents at module level
perception_agent = RepositoryPerceptionAgent()
decision_agent = ArchitecturalDecisionAgent()
ownership_agent = OwnershipAnalysisAgent()
ghost_code_agent = GhostCodeDetectorAgent()
bus_factor_agent = BusFactorEvaluatorAgent()
scar_tissue_agent = ScarTissueAnalyzerAgent()
onboarding_agent = OnboardingPathGeneratorAgent()


def _analysis_agents() -> dict[str, Any]:
    return {
        "perception": perception_agent,
        "decisions": decision_agent,
        "ownership": ownership_agent,
        "ghost_code": ghost_code_agent,
        "bus_factor": bus_factor_agent,
        "scar_tissue": scar_tissue_agent,
    }


async def _run_agentic_analysis(owner: str, repo: str, branch: str | None = None, use_cache: bool = True) -> dict[str, Any]:
    """Run the evidence-backed multi-agent workflow for a GitHub repository."""
    if use_cache:
        cached_result = analysis_cache.get(owner, repo)
        if cached_result:
            return {**cached_result, "message": "Result from cache", "source": "cache"}

    analysis_input = {
        "owner": owner,
        "repo": repo,
        "branch": branch,
        "repo_path": None,
        "analysis_scope": "full",
    }

    agents = _analysis_agents()
    for agent in agents.values():
        agent.memory["owner"] = owner
        agent.memory["repo"] = repo
        agent.memory["branch"] = branch
        agent.memory["analysis_input"] = analysis_input

    perception_result = await agents["perception"].run_cycle(analysis_input)
    specialist_names = ["decisions", "ownership", "ghost_code", "bus_factor", "scar_tissue"]
    specialist_results = await asyncio.gather(
        *(agents[name].run_cycle(analysis_input) for name in specialist_names),
        return_exceptions=True,
    )

    agent_results: dict[str, Any] = {"perception": perception_result}
    for name, response in zip(specialist_names, specialist_results):
        agent_results[name] = {"error": str(response)} if isinstance(response, Exception) else response

    result = {
        "status": "success",
        "repository": f"{owner}/{repo}",
        "analysis_mode": "agentic_evidence_workflow",
        "workflow": [
            "perception gathers repository metadata and evidence",
            "specialist agents reason over shared analysis evidence",
            "decision traces expose each agent thought and action",
            "feedback endpoint stores human review signals for later runs",
        ],
        "llm": {
            "enabled": settings.enable_llm_analysis,
            "provider": settings.llm_provider,
            "model": settings.llm_model if settings.llm_provider.lower() in {"ollama", "local"} else settings.anthropic_model,
        },
        "timestamp": datetime.now().isoformat(),
        "agents_executed": len(agents),
        "data_source": "git_history_and_github_api",
        "source": "real_analysis",
        "agent_results": agent_results,
        "agent_summaries": {name: agent.get_summary() for name, agent in agents.items()},
        "decision_traces": {name: agent.get_decision_trace() for name, agent in agents.items()},
        "message": "Agentic repository analysis completed",
    }

    if use_cache:
        analysis_cache.set(owner, repo, result)
    return result


@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}


@app.post("/api/analyze", response_model=AnalysisOut)
def analyze(request: AnalyzeRequest, db: Session = Depends(get_db)):
    return _run_analysis(request, db)


@app.post("/api/analyze/advanced", response_model=AnalysisOut)
def analyze_advanced(request: AnalyzeRequest, db: Session = Depends(get_db)):
    return _run_analysis(request, db, create_job=True)

@app.get("/api/v2/analyze-autonomous-report")
async def analyze_autonomous_report(owner: str, repo: str, format: str = "text"):
    """Get analysis as formatted report (text or HTML)"""
    try:
        # Run analysis
        result = await analyze_autonomous(owner, repo)
        
        if format == "html":
            html_report = HTMLReportFormatter.format_analysis_as_html(result)
            return {"report": html_report, "format": "html"}
        else:  # text
            text_report = ReportFormatter.format_analysis_report(result)
            return {"report": text_report, "format": "text"}
    
    except Exception as e:
        return {"status": "error", "error": str(e)}

from .services.agent_pool import PoolManager
from .services.cache import analysis_cache

@app.post("/api/v2/analyze-autonomous")
async def analyze_autonomous(owner: str, repo: str, repo_path: str = None, use_cache: bool = True):
    """Analyze with the evidence-backed multi-agent workflow."""
    try:
        return await _run_agentic_analysis(owner, repo, branch=repo_path, use_cache=use_cache)
    except Exception as e:
        logger.error(f"Autonomous analysis failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "agents_attempted": 6
        }


@app.get("/api/v2/system-stats")
async def system_stats():
    """Get system performance statistics"""
    return {
        "timestamp": datetime.now().isoformat(),
        "pools": PoolManager.get_stats(),
        "cache": analysis_cache.get_stats()
    }

@app.get("/api/v2/agent-decision-trace-report/{agent_name}")
async def agent_decision_trace_report(agent_name: str):
    """Get formatted decision trace"""
    result = await agent_decision_trace(agent_name)
    
    if "error" in result:
        return result
    
    formatted = ReportFormatter.format_decision_trace_report(
        agent_name,
        result.get("decision_trace", [])
    )
    
    return {
        "agent_name": agent_name,
        "report": formatted,
        "format": "text"
    }

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

# ============================================================================
# AUTONOMOUS AGENT ENDPOINTS
# ============================================================================

@app.post("/api/v2/analyze-autonomous")
async def analyze_autonomous(owner: str, repo: str, repo_path: str = None):
    """Analyze repository using autonomous agents with REAL DATA"""
    try:
        analysis_input = {
            "owner": owner,
            "repo": repo,
            "repo_path": repo_path or f"/tmp/{owner}_{repo}",
            "analysis_scope": "full"
        }
        
        # ✨ NEW: Store owner and repo in agent memory BEFORE running
        for agent in [perception_agent, decision_agent, ownership_agent,
                     ghost_code_agent, bus_factor_agent, scar_tissue_agent]:
            agent.memory["owner"] = owner
            agent.memory["repo"] = repo
            agent.memory["repo_path"] = analysis_input["repo_path"]
            agent.memory["analysis_input"] = analysis_input
        
        print(f"🤖 Starting autonomous analysis: {owner}/{repo}")
        
        # Run all agents - they'll now use REAL data from services
        perception_result = await perception_agent.run_cycle(analysis_input)
        decision_result = await decision_agent.run_cycle(analysis_input)
        ownership_result = await ownership_agent.run_cycle(analysis_input)
        ghost_code_result = await ghost_code_agent.run_cycle(analysis_input)
        bus_factor_result = await bus_factor_agent.run_cycle(analysis_input)
        scar_tissue_result = await scar_tissue_agent.run_cycle(analysis_input)
        
        agent_results = {
            "perception": perception_result,
            "decisions": decision_result,
            "ownership": ownership_result,
            "ghost_code": ghost_code_result,
            "bus_factor": bus_factor_result,
            "scar_tissue": scar_tissue_result
        }
        
        agent_summaries = {
            "perception": perception_agent.get_summary(),
            "decisions": decision_agent.get_summary(),
            "ownership": ownership_agent.get_summary(),
            "ghost_code": ghost_code_agent.get_summary(),
            "bus_factor": bus_factor_agent.get_summary(),
            "scar_tissue": scar_tissue_agent.get_summary()
        }
        
        decision_traces = {
            "perception": perception_agent.get_decision_trace(),
            "decisions": decision_agent.get_decision_trace(),
            "ownership": ownership_agent.get_decision_trace(),
            "ghost_code": ghost_code_agent.get_decision_trace(),
            "bus_factor": bus_factor_agent.get_decision_trace(),
            "scar_tissue": scar_tissue_agent.get_decision_trace()
        }
        
        return {
            "status": "success",
            "repository": f"{owner}/{repo}",
            "analysis_mode": "autonomous_agents_with_real_data",  # Updated
            "timestamp": datetime.now().isoformat(),
            "agents_executed": 6,
            "data_source": "real_services",  # New
            "agent_results": agent_results,
            "agent_summaries": agent_summaries,
            "decision_traces": decision_traces,
            "message": "All agents completed analysis with real data"
        }
    
    except Exception as e:
        logger.error(f"Autonomous analysis failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "agents_attempted": 6
        }


@app.post("/api/v2/onboarding-autonomous")
async def onboarding_autonomous(
    repo_id: int,
    level: str = "junior"
):
    """
    Generate onboarding path using Onboarding Path Generator Agent.
    
    Adapts to:
    - level: "junior", "mid", or "senior"
    - Time available: defaults to 40 hours (5 days)
    
    Uses findings from previous analysis to create personalized journey.
    """
    try:
        from sqlalchemy.orm import Session
        
        # Get the analysis from database
        db: Session = next(get_db())
        
        repo = db.query(Repository).filter(Repository.id == repo_id).first()
        if not repo:
            return {"status": "error", "error": "Repository not found"}
        
        # Prepare onboarding input
        onboarding_input = {
            "level": level,
            "analysis": _analysis_out(db, repo).model_dump(mode="json"),
            "time_available_hours": 40,
            "preferences": {}
        }
        
        # Run agent
        result = await onboarding_agent.run_cycle(onboarding_input)
        
        return {
            "status": "success",
            "repository_id": repo_id,
            "learner_level": level,
            "agent_summary": onboarding_agent.get_summary(),
            "path_generated": result,
            "agent_trace": onboarding_agent.get_execution_trace()
        }
    
    except Exception as e:
        logger.error(f"Onboarding generation failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }




@app.get("/api/v2/agent-status")
async def agent_status():
    """
    Get status of all autonomous agents.
    
    Returns:
    - Agents initialized
    - Last execution details
    - Decision histories
    - Memory snapshots
    """
    return {
        "status": "operational",
        "agents": {
            "perception": perception_agent.get_summary(),
            "decisions": decision_agent.get_summary(),
            "ownership": ownership_agent.get_summary(),
            "ghost_code": ghost_code_agent.get_summary(),
            "bus_factor": bus_factor_agent.get_summary(),
            "scar_tissue": scar_tissue_agent.get_summary(),
            "onboarding": onboarding_agent.get_summary()
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v2/agent-decision-trace/{agent_name}")
async def agent_decision_trace(agent_name: str):
    """
    Get decision trace for a specific agent.
    
    Shows all thoughts, decisions, and execution results.
    Useful for understanding agent reasoning.
    """
    agent_map = {
        "perception": perception_agent,
        "decisions": decision_agent,
        "ownership": ownership_agent,
        "ghost_code": ghost_code_agent,
        "bus_factor": bus_factor_agent,
        "scar_tissue": scar_tissue_agent,
        "onboarding": onboarding_agent
    }
    
    agent = agent_map.get(agent_name.lower())
    if not agent:
        return {
            "error": f"Agent '{agent_name}' not found",
            "available_agents": list(agent_map.keys())
        }
    
    return {
        "agent_id": agent.agent_id,
        "agent_name": agent.agent_name,
        "decision_trace": agent.get_decision_trace(),
        "execution_trace": agent.get_execution_trace(),
        "memory_snapshot": agent.memory,
        "summary": agent.get_summary()
    }


@app.get("/api/v2/agent-decision-trace/{agent_name}")
async def agent_decision_trace(agent_name: str):
    """
    Get decision trace for a specific agent.
    
    Useful for debugging and understanding agent reasoning.
    Shows all thoughts, decisions, and execution results.
    """
    agent_map = {
        "perception": perception_agent,
        "decisions": decision_agent,
        "ownership": ownership_agent,
        "ghost_code": ghost_code_agent,
        "bus_factor": bus_factor_agent,
        "scar_tissue": scar_tissue_agent,
        "onboarding": onboarding_agent
    }
    
    agent = agent_map.get(agent_name)
    if not agent:
        return {"error": f"Agent '{agent_name}' not found"}
    
    return {
        "agent_id": agent.agent_id,
        "agent_name": agent.agent_name,
        "decision_trace": agent.get_decision_trace(),
        "execution_trace": agent.get_execution_trace(),
        "memory_snapshot": agent.memory
    }


@app.post("/api/v2/submit-agent-feedback")
async def submit_agent_feedback(
    agent_id: str,
    execution_id: str,
    feedback_type: str,  # "positive", "negative", "partial"
    feedback_text: str,
    rating: float = 0.5
):
    """
    Submit feedback about agent decisions for learning/adaptation.
    
    Helps agents improve over time:
    - positive: Agent performed well, reinforce this approach
    - negative: Agent missed something, adjust thresholds
    - partial: Mixed results, refine strategy
    
    Rating: 0.0 (terrible) to 1.0 (perfect)
    """
    try:
        agent_map = {
            "perception": perception_agent,
            "decisions": decision_agent,
            "ownership": ownership_agent,
            "ghost_code": ghost_code_agent,
            "bus_factor": bus_factor_agent,
            "scar_tissue": scar_tissue_agent,
            "onboarding": onboarding_agent
        }
        
        agent = agent_map.get(agent_id)
        if not agent:
            return {"status": "error", "error": f"Agent '{agent_id}' not found"}
        
        # Record feedback in agent memory
        if "feedback_history" not in agent.memory:
            agent.memory["feedback_history"] = []
        
        agent.memory["feedback_history"].append({
            "execution_id": execution_id,
            "type": feedback_type,
            "text": feedback_text,
            "rating": rating,
            "timestamp": datetime.now().isoformat()
        })
        
        # Adapt agent based on feedback
        if feedback_type == "positive" and rating > 0.7:
            agent.memory["confidence_boost"] = min(1.5, agent.memory.get("confidence_boost", 1.0) + 0.1)
        elif feedback_type == "negative" and rating < 0.3:
            agent.memory["confidence_reduction"] = min(0.9, agent.memory.get("confidence_reduction", 1.0) + 0.1)
        
        return {
            "status": "success",
            "feedback_recorded": True,
            "agent_adapted": True,
            "agent_id": agent_id
        }
    
    except Exception as e:
        logger.error(f"Feedback processing failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }

@app.post("/api/v2/analyze-autonomous")
async def analyze_autonomous(owner: str, repo: str, repo_path: str = None):
    """
    Analyze repository using autonomous agent workflow.
    
    Runs all agents in parallel:
    - Repository Perception Agent
    - Architectural Decision Agent
    - Ownership Analysis Agent
    - Ghost Code Detector Agent
    - Bus Factor Evaluator Agent
    - Scar Tissue Analyzer Agent
    
    Query params:
    - owner: Repository owner (e.g., "anthropic")
    - repo: Repository name (e.g., "claude-code")
    - repo_path: Local path to repository (optional)
    """
    try:
        import asyncio
        
        # Prepare input for all agents
        analysis_input = {
            "owner": owner,
            "repo": repo,
            "repo_path": repo_path or f"/tmp/{owner}_{repo}",
            "analysis_scope": "full"
        }
        
        # Store input in agent memory for later use
        for agent in [
            perception_agent, decision_agent, ownership_agent,
            ghost_code_agent, bus_factor_agent, scar_tissue_agent
        ]:
            agent.memory["analysis_input"] = analysis_input
        
        # Run all analysis agents in parallel
        print(f"🤖 Starting autonomous analysis: {owner}/{repo}")
        
        perception_result = await perception_agent.run_cycle(analysis_input)
        decision_result = await decision_agent.run_cycle(analysis_input)
        ownership_result = await ownership_agent.run_cycle(analysis_input)
        ghost_code_result = await ghost_code_agent.run_cycle(analysis_input)
        bus_factor_result = await bus_factor_agent.run_cycle(analysis_input)
        scar_tissue_result = await scar_tissue_agent.run_cycle(analysis_input)
        
        # Aggregate results
        agent_results = {
            "perception": perception_result,
            "decisions": decision_result,
            "ownership": ownership_result,
            "ghost_code": ghost_code_result,
            "bus_factor": bus_factor_result,
            "scar_tissue": scar_tissue_result
        }
        
        # Get agent summaries and decision traces
        agent_summaries = {
            "perception": perception_agent.get_summary(),
            "decisions": decision_agent.get_summary(),
            "ownership": ownership_agent.get_summary(),
            "ghost_code": ghost_code_agent.get_summary(),
            "bus_factor": bus_factor_agent.get_summary(),
            "scar_tissue": scar_tissue_agent.get_summary()
        }
        
        decision_traces = {
            "perception": perception_agent.get_decision_trace(),
            "decisions": decision_agent.get_decision_trace(),
            "ownership": ownership_agent.get_decision_trace(),
            "ghost_code": ghost_code_agent.get_decision_trace(),
            "bus_factor": bus_factor_agent.get_decision_trace(),
            "scar_tissue": scar_tissue_agent.get_decision_trace()
        }
        
        return {
            "status": "success",
            "repository": f"{owner}/{repo}",
            "analysis_mode": "autonomous_agents",
            "timestamp": datetime.now().isoformat(),
            "agents_executed": 6,
            "agent_results": agent_results,
            "agent_summaries": agent_summaries,
            "decision_traces": decision_traces,
            "message": "All agents completed analysis successfully"
        }
    
    except Exception as e:
        logger.error(f"Autonomous analysis failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "agents_attempted": 6
        }

    
    
async def analyze_autonomous(owner: str, repo: str, repo_path: str = None, use_cache: bool = True):
    """Shared callable used by report endpoints after duplicate route registration."""
    return await _run_agentic_analysis(owner, repo, branch=repo_path, use_cache=use_cache)


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
        "llm": {
            "enabled": settings.enable_llm_analysis,
            "provider": settings.llm_provider,
            "model": settings.llm_model if settings.llm_provider.lower() in {"ollama", "local"} else settings.anthropic_model,
        },
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
