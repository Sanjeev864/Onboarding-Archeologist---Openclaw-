from datetime import datetime
from typing import List, Dict, Any
from .base import AutonomousAgent, AgentThought, AgentDecision
from .evidence_agents import (
    RepositoryPerceptionAgent,
    ArchitecturalDecisionAgent,
    OwnershipAnalysisAgent,
    GhostCodeDetectorAgent,
    BusFactorEvaluatorAgent
)

class AnalysisOrchestrationAgent(AutonomousAgent):
    """
    Orchestrates the execution of specialized analysis agents
    Coordinates findings and generates comprehensive reports
    """
    
    def __init__(self):
        super().__init__(
            agent_id="orchestrator-001",
            agent_name="Analysis Orchestration Agent",
            description="Coordinates multi-agent analysis workflow"
        )
        
        # Initialize all specialized agents
        self.perception_agent = RepositoryPerceptionAgent()
        self.decision_agent = ArchitecturalDecisionAgent()
        self.ownership_agent = OwnershipAnalysisAgent()
        self.ghost_code_agent = GhostCodeDetectorAgent()
        self.bus_factor_agent = BusFactorEvaluatorAgent()
        
        self.specialized_agents = [
            self.perception_agent,
            self.decision_agent,
            self.ownership_agent,
            self.ghost_code_agent,
            self.bus_factor_agent
        ]
    
    async def perceive(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perceive analysis request and context"""
        return {
            "request_type": input_data.get("request_type", "full_analysis"),
            "repository": input_data.get("repository"),
            "analysis_scope": input_data.get("analysis_scope", "full"),
            "specialized_agents_available": len(self.specialized_agents)
        }
    
    async def reason(self, perception: Dict[str, Any]) -> AgentThought:
        """Decide on agent deployment strategy"""
        scope = perception["analysis_scope"]
        
        if scope == "full":
            reasoning = "Full analysis requested; activating all specialized agents"
            confidence = 0.95
        elif scope == "quick":
            reasoning = "Quick scan requested; deploying perception and decision agents"
            confidence = 0.9
        else:
            reasoning = f"Custom scope: {scope}; deploying relevant agents"
            confidence = 0.85
        
        return AgentThought(
            step=self.step_count,
            reasoning=reasoning,
            confidence=confidence,
            next_action="deploy_agents",
            alternatives=["parallel_deployment", "sequential_deployment"]
        )
    
    async def decide(self, thought: AgentThought) -> AgentDecision:
        """Decide on deployment strategy"""
        return AgentDecision(
            action_type="coordinate_agents",
            parameters={
                "deployment": "parallel",  # Run agents concurrently
                "error_handling": "continue",  # Don't fail on single agent error
                "aggregate_results": True
            },
            reasoning=thought.reasoning,
            confidence=thought.confidence
        )
    
    async def execute(self, decision: AgentDecision) -> Dict[str, Any]:
        """Execute the coordinated agent analysis"""
        import asyncio
        
        # Run all agents in parallel
        results = {}
        
        agent_tasks = {
            agent.agent_id: agent.run_cycle(self.memory.get("analysis_input"))
            for agent in self.specialized_agents
        }
        
        responses = await asyncio.gather(
            *agent_tasks.values(),
            return_exceptions=True
        )
        
        # Aggregate results
        for (agent_id, task), response in zip(agent_tasks.items(), responses):
            if isinstance(response, Exception):
                results[agent_id] = {"error": str(response)}
            else:
                results[agent_id] = response
        
        # Aggregate findings
        self.memory["aggregated_results"] = {
            "timestamp": datetime.now().isoformat(),
            "agent_results": results,
            "agents_executed": len(self.specialized_agents)
        }
        
        return {
            "orchestration_complete": True,
            "agents_executed": len(self.specialized_agents),
            "results": results
        }


class OnboardingOrchestrationAgent(AutonomousAgent):
    """
    Specializes in generating adaptive onboarding paths
    based on analysis results and learner profile
    """
    
    def __init__(self):
        super().__init__(
            agent_id="onboarding-001",
            agent_name="Onboarding Orchestration Agent",
            description="Generates adaptive onboarding journeys"
        )
    
    async def perceive(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perceive onboarding context"""
        return {
            "learner_level": input_data.get("level", "junior"),
            "analysis_results": input_data.get("analysis"),
            "preferences": input_data.get("preferences", {}),
            "time_available_hours": input_data.get("time_available_hours", 40)
        }
    
    async def reason(self, perception: Dict[str, Any]) -> AgentThought:
        """Reason about onboarding strategy"""
        level = perception["learner_level"]
        time_available = perception["time_available_hours"]
        
        if level == "junior":
            confidence = 0.9
            reasoning = f"Junior level: structured curriculum needed ({time_available}h available)"
        elif level == "mid":
            confidence = 0.85
            reasoning = f"Mid level: focus on patterns and decisions ({time_available}h available)"
        else:
            confidence = 0.8
            reasoning = f"Senior level: deep dives and edge cases ({time_available}h available)"
        
        return AgentThought(
            step=self.step_count,
            reasoning=reasoning,
            confidence=confidence,
            next_action="generate_journey",
            alternatives=["adaptive_path", "self_directed_path"]
        )
    
    async def decide(self, thought: AgentThought) -> AgentDecision:
        """Decide on onboarding approach"""
        return AgentDecision(
            action_type="generate_onboarding",
            parameters={
                "approach": "structured" if "junior" in thought.reasoning else "exploratory",
                "days": 5,
                "include_recommendations": True
            },
            reasoning=thought.reasoning,
            confidence=thought.confidence
        )
    
    async def execute(self, decision: AgentDecision) -> Dict[str, Any]:
        """Generate the onboarding journey"""
        self.memory["onboarding_generated"] = {
            "timestamp": datetime.now().isoformat(),
            "approach": decision.parameters["approach"]
        }
        
        return {
            "onboarding_path_generated": True,
            "approach": decision.parameters["approach"],
            "days": decision.parameters["days"]
        }
