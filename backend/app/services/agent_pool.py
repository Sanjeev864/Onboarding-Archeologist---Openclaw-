"""
agent_pool.py - Agent pooling for concurrent requests
Reuse agent instances to avoid initialization overhead
"""

import asyncio
from typing import Dict, Any, Type
import logging

logger = logging.getLogger(__name__)


class AgentPool:
    """Pool of reusable agent instances"""
    
    def __init__(self, agent_class: Type, pool_size: int = 3):
        """Initialize agent pool"""
        self.agent_class = agent_class
        self.pool_size = pool_size
        self.available_agents = [agent_class() for _ in range(pool_size)]
        self.in_use_count = 0
        self.total_uses = 0
    
    async def acquire(self):
        """Get an agent from pool"""
        # Wait if no agents available
        while not self.available_agents:
            await asyncio.sleep(0.1)
        
        agent = self.available_agents.pop()
        self.in_use_count += 1
        self.total_uses += 1
        
        logger.debug(f"Agent acquired. In use: {self.in_use_count}/{self.pool_size}")
        return agent
    
    def release(self, agent):
        """Return agent to pool"""
        # Reset agent state for reuse
        agent.memory.clear()
        agent.step_count = 0
        agent.error_count = 0
        
        self.available_agents.append(agent)
        self.in_use_count -= 1
        
        logger.debug(f"Agent released. In use: {self.in_use_count}/{self.pool_size}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics"""
        return {
            "agent_class": self.agent_class.__name__,
            "pool_size": self.pool_size,
            "available": len(self.available_agents),
            "in_use": self.in_use_count,
            "total_uses": self.total_uses
        }


# Create pools for each agent type
from .agents.evidence_agents import (
    RepositoryPerceptionAgent,
    ArchitecturalDecisionAgent,
    OwnershipAnalysisAgent,
    GhostCodeDetectorAgent,
    BusFactorEvaluatorAgent,
    ScarTissueAnalyzerAgent,
    OnboardingPathGeneratorAgent
)

perception_pool = AgentPool(RepositoryPerceptionAgent, pool_size=3)
decision_pool = AgentPool(ArchitecturalDecisionAgent, pool_size=3)
ownership_pool = AgentPool(OwnershipAnalysisAgent, pool_size=3)
ghost_code_pool = AgentPool(GhostCodeDetectorAgent, pool_size=3)
bus_factor_pool = AgentPool(BusFactorEvaluatorAgent, pool_size=3)
scar_tissue_pool = AgentPool(ScarTissueAnalyzerAgent, pool_size=3)
onboarding_pool = AgentPool(OnboardingPathGeneratorAgent, pool_size=3)


class PoolManager:
    """Manages all agent pools"""
    
    pools = {
        "perception": perception_pool,
        "decisions": decision_pool,
        "ownership": ownership_pool,
        "ghost_code": ghost_code_pool,
        "bus_factor": bus_factor_pool,
        "scar_tissue": scar_tissue_pool,
        "onboarding": onboarding_pool
    }
    
    @staticmethod
    def get_stats() -> Dict[str, Any]:
        """Get stats for all pools"""
        return {
            name: pool.get_stats()
            for name, pool in PoolManager.pools.items()
        }