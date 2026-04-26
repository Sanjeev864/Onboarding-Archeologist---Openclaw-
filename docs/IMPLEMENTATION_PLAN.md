# Onboarding Archaeologist - Complete Implementation Plan
## Industry-Standard, Production-Ready System

---

## EXECUTIVE SUMMARY

This document provides a complete technical implementation plan to transform the Onboarding Archaeologist MVP into an industry-standard, production-ready codebase intelligence platform. The system will use only free APIs (GitHub, Anthropic) and local open-source tools to maintain zero operating costs while achieving enterprise-grade functionality.

**Key Objectives:**
- Complete LLM integration for intelligent analysis (not just heuristics)
- Implement all 6 Intelligence Layers from the specification
- Build comprehensive error handling and resilience
- Create production-grade frontend with proper state management
- Implement real-time updates and webhooks
- Add multi-repository analysis capabilities
- Implement persistent background analysis
- Create monitoring, logging, and observability
- Build comprehensive documentation and testing

---

## PHASE 1: FOUNDATION & CORE INTELLIGENCE (WEEKS 1-2)

### 1.1 Backend Architecture Overhaul

#### 1.1.1 Enhanced Configuration System
**File:** `backend/app/config.py`

**Changes:**
```python
# Add new configuration parameters
- Add support for multiple LLM providers (free Anthropic API as primary)
- Add queue system configuration (Redis alternative: in-memory for MVP)
- Add caching strategy configuration
- Add webhook configuration
- Add logging configuration with structured logging
- Add rate limiting configuration
- Add feature flags for gradual rollout
```

**Specific Additions:**
- `anthropic_api_key: str` - Free Anthropic API for analysis
- `cache_dir: str` - Local file-based cache for LLM responses
- `queue_type: str` - "memory" | "redis" (default: "memory")
- `log_level: str` - "DEBUG" | "INFO" | "WARNING"
- `max_workers: int` - Parallel analysis workers (default: 4)
- `webhook_timeout: int` - seconds (default: 30)
- `analysis_timeout: int` - seconds (default: 300)

#### 1.1.2 Database Enhancement
**File:** `backend/app/models/analysis.py`

**Add Models:**

```python
# 1. ScarTissuePattern Model
class ScarTissuePattern(Base):
    __tablename__ = "scar_tissue_patterns"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    repository_id: Mapped[int] = mapped_column(ForeignKey("repositories.id"))
    pattern_type: Mapped[str] = mapped_column(String(100))  # "defensive_check", "retry_loop", "fallback"
    file_path: Mapped[str] = mapped_column(String(500))
    line_numbers: Mapped[str] = mapped_column(Text)  # JSON array
    incident_date: Mapped[datetime] = mapped_column(DateTime)  # When incident occurred
    related_incident: Mapped[str] = mapped_column(Text)  # Description of incident
    severity: Mapped[str] = mapped_column(String(20))  # "high" | "medium" | "low"
    confidence: Mapped[float] = mapped_column(Float)

# 2. BusFactorAlert Model
class BusFactorAlert(Base):
    __tablename__ = "bus_factor_alerts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    repository_id: Mapped[int] = mapped_column(ForeignKey("repositories.id"))
    critical_person: Mapped[str] = mapped_column(String(160))
    areas_affected: Mapped[str] = mapped_column(Text)  # JSON array of paths
    concentration: Mapped[float] = mapped_column(Float)  # 0-1, percentage
    risk_level: Mapped[str] = mapped_column(String(20))  # "critical" | "high" | "medium"
    last_triggered: Mapped[datetime] = mapped_column(DateTime)
    dismissal_reason: Mapped[str] = mapped_column(Text, nullable=True)

# 3. AnalysisJob Model (for background processing)
class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    repository_id: Mapped[int] = mapped_column(ForeignKey("repositories.id"))
    status: Mapped[str] = mapped_column(String(20))  # "queued" | "processing" | "complete" | "failed"
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    progress: Mapped[int] = mapped_column(Integer, default=0)  # 0-100

# 4. OnboardingPath Model
class OnboardingPath(Base):
    __tablename__ = "onboarding_paths"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    repository_id: Mapped[int] = mapped_column(ForeignKey("repositories.id"))
    experience_level: Mapped[str] = mapped_column(String(50))  # "junior" | "mid" | "senior"
    role: Mapped[str] = mapped_column(String(100))  # "backend" | "frontend" | "fullstack" | "devops"
    day_number: Mapped[int] = mapped_column(Integer)  # 1-5
    focus_area: Mapped[str] = mapped_column(String(500))  # What to learn on this day
    resources: Mapped[str] = mapped_column(Text)  # JSON array of findings
    estimated_hours: Mapped[float] = mapped_column(Float)

# 5. WebhookLog Model
class WebhookLog(Base):
    __tablename__ = "webhook_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    repository_id: Mapped[int] = mapped_column(ForeignKey("repositories.id"))
    event_type: Mapped[str] = mapped_column(String(100))
    payload: Mapped[str] = mapped_column(Text)  # JSON
    processed_at: Mapped[datetime] = mapped_column(DateTime)
    success: Mapped[bool] = mapped_column(default=True)
```

