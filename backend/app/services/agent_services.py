"""
agent_services.py - Integration layer between agents and existing services
Wraps your existing services for use by autonomous agents
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class AnalyzerServiceWrapper:
    """Wraps your existing analyzer.py for agent use"""
    
    def __init__(self):
        """Initialize wrapper with your existing analyzer"""
        try:
            from .analyzer import RepositoryAnalyzer
            self.analyzer = RepositoryAnalyzer()
            self.available = True
        except ImportError:
            logger.warning("RepositoryAnalyzer not available, using mock")
            self.available = False
    
    async def analyze_repository(
        self,
        owner: str,
        repo: str,
        path: Optional[str] = None,
        deep: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze repository using your existing analyzer
        
        Returns structured analysis data for agents
        """
        if not self.available:
            return self._mock_analysis(owner, repo)
        
        try:
            # Call your existing analyzer
            analysis = self.analyzer.analyze(
                owner=owner,
                repo=repo,
                path=path,
                deep_analysis=deep
            )
            
            logger.info(f"✓ Real analysis completed: {owner}/{repo}")
            return analysis
        
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}, using mock data")
            return self._mock_analysis(owner, repo)
    
    async def extract_decisions(self, code_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract architectural decisions from code analysis"""
        if not self.available:
            return self._mock_decisions()
        
        try:
            decisions = self.analyzer.extract_decisions(code_data)
            logger.info(f"✓ Extracted {len(decisions)} decisions")
            return decisions
        except Exception as e:
            logger.error(f"Decision extraction failed: {str(e)}")
            return self._mock_decisions()
    
    async def analyze_ownership(self, code_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze code ownership and concentration"""
        if not self.available:
            return self._mock_ownership()
        
        try:
            ownership = self.analyzer.analyze_ownership(code_data)
            logger.info(f"✓ Analyzed ownership patterns")
            return ownership
        except Exception as e:
            logger.error(f"Ownership analysis failed: {str(e)}")
            return self._mock_ownership()
    
    async def detect_ghost_code(self, code_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect unused/stale code"""
        if not self.available:
            return self._mock_ghost_code()
        
        try:
            ghost_code = self.analyzer.detect_ghost_code(code_data)
            logger.info(f"✓ Detected {len(ghost_code)} ghost code candidates")
            return ghost_code
        except Exception as e:
            logger.error(f"Ghost code detection failed: {str(e)}")
            return self._mock_ghost_code()
    
    async def evaluate_bus_factor(self, ownership: List[Dict]) -> List[Dict[str, Any]]:
        """Evaluate bus factor and single points of failure"""
        if not self.available:
            return self._mock_bus_factor()
        
        try:
            alerts = self.analyzer.evaluate_bus_factor(ownership)
            logger.info(f"✓ Evaluated bus factor: {len(alerts)} alerts")
            return alerts
        except Exception as e:
            logger.error(f"Bus factor evaluation failed: {str(e)}")
            return self._mock_bus_factor()
    
    # Mock data methods (fallback when real services unavailable)
    @staticmethod
    def _mock_analysis(owner: str, repo: str) -> Dict[str, Any]:
        return {
            "owner": owner,
            "repo": repo,
            "timestamp": datetime.now().isoformat(),
            "decisions": [],
            "ownership": [],
            "ghost_code": [],
            "bus_factor_alerts": [],
            "scar_tissue": [],
            "metadata": {"mode": "mock", "note": "Real analyzer not available"}
        }
    
    @staticmethod
    def _mock_decisions() -> List[Dict[str, Any]]:
        return [
            {
                "type": "architecture",
                "description": "Move to microservices",
                "confidence": 0.85,
                "date": "2024-06-15"
            }
        ]
    
    @staticmethod
    def _mock_ownership() -> List[Dict[str, Any]]:
        return [
            {
                "path": "src/core",
                "owner": "alice",
                "concentration_percentage": 65,
                "risk": "high",
                "commit_count": 234
            }
        ]
    
    @staticmethod
    def _mock_ghost_code() -> List[Dict[str, Any]]:
        return [
            {
                "file": "src/legacy/old_module.py",
                "type": "unused_import",
                "last_touched_days": 390,
                "confidence": 0.92
            }
        ]
    
    @staticmethod
    def _mock_bus_factor() -> List[Dict[str, Any]]:
        return [
            {
                "area": "Authentication System",
                "owner": "bob",
                "concentration_percentage": 87,
                "risk_level": "CRITICAL"
            }
        ]


class OracleServiceWrapper:
    """Wraps your oracle.py for knowledge queries"""
    
    def __init__(self):
        """Initialize wrapper with your existing oracle"""
        try:
            from .oracle import Oracle
            self.oracle = Oracle()
            self.available = True
        except ImportError:
            logger.warning("Oracle not available, using mock")
            self.available = False
    
    async def query_knowledge(self, question: str) -> str:
        """Query oracle for contextual knowledge"""
        if not self.available:
            return f"[Mock Response] Context for: {question}"
        
        try:
            response = self.oracle.query(question)
            logger.info(f"✓ Oracle query completed")
            return response
        except Exception as e:
            logger.error(f"Oracle query failed: {str(e)}")
            return f"[Error] Could not retrieve knowledge: {str(e)}"


class GitHubIntegrationWrapper:
    """Wraps your GitHub integration"""
    
    def __init__(self):
        """Initialize GitHub client"""
        try:
            from .github_client import GitHubClient
            self.client = GitHubClient()
            self.available = True
        except ImportError:
            logger.warning("GitHub client not available")
            self.available = False
    
    async def get_repository_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get repository information from GitHub"""
        if not self.available:
            return self._mock_repo_info(owner, repo)
        
        try:
            info = self.client.get_repo(owner, repo)
            logger.info(f"✓ Retrieved repo info: {owner}/{repo}")
            return info
        except Exception as e:
            logger.error(f"GitHub fetch failed: {str(e)}")
            return self._mock_repo_info(owner, repo)
    
    async def get_commit_history(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """Get commit history"""
        if not self.available:
            return self._mock_commits()
        
        try:
            commits = self.client.get_commits(owner, repo)
            logger.info(f"✓ Retrieved {len(commits)} commits")
            return commits
        except Exception as e:
            logger.error(f"Commit fetch failed: {str(e)}")
            return self._mock_commits()
    
    @staticmethod
    def _mock_repo_info(owner: str, repo: str) -> Dict[str, Any]:
        return {
            "owner": owner,
            "name": repo,
            "url": f"https://github.com/{owner}/{repo}",
            "stars": 1250,
            "contributors": 24,
            "commits": 2834,
            "language": "Python",
            "mode": "mock"
        }
    
    @staticmethod
    def _mock_commits() -> List[Dict[str, Any]]:
        return [
            {
                "sha": "abc123",
                "message": "Refactor authentication module",
                "author": "alice",
                "date": "2024-06-15"
            }
        ]


# Initialize global service wrappers
analyzer_service = AnalyzerServiceWrapper()
oracle_service = OracleServiceWrapper()
github_service = GitHubIntegrationWrapper()