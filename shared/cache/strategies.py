"""
Caching strategies for improved performance across services.
"""
import json
import redis.asyncio as redis
from typing import List, Optional
from shared.domain.entities.skin_tone import SkinToneAnalysis
from shared.domain.entities.color_recommendation import ColorRecommendation


class CacheStrategy:
    """Base caching strategy using Redis."""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    async def cache_skin_tone_analysis(self, user_id: str, analysis: SkinToneAnalysis) -> None:
        """Cache skin tone analysis for a user with 1 hour TTL."""
        key = f"skin_tone:{user_id}"
        value = analysis.to_dict() if hasattr(analysis, 'to_dict') else analysis.__dict__
        await self.redis.setex(key, 3600, json.dumps(value))
    
    async def get_cached_skin_tone_analysis(self, user_id: str) -> Optional[dict]:
        """Retrieve cached skin tone analysis."""
        key = f"skin_tone:{user_id}"
        cached_data = await self.redis.get(key)
        if cached_data:
            return json.loads(cached_data)
        return None
    
    async def cache_color_recommendations(self, skin_tone: str, recommendations: List[ColorRecommendation]) -> None:
        """Cache color recommendations with 30 minute TTL."""
        key = f"color_recs:{skin_tone}"
        value = [rec.to_dict() if hasattr(rec, 'to_dict') else rec.__dict__ for rec in recommendations]
        await self.redis.setex(key, 1800, json.dumps(value))
    
    async def get_cached_color_recommendations(self, skin_tone: str) -> Optional[List[dict]]:
        """Retrieve cached color recommendations."""
        key = f"color_recs:{skin_tone}"
        cached_data = await self.redis.get(key)
        if cached_data:
            return json.loads(cached_data)
        return None
    
    async def cache_product_search(self, search_key: str, products: List[dict]) -> None:
        """Cache product search results with 10 minute TTL."""
        key = f"products:{search_key}"
        await self.redis.setex(key, 600, json.dumps(products))
    
    async def get_cached_product_search(self, search_key: str) -> Optional[List[dict]]:
        """Retrieve cached product search results."""
        key = f"products:{search_key}"
        cached_data = await self.redis.get(key)
        if cached_data:
            return json.loads(cached_data)
        return None
    
    async def invalidate_user_cache(self, user_id: str) -> None:
        """Invalidate all cache entries for a user."""
        pattern = f"*:{user_id}*"
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)
    
    async def clear_all_cache(self) -> None:
        """Clear all cache entries (use with caution)."""
        await self.redis.flushall()
