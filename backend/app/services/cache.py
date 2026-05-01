"""
cache.py - Result caching to avoid re-analyzing
"""

import hashlib
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)


class AnalysisCache:
    """Cache analysis results by repository"""
    
    def __init__(self, ttl_hours: int = 24):
        """Initialize cache with TTL"""
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = timedelta(hours=ttl_hours)
    
    def _get_key(self, owner: str, repo: str) -> str:
        """Generate cache key"""
        key_str = f"{owner}:{repo}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, owner: str, repo: str) -> Optional[Dict[str, Any]]:
        """Get cached result if valid"""
        key = self._get_key(owner, repo)
        
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        
        # Check if expired
        cached_at = datetime.fromisoformat(entry["cached_at"])
        if datetime.now() - cached_at > self.ttl:
            del self.cache[key]
            logger.info(f"Cache expired for {owner}/{repo}")
            return None
        
        logger.info(f"✓ Cache hit for {owner}/{repo}")
        return entry["data"]
    
    def set(self, owner: str, repo: str, data: Dict[str, Any]):
        """Cache analysis result"""
        key = self._get_key(owner, repo)
        
        self.cache[key] = {
            "data": data,
            "cached_at": datetime.now().isoformat()
        }
        
        logger.info(f"✓ Cached result for {owner}/{repo}")
    
    def clear(self):
        """Clear entire cache"""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "cached_entries": len(self.cache),
            "ttl_hours": self.ttl.total_seconds() / 3600
        }


# Global cache instance
analysis_cache = AnalysisCache(ttl_hours=24)