**Update Repository Model:**
```python
class Repository(Base):
    # ... existing fields ...
    last_webhook_received: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    webhook_secret: Mapped[str] = mapped_column(String(200), unique=True)  # For GitHub webhook validation
    auto_reanalyze: Mapped[bool] = mapped_column(default=False)  # Auto-reanalyze on push
    total_commits_analyzed: Mapped[int] = mapped_column(Integer, default=0)
    coverage_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    
    # New relationships
    scar_tissue: Mapped[list["ScarTissuePattern"]] = relationship(cascade="all, delete-orphan")
    bus_factor_alerts: Mapped[list["BusFactorAlert"]] = relationship(cascade="all, delete-orphan")
    analysis_jobs: Mapped[list["AnalysisJob"]] = relationship(cascade="all, delete-orphan")
    onboarding_paths: Mapped[list["OnboardingPath"]] = relationship(cascade="all, delete-orphan")
    webhook_logs: Mapped[list["WebhookLog"]] = relationship(cascade="all, delete-orphan")
```

#### 1.1.3 LLM Integration Service
**New File:** `backend/app/services/llm_analyzer.py`

```python
"""
LLM-powered analysis using free Anthropic API.
Provides intelligent decision extraction, code understanding, and ranking.
"""

from anthropic import Anthropic
from typing import Optional
import json
from datetime import datetime, timezone

class LLMAnalyzer:
    """
    Intelligent analyzer using Claude (Anthropic) for advanced reasoning.
    
    Uses free API with careful rate limiting and caching to maintain zero cost.
    """
    
    def __init__(self):
        self.client = Anthropic()
        self.cache = {}  # Simple file-based cache
        
    def extract_decision_signals(self, commits: list) -> list[dict]:
        """
        Use Claude to deeply analyze commit messages and extract architectural decisions.
        
        Input: Last 200 commits
        Output: High-confidence decision signals with reasoning
        
        Process:
        1. Group commits by theme/component
        2. Identify decision keywords and context
        3. Ask Claude to rank by importance
        4. Extract architectural implications
        """
        # Implementation...
        pass
        
    def analyze_code_patterns(self, repo_path: str, file_contents: dict) -> list[dict]:
        """
        Analyze actual source code for patterns:
        - Error handling patterns
        - Defensive coding (scar tissue)
        - Code duplication and reuse
        - Technology choices and tradeoffs
        """
        # Implementation...
        pass
        
    def generate_knowledge_summary(self, path: str, commits: list) -> str:
        """
        Generate human-readable summary of what changed in each area
        and why those changes matter.
        """
        # Implementation...
        pass
        
    def rank_by_importance(self, signals: list[dict]) -> list[dict]:
        """
        Use Claude to semantically understand and rank signals by importance
        to a new developer onboarding.
        """
        # Implementation...
        pass
```

**Key Features:**
- Batch processing to minimize API calls
- Smart caching of analyses
- Semantic understanding of decisions
- Multi-language support
- Confidence scoring with reasoning

### 1.2 Enhanced Repository Analyzer

**File:** `backend/app/services/analyzer.py`

**Add New Methods:**

```python
def _scar_tissue_detection(self, repo: Repo, commits) -> list[ScarTissueSignal]:
    """
    Identify over-engineered defensive code and trace back to incidents.
    
    Patterns:
    - Multiple validation/checks on same data
    - Retry loops with exponential backoff
    - Fallback/fallthrough logic
    - Try-catch wrapping entire functions
    """
    # Implementation...
    pass

def _incident_correlation(self, commit_messages: list[str]) -> dict:
    """
    Find commit messages mentioning incidents, bugs, crashes, outages.
    Correlate with scar tissue patterns to understand why code is defensive.
    """
    # Implementation...
    pass

def _component_boundaries(self, repo: Repo) -> dict:
    """
    Identify logical components/modules and their integration points.
    Understand how different areas interact.
    """
    # Implementation...
    pass

def _technology_stack_analysis(self, repo: Repo) -> dict:
    """
    Detect framework/library versions and evolution over time.
    Identify deprecated vs. modern patterns.
    """
    # Implementation...
    pass
```

