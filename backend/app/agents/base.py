"""
backend/app/agents/base.py - Base classes for autonomous agents
Ready to copy into your project
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from enum import Enum
from datetime import datetime
import json


class AgentState(Enum):
    """Agent lifecycle states"""
    IDLE = "idle"
    PERCEIVING = "perceiving"
    REASONING = "reasoning"
    DECIDING = "deciding"
    EXECUTING = "executing"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class AgentThought:
    """Represents an agent's reasoning step"""
    step: int
    reasoning: str
    confidence: float
    next_action: str
    alternatives: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class AgentDecision:
    """Represents an agent's concrete decision"""
    action_type: str
    parameters: Dict[str, Any]
    reasoning: str
    confidence: float
    alternatives: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class AutonomousAgent(ABC):
    """
    Base class for all autonomous agents.
    
    Implements the perception-reasoning-decision-execution loop:
    1. PERCEIVE: Extract relevant information from input
    2. REASON: Generate reasoning and confidence scores
    3. DECIDE: Convert reasoning into concrete action
    4. EXECUTE: Carry out the decision
    """
    
    def __init__(self, agent_id: str, agent_name: str, description: str):
        """
        Initialize an autonomous agent.
        
        Args:
            agent_id: Unique identifier for the agent
            agent_name: Human-readable name
            description: Description of agent purpose
        """
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.description = description
        
        # Execution state
        self.state = AgentState.IDLE
        self.step_count = 0
        self.error_count = 0
        
        # Decision history
        self.thoughts: List[AgentThought] = []
        self.decisions: List[AgentDecision] = []
        self.execution_results: List[Dict[str, Any]] = []
        
        # Agent memory
        self.memory: Dict[str, Any] = {}
        
        # Execution trace
        self.trace: List[Dict[str, Any]] = []
    
    @abstractmethod
    async def perceive(self, input_data: Any) -> Dict[str, Any]:
        """
        Perception phase: Process input and extract relevant information.
        
        Args:
            input_data: Raw input data for the agent
            
        Returns:
            Dict containing perceived information
        """
        pass
    
    @abstractmethod
    async def reason(self, perception: Dict[str, Any]) -> AgentThought:
        """
        Reasoning phase: Generate reasoning and confidence scores.
        
        Args:
            perception: Output from perceive() phase
            
        Returns:
            AgentThought with reasoning and confidence
        """
        pass
    
    @abstractmethod
    async def decide(self, thought: AgentThought) -> AgentDecision:
        """
        Decision phase: Convert reasoning into concrete action.
        
        Args:
            thought: Output from reason() phase
            
        Returns:
            AgentDecision with action and parameters
        """
        pass
    
    @abstractmethod
    async def execute(self, decision: AgentDecision) -> Any:
        """
        Execution phase: Carry out the decision.
        
        Args:
            decision: Output from decide() phase
            
        Returns:
            Result of execution
        """
        pass
    
    async def run_cycle(self, input_data: Any) -> Dict[str, Any]:
        """
        Run one complete perception-reasoning-decision-execution cycle.
        
        Args:
            input_data: Input for the agent
            
        Returns:
            Dict with execution results and trace
        """
        self.step_count += 1
        cycle_trace = {
            "step": self.step_count,
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.agent_id,
            "phases": {}
        }
        
        try:
            # PERCEIVE
            self.state = AgentState.PERCEIVING
            perception = await self.perceive(input_data)
            cycle_trace["phases"]["perceive"] = {
                "status": "success",
                "perception_keys": list(perception.keys())
            }
            
            # REASON
            self.state = AgentState.REASONING
            thought = await self.reason(perception)
            self.thoughts.append(thought)
            cycle_trace["phases"]["reason"] = {
                "status": "success",
                "confidence": thought.confidence,
                "reasoning": thought.reasoning[:100] + "..." if len(thought.reasoning) > 100 else thought.reasoning
            }
            
            # DECIDE
            self.state = AgentState.DECIDING
            decision = await self.decide(thought)
            self.decisions.append(decision)
            cycle_trace["phases"]["decide"] = {
                "status": "success",
                "action_type": decision.action_type,
                "confidence": decision.confidence
            }
            
            # EXECUTE
            self.state = AgentState.EXECUTING
            result = await self.execute(decision)
            self.execution_results.append(result)
            cycle_trace["phases"]["execute"] = {
                "status": "success",
                "result_type": type(result).__name__
            }
            
            self.state = AgentState.COMPLETE
            cycle_trace["final_state"] = "complete"
            
        except Exception as e:
            self.state = AgentState.ERROR
            self.error_count += 1
            cycle_trace["final_state"] = "error"
            cycle_trace["error"] = str(e)
            raise
        
        finally:
            self.trace.append(cycle_trace)
        
        return {
            "step": self.step_count,
            "state": self.state.value,
            "result": result if 'result' in locals() else None,
            "trace": cycle_trace
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of agent execution.
        
        Returns:
            Dict with execution summary
        """
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "description": self.description,
            "state": self.state.value,
            "steps_executed": self.step_count,
            "errors": self.error_count,
            "thoughts_count": len(self.thoughts),
            "decisions_count": len(self.decisions),
            "execution_results_count": len(self.execution_results),
            "last_thought": self.thoughts[-1].to_dict() if self.thoughts else None,
            "last_decision": self.decisions[-1].to_dict() if self.decisions else None,
            "memory_keys": list(self.memory.keys())
        }
    
    def get_decision_trace(self) -> List[Dict[str, Any]]:
        """
        Get full trace of reasoning and decisions.
        
        Returns:
            List of decision steps with reasoning
        """
        trace = []
        
        for i, (thought, decision, result) in enumerate(
            zip(self.thoughts, self.decisions, self.execution_results)
        ):
            trace.append({
                "step": i + 1,
                "thought": {
                    "reasoning": thought.reasoning,
                    "confidence": thought.confidence,
                    "alternatives": thought.alternatives
                },
                "decision": {
                    "action_type": decision.action_type,
                    "parameters": decision.parameters,
                    "reasoning": decision.reasoning
                },
                "execution": {
                    "result_type": type(result).__name__,
                    "success": result.get("success", False) if isinstance(result, dict) else True
                }
            })
        
        return trace
    
    def get_execution_trace(self) -> List[Dict[str, Any]]:
        """
        Get detailed execution trace for debugging.
        
        Returns:
            List of all execution events
        """
        return self.trace
    
    def export_analysis(self) -> Dict[str, Any]:
        """
        Export complete agent analysis for persistence.
        
        Returns:
            Dict with all agent data
        """
        return {
            "agent_metadata": {
                "agent_id": self.agent_id,
                "agent_name": self.agent_name,
                "description": self.description,
                "exported_at": datetime.now().isoformat()
            },
            "execution_summary": self.get_summary(),
            "decision_trace": self.get_decision_trace(),
            "execution_trace": self.get_execution_trace(),
            "memory": self.memory,
            "final_state": self.state.value
        }


class MultiAgentOrchestrator(ABC):
    """
    Base class for orchestrating multiple agents.
    Manages agent coordination, error handling, and result aggregation.
    """
    
    def __init__(self, orchestrator_id: str, name: str):
        """
        Initialize the orchestrator.
        
        Args:
            orchestrator_id: Unique orchestrator identifier
            name: Orchestrator name
        """
        self.orchestrator_id = orchestrator_id
        self.name = name
        self.agents: Dict[str, AutonomousAgent] = {}
        self.execution_history: List[Dict[str, Any]] = []
    
    def register_agent(self, agent: AutonomousAgent) -> None:
        """
        Register an agent with the orchestrator.
        
        Args:
            agent: Agent to register
        """
        self.agents[agent.agent_id] = agent
    
    def register_agents(self, agents: List[AutonomousAgent]) -> None:
        """
        Register multiple agents.
        
        Args:
            agents: List of agents to register
        """
        for agent in agents:
            self.register_agent(agent)
    
    async def run_sequential(
        self,
        input_data: Any,
        agent_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Run agents sequentially, passing output to next agent.
        
        Args:
            input_data: Initial input
            agent_ids: List of agent IDs (if None, use all)
            
        Returns:
            Dict with execution results
        """
        agents_to_run = agent_ids or list(self.agents.keys())
        results = {}
        current_input = input_data
        
        for agent_id in agents_to_run:
            agent = self.agents.get(agent_id)
            if not agent:
                results[agent_id] = {"error": "Agent not found"}
                continue
            
            try:
                result = await agent.run_cycle(current_input)
                results[agent_id] = result
                current_input = result  # Pass output to next agent
            except Exception as e:
                results[agent_id] = {"error": str(e)}
        
        execution_record = {
            "timestamp": datetime.now().isoformat(),
            "mode": "sequential",
            "agents_run": len(agents_to_run),
            "results": results
        }
        self.execution_history.append(execution_record)
        
        return results
    
    async def run_parallel(
        self,
        input_data: Any,
        agent_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Run agents in parallel.
        
        Args:
            input_data: Input for all agents
            agent_ids: List of agent IDs (if None, use all)
            
        Returns:
            Dict with execution results
        """
        import asyncio
        
        agents_to_run = agent_ids or list(self.agents.keys())
        tasks = {}
        
        for agent_id in agents_to_run:
            agent = self.agents.get(agent_id)
            if agent:
                tasks[agent_id] = agent.run_cycle(input_data)
        
        # Run all tasks concurrently
        results = await asyncio.gather(
            *tasks.values(),
            return_exceptions=True
        )
        
        # Map results back to agent IDs
        execution_results = {}
        for agent_id, result in zip(tasks.keys(), results):
            if isinstance(result, Exception):
                execution_results[agent_id] = {"error": str(result)}
            else:
                execution_results[agent_id] = result
        
        execution_record = {
            "timestamp": datetime.now().isoformat(),
            "mode": "parallel",
            "agents_run": len(agents_to_run),
            "results": execution_results
        }
        self.execution_history.append(execution_record)
        
        return execution_results
    
    def get_agents_summary(self) -> Dict[str, Any]:
        """
        Get summary of all registered agents.
        
        Returns:
            Dict with agent summaries
        """
        return {
            agent_id: agent.get_summary()
            for agent_id, agent in self.agents.items()
        }
    
    def get_orchestration_summary(self) -> Dict[str, Any]:
        """
        Get summary of orchestration execution.
        
        Returns:
            Dict with orchestration summary
        """
        return {
            "orchestrator_id": self.orchestrator_id,
            "name": self.name,
            "agents_registered": len(self.agents),
            "executions": len(self.execution_history),
            "agents": self.get_agents_summary(),
            "execution_history": self.execution_history[-5:]  # Last 5 executions
        }