"""
backend/app/agents/evidence_agents.py - Concrete agent implementations
Specialized agents for your analyzer services
Ready to copy into your project
"""

from typing import Any, Dict, List
from datetime import datetime
from .base import AutonomousAgent, AgentThought, AgentDecision
from ..services.agent_services import analyzer_service, oracle_service, github_service


class RepositoryPerceptionAgent(AutonomousAgent):
    """
    Initial perception agent - understands repository structure and context.
    Extracts metadata and prepares for deep analysis.
    """
    
    def __init__(self):
        super().__init__(
            agent_id="repo-perception-001",
            agent_name="Repository Perception Agent",
            description="Analyzes repository structure and context"
        )
    
    async def perceive(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract repository metadata and initial signals.
        
        Example input:
        {
            "owner": "anthropic",
            "repo": "claude-code",
            "repo_path": "/tmp/repo",
            "analysis_scope": "full"
        }
        """
        return {
            "owner": input_data.get("owner", "unknown"),
            "repo_name": input_data.get("repo", "unknown"),
            "repo_path": input_data.get("repo_path"),
            "analysis_scope": input_data.get("analysis_scope", "full"),
            "timestamp": datetime.now().isoformat()
        }
    
    async def reason(self, perception: Dict[str, Any]) -> AgentThought:
        """
        Generate reasoning about repository state and analysis readiness.
        """
        owner = perception["owner"]
        repo = perception["repo_name"]
        scope = perception["analysis_scope"]
        
        reasoning = f"Repository {owner}/{repo} ready for {scope} analysis"
        confidence = 0.95 if perception["repo_path"] else 0.7
        
        return AgentThought(
            step=self.step_count,
            reasoning=reasoning,
            confidence=confidence,
            next_action="extract_signals",
            alternatives=["quick_scan", "incremental_analysis"]
        )
    
    async def decide(self, thought: AgentThought) -> AgentDecision:
        """
        Decide on analysis strategy based on confidence.
        """
        strategy = "full" if thought.confidence > 0.9 else "partial"
        
        return AgentDecision(
            action_type="initiate_analysis",
            parameters={
                "strategy": strategy,
                "depth": "comprehensive" if strategy == "full" else "focused"
            },
            reasoning=thought.reasoning,
            confidence=thought.confidence
        )
    
    async def execute(self, decision: AgentDecision) -> Dict[str, Any]:
        """
        Initialize analysis workflow.
        """
        self.memory["analysis_initiated"] = {
            "strategy": decision.parameters["strategy"],
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "status": "ready",
            "strategy": decision.parameters["strategy"],
            "success": True
        }
async def execute(self, decision: AgentDecision) -> Dict[str, Any]:
    """Execute using real GitHub and analyzer data"""
    try:
        # Get real repository info from GitHub
        repo_info = await github_service.get_repository_info(
            self.memory.get("owner", "unknown"),
            self.memory.get("repo", "unknown")
        )
        
        # Get real analysis
        analysis = await analyzer_service.analyze_repository(
            owner=self.memory.get("owner"),
            repo=self.memory.get("repo"),
            path=self.memory.get("repo_path"),
            deep=decision.parameters.get("depth") == "comprehensive"
        )
        
        self.memory["repository_info"] = repo_info
        self.memory["analysis_results"] = analysis
        
        return {
            "status": "ready",
            "strategy": decision.parameters["strategy"],
            "repository_info": repo_info,
            "analysis_ready": bool(analysis),
            "success": True
        }
    except Exception as e:
        logger.error(f"Real data fetch failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "fallback_to_mock": True,
            "success": False
        }



class ArchitecturalDecisionAgent(AutonomousAgent):
    """
    Identifies and evaluates architectural decisions from git history.
    Extracts decision signals and generates confidence scores.
    """
    
    def __init__(self):
        super().__init__(
            agent_id="arch-decision-001",
            agent_name="Architectural Decision Agent",
            description="Identifies and evaluates architectural decisions"
        )
        
        # Decision signal patterns (from your analyzer.py DECISION_TERMS)
        self.decision_keywords = {
            "because", "decided", "decision", "tradeoff", "migrate",
            "replace", "remove", "deprecate", "security", "performance",
            "refactor", "workaround", "fix"
        }
    
    async def perceive(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract decision signals from analysis results.
        """
        decisions = input_data.get("decisions", [])
        
        return {
            "raw_decisions": decisions,
            "decision_count": len(decisions),
            "high_confidence": [d for d in decisions if d.get("confidence", 0) > 0.8],
            "avg_confidence": (
                sum(d.get("confidence", 0) for d in decisions) / len(decisions)
                if decisions else 0.0
            ),
            "timestamp": datetime.now().isoformat()
        }
    
    async def reason(self, perception: Dict[str, Any]) -> AgentThought:
        """
        Reason about decision significance and confidence.
        """
        count = perception["decision_count"]
        avg_conf = perception["avg_confidence"]
        
        if count == 0:
            reasoning = "No explicit decisions found; may require inference"
            confidence = 0.4
        elif count > 10:
            reasoning = f"Strong decision signal: {count} decisions identified"
            confidence = min(0.95, 0.7 + (count * 0.02))
        else:
            reasoning = f"Moderate decision signal: {count} decisions"
            confidence = 0.7
        
        return AgentThought(
            step=self.step_count,
            reasoning=reasoning,
            confidence=confidence,
            next_action="evaluate_decisions",
            alternatives=["infer_implicit_decisions", "focus_recent_decisions"]
        )
    
    async def decide(self, thought: AgentThought) -> AgentDecision:
        """
        Decide on decision extraction strategy.
        """
        min_confidence = 0.7 if thought.confidence > 0.75 else 0.5
        
        return AgentDecision(
            action_type="extract_decisions",
            parameters={
                "min_confidence_threshold": min_confidence,
                "rank_by_recency": True,
                "include_inferred": thought.confidence < 0.6
            },
            reasoning=thought.reasoning,
            confidence=thought.confidence
        )
    
    async def execute(self, decision: AgentDecision) -> Dict[str, Any]:
        """
        Execute decision extraction.
        """
        self.memory["decisions_extracted"] = {
            "threshold": decision.parameters["min_confidence_threshold"],
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "extraction_complete": True,
            "threshold": decision.parameters["min_confidence_threshold"],
            "success": True
        }
async def execute(self, decision: AgentDecision) -> Dict[str, Any]:
    """Execute decision extraction with real analyzer"""
    try:
        analysis = self.memory.get("analysis_results", {})
        
        # Extract decisions using real analyzer
        decisions = await analyzer_service.extract_decisions(analysis)
        
        self.memory["decisions_extracted"] = {
            "count": len(decisions),
            "threshold": decision.parameters["min_confidence_threshold"],
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "extraction_complete": True,
            "decisions_found": len(decisions),
            "threshold": decision.parameters["min_confidence_threshold"],
            "success": True
        }
    except Exception as e:
        logger.error(f"Decision extraction failed: {str(e)}")
        return {"extraction_complete": False, "success": False, "error": str(e)}


class OwnershipAnalysisAgent(AutonomousAgent):
    """
    Analyzes code ownership patterns and concentration risks.
    Identifies single points of failure (bus factor).
    """
    
    def __init__(self):
        super().__init__(
            agent_id="ownership-001",
            agent_name="Ownership Analysis Agent",
            description="Analyzes ownership patterns and concentration risks"
        )
    
    async def perceive(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract ownership signals.
        """
        ownership = input_data.get("ownership", [])
        
        high_risk = [o for o in ownership if o.get("risk") == "high"]
        medium_risk = [o for o in ownership if o.get("risk") == "medium"]
        
        total_concentration = sum(
            o.get("concentration_percentage", 0) for o in ownership
        ) / len(ownership) if ownership else 0
        
        return {
            "ownership_signals": ownership,
            "high_risk_count": len(high_risk),
            "medium_risk_count": len(medium_risk),
            "total_paths": len(ownership),
            "avg_concentration_percent": total_concentration,
            "timestamp": datetime.now().isoformat()
        }
    
    async def reason(self, perception: Dict[str, Any]) -> AgentThought:
        """
        Reason about concentration risks and their severity.
        """
        high_risk = perception["high_risk_count"]
        avg_concentration = perception["avg_concentration_percent"]
        
        if high_risk > 0:
            reasoning = f"CRITICAL: {high_risk} high-risk areas detected"
            confidence = 0.95
            severity = "critical"
        elif avg_concentration > 60:
            reasoning = f"HIGH: {avg_concentration:.0f}% average concentration"
            confidence = 0.85
            severity = "high"
        else:
            reasoning = "MODERATE: Healthy ownership distribution"
            confidence = 0.7
            severity = "medium"
        
        return AgentThought(
            step=self.step_count,
            reasoning=reasoning,
            confidence=confidence,
            next_action="generate_recommendations",
            alternatives=["escalate_critical", "plan_mitigation"]
        )
    
    async def decide(self, thought: AgentThought) -> AgentDecision:
        """
        Decide on mitigation strategy.
        """
        return AgentDecision(
            action_type="analyze_ownership",
            parameters={
                "generate_recommendations": True,
                "severity_threshold": "high" if thought.confidence > 0.8 else "medium",
                "include_mitigation_plan": thought.confidence > 0.8
            },
            reasoning=thought.reasoning,
            confidence=thought.confidence
        )
    
    async def execute(self, decision: AgentDecision) -> Dict[str, Any]:
        """
        Execute ownership analysis.
        """
        self.memory["ownership_analyzed"] = {
            "severity_threshold": decision.parameters["severity_threshold"],
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "analysis_complete": True,
            "severity_threshold": decision.parameters["severity_threshold"],
            "success": True
        }


class GhostCodeDetectorAgent(AutonomousAgent):
    """
    Identifies ghost code (unused, deprecated, stale code).
    Provides cleanup recommendations with safety-first approach.
    """
    
    def __init__(self):
        super().__init__(
            agent_id="ghost-code-001",
            agent_name="Ghost Code Detector Agent",
            description="Identifies stale and unused code candidates"
        )
    
    async def perceive(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract ghost code signals.
        """
        ghost_code = input_data.get("ghost_code", [])
        
        high_confidence = [
            g for g in ghost_code
            if g.get("confidence", 0) > 0.8
        ]
        
        avg_staleness = (
            sum(g.get("last_touched_days", 0) for g in ghost_code) / len(ghost_code)
            if ghost_code else 0
        )
        
        return {
            "ghost_code_findings": ghost_code,
            "high_confidence_count": len(high_confidence),
            "findings_count": len(ghost_code),
            "avg_staleness_days": int(avg_staleness),
            "timestamp": datetime.now().isoformat()
        }
    
    async def reason(self, perception: Dict[str, Any]) -> AgentThought:
        """
        Reason about cleanup opportunities and urgency.
        """
        high_conf = perception["high_confidence_count"]
        findings = perception["findings_count"]
        staleness = perception["avg_staleness_days"]
        
        if high_conf > 5 and staleness > 365:
            reasoning = f"Strong candidates: {high_conf} high-confidence, avg {staleness} days old"
            confidence = 0.85
        elif high_conf > 0:
            reasoning = f"Candidates identified: {high_conf} high-confidence items"
            confidence = 0.7
        else:
            reasoning = "Limited cleanup candidates identified"
            confidence = 0.4
        
        return AgentThought(
            step=self.step_count,
            reasoning=reasoning,
            confidence=confidence,
            next_action="generate_cleanup_plan",
            alternatives=["defer_review", "manual_investigation"]
        )
    
    async def decide(self, thought: AgentThought) -> AgentDecision:
        """
        Decide on cleanup approach (safety-first).
        """
        return AgentDecision(
            action_type="detect_ghost_code",
            parameters={
                "confidence_threshold": 0.75,
                "generate_cleanup_plan": thought.confidence > 0.6,
                "safety_first": True,  # Never auto-delete
                "require_human_review": thought.confidence < 0.8
            },
            reasoning=thought.reasoning,
            confidence=thought.confidence
        )
    
    async def execute(self, decision: AgentDecision) -> Dict[str, Any]:
        """
        Execute ghost code detection.
        """
        self.memory["ghost_code_detected"] = {
            "threshold": decision.parameters["confidence_threshold"],
            "requires_review": decision.parameters["require_human_review"],
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "detection_complete": True,
            "safety_first_mode": decision.parameters["safety_first"],
            "success": True
        }
async def execute(self, decision: AgentDecision) -> Dict[str, Any]:
    """Execute ghost code detection with real analyzer"""
    try:
        analysis = self.memory.get("analysis_results", {})
        
        # Detect ghost code using real analyzer
        ghost_code = await analyzer_service.detect_ghost_code(analysis)
        
        self.memory["ghost_code_detected"] = {
            "candidates_found": len(ghost_code),
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "detection_complete": True,
            "candidates_found": len(ghost_code),
            "success": True
        }
    except Exception as e:
        return {"detection_complete": False, "success": False, "error": str(e)}



class BusFactorEvaluatorAgent(AutonomousAgent):
    """
    Evaluates bus factor (single points of failure).
    Assesses knowledge concentration risks and provides recommendations.
    """
    
    def __init__(self):
        super().__init__(
            agent_id="bus-factor-001",
            agent_name="Bus Factor Evaluator Agent",
            description="Assesses knowledge concentration and single-person risks"
        )
    
    async def perceive(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract bus factor signals.
        """
        alerts = input_data.get("bus_factor_alerts", [])
        
        critical = [a for a in alerts if a.get("risk_level") == "CRITICAL"]
        high = [a for a in alerts if a.get("risk_level") == "HIGH"]
        
        avg_concentration = (
            sum(a.get("concentration_percentage", 0) for a in alerts) / len(alerts)
            if alerts else 0.0
        )
        
        return {
            "alerts": alerts,
            "critical_count": len(critical),
            "high_count": len(high),
            "total_alerts": len(alerts),
            "avg_concentration_percent": avg_concentration,
            "timestamp": datetime.now().isoformat()
        }
    
    async def reason(self, perception: Dict[str, Any]) -> AgentThought:
        """
        Reason about bus factor severity.
        """
        critical = perception["critical_count"]
        high = perception["high_count"]
        avg_concentration = perception["avg_concentration_percent"]
        
        if critical > 0:
            reasoning = f"CRITICAL RISK: {critical} single points of failure"
            confidence = 0.95
            severity = "critical"
        elif high > 0 or avg_concentration > 70:
            reasoning = f"HIGH RISK: {high} high-risk areas, {avg_concentration:.0f}% concentration"
            confidence = 0.9
            severity = "high"
        else:
            reasoning = "MODERATE: Acceptable risk distribution"
            confidence = 0.7
            severity = "moderate"
        
        return AgentThought(
            step=self.step_count,
            reasoning=reasoning,
            confidence=confidence,
            next_action="generate_mitigation",
            alternatives=["escalate_to_leadership", "create_knowledge_plan"]
        )
    
    async def decide(self, thought: AgentThought) -> AgentDecision:
        """
        Decide on risk response strategy.
        """
        return AgentDecision(
            action_type="evaluate_bus_factor",
            parameters={
                "generate_recommendations": True,
                "escalation_needed": thought.confidence > 0.9,
                "timeline_urgent": thought.confidence > 0.85,
                "mitigation_strategies": [
                    "knowledge_transfer",
                    "documentation",
                    "team_building"
                ]
            },
            reasoning=thought.reasoning,
            confidence=thought.confidence
        )
    
    async def execute(self, decision: AgentDecision) -> Dict[str, Any]:
        """
        Execute bus factor evaluation.
        """
        self.memory["bus_factor_evaluated"] = {
            "escalation_needed": decision.parameters["escalation_needed"],
            "timeline": "URGENT" if decision.parameters["timeline_urgent"] else "30-90 days",
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "evaluation_complete": True,
            "escalation_needed": decision.parameters["escalation_needed"],
            "success": True
        }
async def execute(self, decision: AgentDecision) -> Dict[str, Any]:
    """Execute bus factor evaluation with real analyzer"""
    try:
        ownership = self.memory.get("ownership_analyzed", {})
        
        # Evaluate bus factor using real analyzer
        alerts = await analyzer_service.evaluate_bus_factor(
            self.memory.get("analysis_results", {})
        )
        
        self.memory["bus_factor_evaluated"] = {
            "alerts_found": len(alerts),
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "evaluation_complete": True,
            "alerts_found": len(alerts),
            "success": True
        }
    except Exception as e:
        return {"evaluation_complete": False, "success": False, "error": str(e)}


class ScarTissueAnalyzerAgent(AutonomousAgent):
    """
    Detects scar tissue patterns (code marked by incidents/struggles).
    Identifies areas requiring careful handling and extra testing.
    """
    
    def __init__(self):
        super().__init__(
            agent_id="scar-tissue-001",
            agent_name="Scar Tissue Analyzer Agent",
            description="Identifies incident-related code patterns"
        )
    
    async def perceive(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract scar tissue signals.
        """
        scars = input_data.get("scar_tissue", [])
        
        critical = [s for s in scars if s.get("severity") == "critical"]
        high = [s for s in scars if s.get("severity") == "high"]
        
        return {
            "scar_findings": scars,
            "critical_count": len(critical),
            "high_count": len(high),
            "total_findings": len(scars),
            "timestamp": datetime.now().isoformat()
        }
    
    async def reason(self, perception: Dict[str, Any]) -> AgentThought:
        """
        Reason about scar tissue severity and testing needs.
        """
        critical = perception["critical_count"]
        high = perception["high_count"]
        total = perception["total_findings"]
        
        if critical > 0:
            reasoning = f"CRITICAL: {critical} high-severity incident areas detected"
            confidence = 0.95
        elif high > 0:
            reasoning = f"HIGH: {high} medium-severity areas; extra testing needed"
            confidence = 0.85
        elif total > 0:
            reasoning = f"MODERATE: {total} incident-related areas to review"
            confidence = 0.7
        else:
            reasoning = "No significant scar tissue patterns detected"
            confidence = 0.5
        
        return AgentThought(
            step=self.step_count,
            reasoning=reasoning,
            confidence=confidence,
            next_action="recommend_testing_strategy",
            alternatives=["defer_review", "schedule_audit"]
        )
    
    async def decide(self, thought: AgentThought) -> AgentDecision:
        """
        Decide on testing and review strategy.
        """
        return AgentDecision(
            action_type="analyze_scar_tissue",
            parameters={
                "recommend_extra_testing": thought.confidence > 0.7,
                "testing_priority": "high" if thought.confidence > 0.85 else "medium",
                "include_regression_tests": thought.confidence > 0.75
            },
            reasoning=thought.reasoning,
            confidence=thought.confidence
        )
    
    async def execute(self, decision: AgentDecision) -> Dict[str, Any]:
        """
        Execute scar tissue analysis.
        """
        self.memory["scar_tissue_analyzed"] = {
            "testing_priority": decision.parameters["testing_priority"],
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "analysis_complete": True,
            "testing_priority": decision.parameters["testing_priority"],
            "success": True
        }


class OnboardingPathGeneratorAgent(AutonomousAgent):
    """
    Generates personalized onboarding paths based on analysis findings.
    Adapts to learner level and available time.
    """
    
    def __init__(self):
        super().__init__(
            agent_id="onboarding-001",
            agent_name="Onboarding Path Generator Agent",
            description="Creates adaptive onboarding journeys"
        )
    
    async def perceive(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract onboarding context.
        """
        return {
            "learner_level": input_data.get("level", "junior"),
            "analysis_findings": input_data.get("analysis", {}),
            "time_available_hours": input_data.get("time_available_hours", 40),
            "preferences": input_data.get("preferences", {}),
            "timestamp": datetime.now().isoformat()
        }
    
    async def reason(self, perception: Dict[str, Any]) -> AgentThought:
        """
        Reason about optimal onboarding strategy.
        """
        level = perception["learner_level"]
        time_hours = perception["time_available_hours"]
        
        level_strategy_map = {
            "junior": ("structured_curriculum", 0.9),
            "mid": ("guided_exploration", 0.85),
            "senior": ("deep_dives", 0.8)
        }
        
        strategy, confidence = level_strategy_map.get(level, ("adaptive", 0.75))
        reasoning = f"Onboarding for {level} with {time_hours}h available: {strategy}"
        
        return AgentThought(
            step=self.step_count,
            reasoning=reasoning,
            confidence=confidence,
            next_action="generate_path",
            alternatives=["accelerated_path", "self_directed_path"]
        )
    
    async def decide(self, thought: AgentThought) -> AgentDecision:
        """
        Decide on specific path components.
        """
        return AgentDecision(
            action_type="generate_onboarding_path",
            parameters={
                "days": 5,
                "daily_hours": 8,
                "include_exercises": thought.confidence > 0.8,
                "include_recommendations": True
            },
            reasoning=thought.reasoning,
            confidence=thought.confidence
        )
    
    async def execute(self, decision: AgentDecision) -> Dict[str, Any]:
        """
        Generate the onboarding path.
        """
        self.memory["path_generated"] = {
            "days": decision.parameters["days"],
            "daily_hours": decision.parameters["daily_hours"],
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "path_generated": True,
            "days": decision.parameters["days"],
            "success": True
        }