### 1.3 Schemas Update
**File:** `backend/app/schemas.py`

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class ScarTissueSignal(BaseModel):
    pattern_type: str
    file_path: str
    line_numbers: List[int]
    incident_summary: str
    severity: str  # "high" | "medium" | "low"
    confidence: float
    explanation: str

class BusFactorSignal(BaseModel):
    critical_person: str
    areas_affected: List[str]
    concentration_percentage: float
    risk_level: str
    recommendation: str

class OnboardingDay(BaseModel):
    day_number: int
    focus_area: str
    key_concepts: List[str]
    code_locations: List[str]
    estimated_hours: float
    learning_resources: List[str]

class AnalysisOutEnhanced(BaseModel):
    repository_id: int
    owner: str
    repo: str
    analyzed_at: datetime
    decisions: List[Decision]
    ownership: List[KnowledgeOwner]
    ghost_code: List[GhostCodeFinding]
    scar_tissue: List[ScarTissueSignal]
    bus_factor_alerts: List[BusFactorSignal]
    onboarding_paths: List[OnboardingDay]  # For each experience level
    coverage_summary: dict  # Files analyzed, confidence, etc.
```

---

## PHASE 2: INTELLIGENCE LAYERS IMPLEMENTATION (WEEKS 3-4)

### 2.1 Decision Excavation Engine (Layer 1)

**File:** `backend/app/services/decision_engine.py`

```python
"""
Decision Excavation Engine - Reconstruct architectural decisions.

Implements multi-signal analysis:
1. Git commit history parsing
2. PR discussion analysis (via GitHub API)
3. Code change impact analysis
4. LLM-powered semantic understanding
5. Confidence scoring with evidence trails
"""

class DecisionExcavationEngine:
    def __init__(self, llm_analyzer):
        self.llm = llm_analyzer
        self.commit_parser = CommitMessageParser()
        self.github_client = GitHubClient()
        
    def excavate_decisions(self, repo_name: str, owner: str, commits: list) -> list[Decision]:
        """
        Multi-stage decision extraction:
        
        Stage 1: Signal Detection
        - Parse commit messages for decision keywords
        - Extract PR discussions from GitHub
        - Identify architectural changes
        
        Stage 2: Context Gathering
        - Get diff for each identified decision commit
        - Extract affected files and LOC changes
        - Find related PRs and issues
        
        Stage 3: LLM Analysis
        - Send context to Claude for semantic understanding
        - Ask for decision reconstruction
        - Get confidence rating with reasoning
        
        Stage 4: Ranking
        - Rank by importance to new developers
        - Score by controversy/discussion
        - Score by impact (changed LOC, affected areas)
        """
        pass
        
    def _extract_from_pr_discussions(self, owner: str, repo: str) -> list[dict]:
        """
        Use GitHub API to get PR discussions.
        
        Extract:
        - Decision rationale from PR descriptions
        - Discussion outcomes from comments
        - Rejected alternatives mentioned
        """
        pass
```

### 2.2 Ghost Code Explainer (Layer 2)

**File:** `backend/app/services/ghost_code_analyzer.py`

```python
"""
Ghost Code Explainer - Identify and explain dead/abandoned code.

Safety Features:
- Never suggest deletion, only flagging for review
- Provide evidence and confidence levels
- Include runtime references check
- Suggest test coverage analysis
"""

class GhostCodeAnalyzer:
    def __init__(self, llm_analyzer):
        self.llm = llm_analyzer
        
    def find_ghost_code(self, repo: Repo) -> list[GhostCodeFinding]:
        """
        Multi-signal detection:
        1. Staleness (no commits in 6+ months)
        2. Explicit markers (TODO, DEPRECATED, UNUSED, LEGACY)
        3. Dead imports analysis
        4. Unreachable code paths
        5. Orphaned configurations
        
        For each candidate:
        - Gather evidence
        - Check for hidden references
        - Ask LLM for context
        - Score confidence
        """
        pass
        
    def _find_hidden_references(self, repo: Repo, file_path: str) -> list[str]:
        """
        Search for references to this file:
        - Grep through other files
        - Check configuration files
        - Look for dynamic imports/requires
        - Check documentation
        """
        pass
        
    def _explain_safety(self, repo: Repo, file_path: str) -> dict:
        """
        Before flagging as safe to remove:
        1. Check test coverage
        2. Look for integration points
        3. Search dependency tree
        4. Check if used in comments/docs
        """
        pass
```

### 2.3 Scar Tissue Detector (Layer 3)

**File:** `backend/app/services/scar_tissue_detector.py`

```python
"""
Scar Tissue Detector - Find over-engineered defensive code.

Reveals why code is the way it is by tracing back to incidents.
Helps new devs understand defensive patterns in codebase.
"""

