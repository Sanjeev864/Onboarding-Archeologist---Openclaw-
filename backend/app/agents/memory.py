from dataclasses import dataclass, field
from typing import Any, Dict, List
from datetime import datetime
from sqlalchemy import create_engine, Column, String, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

@dataclass
class AgentMemoryBank:
    """Persistent memory for agents"""
    
    short_term: Dict[str, Any] = field(default_factory=dict)  # Current task context
    long_term: Dict[str, Any] = field(default_factory=dict)   # Learned patterns
    episodic: List[Dict[str, Any]] = field(default_factory=list)  # Historical decisions
    
    def record_episode(self, agent_id: str, decision: str, outcome: Any):
        """Record a decision and its outcome for learning"""
        self.episodic.append({
            "agent_id": agent_id,
            "decision": decision,
            "outcome": outcome,
            "timestamp": datetime.now().isoformat()
        })
        
        # If outcome was positive, update long-term patterns
        if outcome.get("success", False):
            pattern_key = f"{agent_id}_success_pattern"
            self.long_term[pattern_key] = {
                "pattern": decision,
                "success_count": self.long_term.get(pattern_key, {}).get("success_count", 0) + 1
            }
    
    def get_relevant_context(self, agent_id: str) -> Dict[str, Any]:
        """Retrieve relevant context for an agent"""
        relevant = {
            "current_context": self.short_term,
            "relevant_patterns": [
                ep for ep in self.episodic[-10:]  # Last 10 decisions
                if ep.get("agent_id") == agent_id
            ]
        }
        return relevant