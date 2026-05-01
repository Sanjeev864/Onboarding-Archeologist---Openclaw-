from typing import Dict, Any
from datetime import datetime

class FeedbackProcessor:
    """Processes feedback to improve agent decisions"""
    
    def __init__(self, memory_bank):
        self.memory_bank = memory_bank
        self.feedback_history = []
    
    async def process_feedback(
        self,
        agent_id: str,
        execution_id: str,
        feedback_type: str,  # "positive", "negative", "partial"
        feedback_text: str,
        rating: float = 0.5
    ):
        """
        Process user feedback to adapt future decisions
        
        feedback_type:
            - "positive": agent performed well
            - "negative": agent needs improvement
            - "partial": mixed results
        """
        
        feedback = {
            "agent_id": agent_id,
            "execution_id": execution_id,
            "type": feedback_type,
            "text": feedback_text,
            "rating": rating,  # 0.0 - 1.0
            "timestamp": datetime.now().isoformat()
        }
        
        self.feedback_history.append(feedback)
        
        # Update agent's learned patterns
        if feedback_type == "positive":
            # Reinforce successful patterns
            self._reinforce_pattern(agent_id, rating)
        elif feedback_type == "negative":
            # Adjust decision thresholds
            self._adjust_thresholds(agent_id, rating)
        
        return {"feedback_recorded": True, "agent_adjusted": True}
    
    def _reinforce_pattern(self, agent_id: str, strength: float):
        """Reinforce successful decision patterns"""
        key = f"{agent_id}_confidence_multiplier"
        current = self.memory_bank.long_term.get(key, 1.0)
        # Increase confidence for future decisions (capped at 1.5)
        self.memory_bank.long_term[key] = min(1.5, current + (strength * 0.1))
    
    def _adjust_thresholds(self, agent_id: str, rating: float):
        """Adjust decision thresholds based on negative feedback"""
        key = f"{agent_id}_confidence_threshold"
        current = self.memory_bank.long_term.get(key, 0.5)
        # Increase threshold (be more conservative)
        self.memory_bank.long_term[key] = min(0.9, current + ((1 - rating) * 0.1))
        