class ScarTissueDetector:
    def __init__(self, llm_analyzer):
        self.llm = llm_analyzer
        
    def detect_scar_tissue(self, repo: Repo, commits: list) -> list[ScarTissuePattern]:
        """
        Identify defensive patterns:
        
        1. Retry Loops
           - Code with exponential backoff
           - Max retry limits
           - Often indicates flaky service or external dependency
           
        2. Multiple Validation Layers
           - Same validation repeated
           - Indicates data integrity incidents
           
        3. Fallback Logic
           - Secondary systems/caches
           - Indicates primary system unreliability
           
        4. Try-Catch Wrapping
           - Overly broad exception handling
           - Silent error suppression
           - Indicates previous production issues
        
        For each pattern found:
        - Get git blame to find original commit
        - Search for related incident in commit messages
        - Ask Claude for context
        - Suggest refactoring if safe
        """
        pass
        
    def _correlate_with_incidents(self, pattern_commit: str, commits: list) -> dict:
        """
        Find incident that caused this pattern.
        
        Look in commit messages around time for:
        - BUG, CRASH, OUTAGE keywords
        - Issue references
        - Hotfix mentions
        - Production incident keywords
        """
        pass
```

### 2.4 Tribal Knowledge Extractor (Layer 4)

**File:** `backend/app/services/tribal_knowledge_extractor.py`

```python
"""
Tribal Knowledge Extractor - Map knowledge concentration.

Identifies critical people and flags Bus Factor risks.
Warns before institutional knowledge walks out the door.
"""

class TribalKnowledgeExtractor:
    def __init__(self):
        pass
        
    def extract_knowledge_map(self, commits: list) -> tuple[list[KnowledgeOwner], list[BusFactorAlert]]:
        """
        Build ownership map and identify risks.
        
        For each significant codebase area:
        1. Identify primary authors
        2. Calculate concentration
        3. Cross-check with other signals
           - Who reviews PRs?
           - Who answers questions in issues?
           - Who touched critical paths most recently?
           
        Risk Scoring:
        - High: >75% commits by one person in critical area
        - Medium: >55% commits
        - Low: <55%
        
        Bus Factor Analysis:
        - Identify if person is single point of failure
        - Span multiple components vs. specialized
        - Recent contribution recency
        """
        pass
        
    def _analyze_critical_areas(self, commits: list) -> dict:
        """
        Identify which areas are most critical:
        - Most frequently changed?
        - Most complex?
        - Most impactful when broken?
        - Hardest to maintain?
        """
        pass
        
    def _calculate_bus_factor_risk(self, owner: str, areas: list[str], total_commits: int) -> float:
        """
        Numeric risk score for each person.
        Used to prioritize alerts.
        """
        pass
```

### 2.5 The Oracle (Layer 5)

**File:** `backend/app/services/oracle.py` (Enhanced)

```python
"""
The Oracle - Evidence-backed Q&A system.

Answers any question with citations from git history.
Never guesses - always provides source evidence.
"""

class OracleEnhanced:
    def __init__(self, llm_analyzer, db: Session):
        self.llm = llm_analyzer
        self.db = db
        
    async def answer(self, repository_id: int, question: str, context: str = None) -> tuple[str, list[Evidence]]:
        """
        Answer flow:
        
        1. Intent Detection
           - What is the developer asking about?
           - What level of detail needed?
           - Time period relevant?
           
        2. Evidence Gathering
           - Search decisions
           - Search ownership
           - Search ghost code
           - Search scar tissue
           - Search PRs/issues if available
           
        3. Relevance Ranking
           - Use embeddings to find most relevant signals
           - Score by recency, confidence, impact
           - Get top N most relevant pieces
           
        4. LLM Synthesis
           - Send question + evidence to Claude
           - Ask for synthesized answer with citations
           - Include uncertainty levels
           
        5. Evidence Trail
           - Return specific commits/PRs cited
           - Include links to GitHub
           - Include confidence ratings
        """
        pass
        
    def _gather_evidence(self, repository_id: int, question: str) -> dict:
        """
        Smart evidence gathering using semantic search.
        """
        pass
        
    def _rank_evidence(self, evidence: list[dict], question: str) -> list[dict]:
        """
        Rank evidence by relevance to question.
        """
        pass
```

### 2.6 Personalized Onboarding Journey (Layer 6)

**File:** `backend/app/services/onboarding_journey_generator.py`

```python
"""
Personalized Onboarding Journey - Custom learning paths.

Creates day-by-day learning plan based on:
- Experience level (junior/mid/senior)
- Role (backend/frontend/fullstack/devops)
- Codebase characteristics
"""

class OnboardingJourneyGenerator:
    def __init__(self, llm_analyzer):
        self.llm = llm_analyzer
        
    def generate_journey(self, 
                        repository_id: int, 
                        experience_level: str,  # "junior" | "mid" | "senior"
                        role: str               # "backend" | "frontend" | "fullstack" | "devops"
    ) -> list[OnboardingDay]:
        """
        Generate 5-day onboarding plan.
        
        Day 1: Architecture Overview
        - Key components
        - High-level interactions
        - Technology choices
        
        Day 2: Critical Paths
        - Most changed areas
        - Core business logic
        - Integration points
        
        Day 3: Knowledge Concentration
        - Who knows what
        - Mentorship opportunities
        - Risky areas
        
        Day 4: Defensive Patterns
        - Why code is structured way it is
        - Incident history
        - Reliability patterns
        
        Day 5: Getting Hands-On
        - First PR opportunities
        - Test coverage
        - Development workflow
        """
        pass
        
    def _tailor_by_experience(self, journey: list[OnboardingDay], level: str) -> list[OnboardingDay]:
        """
        Customize complexity and depth based on experience.
        """
        pass
        
    def _tailor_by_role(self, journey: list[OnboardingDay], role: str) -> list[OnboardingDay]:
        """
        Customize focus areas based on role.
        """
        pass
```

---

## PHASE 3: API ENDPOINTS & INTEGRATIONS (WEEKS 5-6)

### 3.1 Enhanced API Endpoints

**File:** `backend/app/main.py` (Add endpoints)

```python
# 1. Analysis Management
@app.post("/api/analyze/advanced", response_model=AnalysisOutEnhanced)
async def analyze_advanced(request: AnalyzeRequest, db: Session = Depends(get_db)):
    """
    Full-featured analysis with all 6 intelligence layers.
    - Uses LLM for semantic understanding
    - Runs in background job
    - Returns job ID for polling
    """
    pass

@app.get("/api/analysis/{repository_id}/job")
async def get_analysis_job(repository_id: int, db: Session = Depends(get_db)):
    """Check status of background analysis job"""
    pass

@app.get("/api/analysis/{repository_id}/scar-tissue")
async def get_scar_tissue(repository_id: int, db: Session = Depends(get_db)):
    """Get detected scar tissue patterns with incident correlation"""
    pass

@app.get("/api/analysis/{repository_id}/bus-factor")
async def get_bus_factor(repository_id: int, db: Session = Depends(get_db)):
    """Get bus factor alerts and knowledge concentration risks"""
    pass

@app.get("/api/analysis/{repository_id}/onboarding/{experience_level}/{role}")
async def get_onboarding_path(
    repository_id: int, 
    experience_level: str,
    role: str,
    db: Session = Depends(get_db)
):
    """Get personalized onboarding journey"""
    pass

# 2. Oracle with Advanced Features
@app.post("/api/oracle/ask")
async def oracle_ask(
    request: QuestionRequest,
    include_evidence: bool = True,
    db: Session = Depends(get_db)
):
    """Ask question with evidence backing"""
    pass

@app.post("/api/oracle/search")
async def oracle_search(
    repository_id: int,
    query: str,
    search_type: str = "semantic",  # "semantic" | "keyword"
    db: Session = Depends(get_db)
):
    """Full-text or semantic search of analysis"""
    pass

# 3. Webhook Management
@app.post("/api/webhooks/github/subscribe")
async def subscribe_webhook(
    request: RepositoryWebhookRequest,
    db: Session = Depends(get_db)
):
    """
    Enable GitHub webhooks for automatic re-analysis.
    
    Returns:
    - Secret for webhook validation
    - Webhook URL to register with GitHub
    """
    pass

@app.post("/api/webhooks/github/event")
async def github_webhook(
    request: Request,
    x_hub_signature: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    Receive GitHub webhook events.
    Validates signature and queues re-analysis if enabled.
    """
    pass

# 4. Repository Management
@app.post("/api/repositories/{repository_id}/reanalyze")
async def reanalyze_repository(repository_id: int, db: Session = Depends(get_db)):
    """Force re-analysis of repository"""
    pass

@app.delete("/api/repositories/{repository_id}")
async def delete_repository(repository_id: int, db: Session = Depends(get_db)):
    """Delete analysis and all related data"""
    pass

@app.get("/api/repositories/{repository_id}/export")
async def export_analysis(repository_id: int, format: str = "json"):
    """Export analysis as JSON or HTML report"""
    pass

# 5. Metrics and Health
@app.get("/api/health/detailed")
async def health_detailed(db: Session = Depends(get_db)):
    """
    Detailed health check including:
    - Database status
    - Queue status
    - LLM API status
    - Last successful analysis
    """
    pass

@app.get("/api/metrics")
async def get_metrics():
    """System metrics for monitoring"""
    pass
```

### 3.2 GitHub Integration

**File:** `backend/app/services/github_client.py`

```python
"""
Enhanced GitHub client with webhook support.
"""

from github import Github
from typing import Optional
import hmac
import hashlib

class GitHubClientEnhanced:
    def __init__(self, token: Optional[str] = None):
        self.github = Github(token) if token else Github()
        
    def get_pr_discussions(self, owner: str, repo: str, limit: int = 50) -> list[dict]:
        """
        Get PR discussions for decision extraction.
        Extract:
        - Decision rationale from descriptions
        - Discussion outcomes
        - Alternative approaches mentioned
        """
        pass
        
    def get_issue_discussions(self, owner: str, repo: str, limit: int = 50) -> list[dict]:
        """
        Get issue discussions.
        Look for:
        - Bug reports with root cause
        - Feature requests with rationale
        - Architecture discussions
        """
        pass
        
    def register_webhook(self, owner: str, repo: str, webhook_url: str, secret: str) -> dict:
        """
        Register webhook with GitHub.
        Events: push, pull_request
        """
        pass
        
    def validate_webhook_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """
        Validate GitHub webhook signature.
        
        GitHub sends: X-Hub-Signature-256: sha256=<hash>
        """
        expected = 'sha256=' + hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature, expected)
```

---

## PHASE 4: FRONTEND ENHANCEMENT (WEEKS 7-8)

### 4.1 Frontend Architecture

**File:** `frontend/src/main.tsx` (Complete Rewrite)

```typescript
/*
Enhanced React frontend with:
- State management (Zustand/Jotai)
- Real-time updates (Server-Sent Events)
- Advanced visualizations (D3.js)
- Responsive design
- Accessibility
*/

import { create } from 'zustand';
import { useQuery, useMutation } from '@tanstack/react-query';

// Global State Management
const useAnalysisStore = create((set) => ({
    currentAnalysis: null,
    repositories: [],
    selectedTab: 'overview',
    
    setCurrentAnalysis: (analysis) => set({ currentAnalysis: analysis }),
    addRepository: (repo) => set((state) => ({
        repositories: [...state.repositories, repo]
    })),
    setSelectedTab: (tab) => set({ selectedTab: tab }),
}));

// Main App Component
export default function App() {
    const [owner, setOwner] = useState('facebook');
    const [repo, setRepo] = useState('react');
    const [branch, setBranch] = useState('');
    
    // Queries
    const analysisQuery = useQuery({
        queryKey: ['analysis', owner, repo, branch],
        queryFn: () => analyze(owner, repo, branch),
        enabled: false,
    });
    
    const repositoriesQuery = useQuery({
        queryKey: ['repositories'],
        queryFn: () => getRepositories(),
        refetchInterval: 30000, // Refresh every 30s
    });
    
    // ... Rest of component
}
```

### 4.2 New UI Components

**File:** `frontend/src/components/`

Create these component files:

```
├── AnalysisHeader.tsx          - Title, timestamp, repo info
├── MetricsGrid.tsx              - 4+ metrics display
├── DecisionCarousel.tsx          - Interactive decision cards
├── OwnershipHeatmap.tsx          - Visual ownership concentration
├── ScarTissuePanel.tsx           - Defensive patterns visualization
├── BusFactorAlert.tsx            - Critical alerts
├── OnboardingJourneyViewer.tsx   - Day-by-day learning path
├── OracleInterface.tsx           - Q&A with evidence sidebar
├── RepositoryHistory.tsx         - Previous analyses
├── AnalysisProgress.tsx          - Real-time job progress
├── ExportDialog.tsx              - Export analysis as HTML/JSON
└── ErrorBoundary.tsx             - Error handling
```

### 4.3 Advanced Visualizations

**File:** `frontend/src/visualizations/`

```typescript
// 1. Knowledge Ownership Heatmap
export function OwnershipHeatmap({ ownership }: { ownership: KnowledgeOwner[] }) {
    /*
    Visual matrix of:
    - X axis: Code areas/components
    - Y axis: Team members
    - Color intensity: Commit concentration
    - Hover: Shows stats and risk level
    */
}

// 2. Decision Timeline
export function DecisionTimeline({ decisions }: { decisions: Decision[] }) {
    /*
    Chronological timeline of architectural decisions.
    Shows:
    - Date
    - Decision title
    - Confidence
    - Links to commits
    */
}

// 3. Scar Tissue Dependency Graph
export function ScarTissueGraph({ scarTissue }: { scarTissue: ScarTissuePattern[] }) {
    /*
    Network graph showing:
    - Code locations
    - Related incidents
    - Pattern types
    - Incident causality
    */
}

// 4. Bus Factor Risk Gauge
export function BusFactorGauge({ alerts }: { alerts: BusFactorAlert[] }) {
    /*
    Radial gauge showing:
    - Overall risk
    - Per-person risk
    - Critical areas
    */
}
```

---

## PHASE 5: QUALITY, TESTING & DEPLOYMENT (WEEKS 9-10)

### 5.1 Testing Strategy

**Backend Tests:**

```python
# File: backend/tests/test_analyzer.py
import pytest
from backend.app.services.analyzer import RepositoryAnalyzer

@pytest.fixture
def analyzer():
    return RepositoryAnalyzer()

def test_decision_extraction(analyzer):
    """Test decision signal extraction from commits"""
    pass

def test_ownership_calculation(analyzer):
    """Test knowledge ownership mapping"""
    pass

def test_ghost_code_detection(analyzer):
    """Test dead code flagging"""
    pass

# File: backend/tests/test_llm_analyzer.py
def test_llm_decision_analysis(mock_anthropic):
    """Test LLM-powered decision analysis"""
    pass

# File: backend/tests/test_oracle.py
def test_oracle_answer_generation(db):
    """Test Oracle Q&A"""
    pass
```

**Frontend Tests:**

```typescript
// File: frontend/tests/main.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import App from '../src/main';

describe('App', () => {
    it('renders analysis form', () => {
        render(<App />);
        expect(screen.getByText('Owner')).toBeInTheDocument();
    });
    
    it('analyzes repository on submit', async () => {
        render(<App />);
        // Test analysis flow
    });
});
```

### 5.2 Error Handling & Resilience

**File:** `backend/app/middleware/error_handler.py`

```python
"""
Comprehensive error handling with user-friendly messages.
"""

class ErrorHandler:
    """
    Handles:
    - Repository not found (404)
    - GitHub API rate limits (429)
    - Timeout (request takes >300s)
    - LLM API failures (fallback to heuristics)
    - Database errors
    - Invalid input
    """
    pass

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Convert exceptions to user-friendly JSON"""
    pass
```

### 5.3 Logging & Monitoring

**File:** `backend/app/middleware/logging.py`

```python
"""
Structured logging for monitoring and debugging.
"""

import structlog
import logging

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Log all API requests, analysis jobs, errors
```

### 5.4 Deployment Configuration

**File:** `docker-compose.prod.yml`

```yaml
version: '3.8'

services:
  backend:
    image: onboarding-archaeologist-backend:latest
    environment:
      ENVIRONMENT: production
      LOG_LEVEL: INFO
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
      GITHUB_TOKEN: ${GITHUB_TOKEN}
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    image: onboarding-archaeologist-frontend:latest
    ports:
      - "3000:3000"
    environment:
      VITE_API_URL: http://backend:8000
```

**Kubernetes Deployment:**

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: onboarding-archaeologist
spec:
  replicas: 3
  selector:
    matchLabels:
      app: onboarding-archaeologist
  template:
    metadata:
      labels:
        app: onboarding-archaeologist
    spec:
      containers:
      - name: backend
        image: onboarding-archaeologist-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        # ... other env vars from secrets
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
```

---

## PHASE 6: DOCUMENTATION & COMMUNITY (WEEKS 11-12)

### 6.1 Developer Documentation

**File:** `docs/ARCHITECTURE.md`

```markdown
# Architecture Guide

## System Overview
[Explain 4-layer architecture]

## Intelligence Layers
[Detail each of the 6 intelligence layers]

## API Reference
[Document all endpoints]

## Development Guide
[Setup, testing, deployment]
```

**File:** `docs/API_REFERENCE.md`

Complete OpenAPI/Swagger documentation with examples.

### 6.2 User Guide

**File:** `docs/USER_GUIDE.md`

- Getting started
- Analyzing a repository
- Interpreting results
- Using the Oracle
- Understanding Bus Factor alerts

### 6.3 Contribution Guidelines

**File:** `CONTRIBUTING.md`

- Code style (Black for Python, Prettier for TypeScript)
- PR process
- Testing requirements
- Commit message format

---

## IMPLEMENTATION CHECKLIST

### Backend Core (Week 1-2)
- [ ] Update configuration system with feature flags
- [ ] Create new database models (scar tissue, bus factor, etc.)
- [ ] Implement LLM analyzer with Anthropic API
- [ ] Add Scar Tissue Detector
- [ ] Add Tribal Knowledge Extractor
- [ ] Add Bus Factor alerting
- [ ] Update schemas for new features
- [ ] Add comprehensive error handling

### Intelligence Layers (Week 3-4)
- [ ] Decision Excavation Engine
- [ ] Ghost Code Explainer with evidence gathering
- [ ] Scar Tissue patterns with incident correlation
- [ ] Knowledge mapping with concentration analysis
- [ ] Oracle enhancement with semantic search
- [ ] Onboarding Journey Generator

### API & Integration (Week 5-6)
- [ ] Add 20+ new API endpoints
- [ ] Implement GitHub client enhancements
- [ ] Add webhook support
- [ ] Add background job queue
- [ ] Add analysis job status tracking
- [ ] Add export functionality
- [ ] Add search capabilities

### Frontend (Week 7-8)
- [ ] Rebuild with React Query for state management
- [ ] Create 12+ new components
- [ ] Add advanced D3.js visualizations
- [ ] Implement real-time updates
- [ ] Add responsive design
- [ ] Add accessibility features
- [ ] Add dark mode

### Quality & Testing (Week 9)
- [ ] Write backend unit tests (50+ tests)
- [ ] Write integration tests
- [ ] Write frontend component tests
- [ ] Add E2E testing
- [ ] Load testing
- [ ] Security testing
- [ ] Test error scenarios

### Documentation & Deployment (Week 10)
- [ ] Write API documentation
- [ ] Write architecture guide
- [ ] Write user guide
- [ ] Create video tutorials
- [ ] Create deployment guide
- [ ] Set up CI/CD pipelines
- [ ] Set up monitoring
- [ ] Prepare for open-source release

---

## KEY CONFIGURATION VALUES

### .env File (Complete)

```bash
# Environment
ENVIRONMENT=production
LOG_LEVEL=INFO

# GitHub
GITHUB_TOKEN=<optional, for private repos>

# Anthropic (FREE API)
ANTHROPIC_API_KEY=<your-key>

# Database
DATABASE_URL=sqlite:///./data/archaeologist.db

# Frontend
VITE_API_URL=http://localhost:8000

# Servers
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
FRONTEND_HOST=0.0.0.0
FRONTEND_PORT=3000

# Analysis
MAX_COMMIT_DEPTH=500
ANALYSIS_TIMEOUT=300
MAX_WORKERS=4

# Queue
QUEUE_TYPE=memory  # Can be "redis" in future

# Cache
CACHE_DIR=./data/cache
CACHE_TTL=86400

# Logging
LOG_FORMAT=json
LOG_FILE=./data/logs/app.log
```

---

## COST ANALYSIS

### Development Cost
- **Total: ₹0** (100% open source)
  - OpenClaw Framework: MIT Licensed
  - LLaMA 3 / CodeLlama: MIT Licensed (if using) OR Anthropic free API tier
  - GitHub API: Free
  - ChromaDB: Open source
  - FastAPI, React, etc.: Open source

### Operating Cost
- **Total: ₹0/month** (Free API tier)
  - Anthropic API: Free tier covers small organizations
  - GitHub API: Free
  - Local LLM or API: Already accounted for
  - Deployment: Can run on any server/cloud free tier

---

## SUCCESS METRICS

**Technical:**
- [ ] All 6 intelligence layers implemented
- [ ] 95%+ test coverage
- [ ] <100ms response time for most queries
- [ ] <5s analysis time for medium repos
- [ ] Zero data loss

**User Experience:**
- [ ] Onboarding time reduced from 3-6 months to 2-4 weeks
- [ ] 90%+ accuracy on decision identification
- [ ] 85%+ accuracy on ghost code detection
- [ ] 100% transparency (all evidence cited)

**Operational:**
- [ ] 99.9% uptime
- [ ] Self-hosted capability
- [ ] Full offline support (except GitHub API)
- [ ] Works with public + private repos

---

## TIMELINE SUMMARY

| Phase | Duration | Focus |
|-------|----------|-------|
| 1 | Weeks 1-2 | Core backend, LLM integration, models |
| 2 | Weeks 3-4 | All 6 intelligence layers |
| 3 | Weeks 5-6 | APIs, GitHub integration, webhooks |
| 4 | Weeks 7-8 | Frontend rebuild, visualizations |
| 5 | Weeks 9-10 | Testing, quality, deployment |
| 6 | Weeks 11-12 | Documentation, community, launch |

**Total: 12 weeks to production-ready system**

---

## NEXT STEPS

1. **Copy this entire document** into your codebase documentation
2. **Create feature branches** for each phase
3. **Set up CI/CD pipeline** for automated testing
4. **Start Phase 1** with backend architecture
5. **Iterate weekly** with working increments
6. **Gather feedback** from real users during Phase 5

This plan maintains **zero cost** while achieving **enterprise quality** through:
- ✅ Free Anthropic API
- ✅ Free GitHub API
- ✅ 100% open-source stack
- ✅ Local-first deployment
- ✅ No vendor lock-in

---

**Document Version:** 1.0  
**Last Updated:** April 26, 2026  
**Status:** Ready for Implementation
