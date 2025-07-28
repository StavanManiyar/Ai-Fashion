"""
Cache Service - Redis-based caching for performance optimization
"""
import json
import logging
from typing import Any, Optional, Dict
import aioredis
import pickle
import hashlib

logger = logging.getLogger(__name__)

class CacheService:
    """
    Redis-based caching service for storing analysis results and improving performance
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client = None
        self.default_ttl = 3600  # 1 hour
        self.cache_prefix = "ai_fashion_cache"
    
    async def initialize(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = aioredis.from_url(self.redis_url, decode_responses=False)
            await self.redis_client.ping()
            logger.info("Cache service initialized successfully")
        except Exception as e:
            logger.warning(f"Could not connect to Redis: {e}. Caching disabled.")
            self.redis_client = None
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
    
    def _generate_key(self, key: str) -> str:
        """Generate a prefixed cache key"""
        return f"{self.cache_prefix}:{key}"
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        """
        if not self.redis_client:
            return None
        
        try:
            cache_key = self._generate_key(key)
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                # Try to deserialize as JSON first, then pickle
                try:
                    return json.loads(cached_data.decode('utf-8'))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    try:
                        return pickle.loads(cached_data)
                    except Exception:
                        logger.warning(f"Could not deserialize cached data for key: {key}")
                        return None
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting from cache (key: {key}): {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache with optional TTL
        """
        if not self.redis_client:
            return False
        
        try:
            cache_key = self._generate_key(key)
            ttl = ttl or self.default_ttl
            
            # Try to serialize as JSON first, then pickle
            try:
                serialized_data = json.dumps(value).encode('utf-8')
            except (TypeError, ValueError):
                try:
                    serialized_data = pickle.dumps(value)
                except Exception as e:
                    logger.error(f"Could not serialize data for key {key}: {e}")
                    return False
            
            await self.redis_client.setex(cache_key, ttl, serialized_data)
            logger.debug(f"Cached data for key: {key} with TTL: {ttl}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting cache (key: {key}): {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Delete value from cache
        """
        if not self.redis_client:
            return False
        
        try:
            cache_key = self._generate_key(key)
            deleted = await self.redis_client.delete(cache_key)
            return bool(deleted)
            
        except Exception as e:
            logger.error(f"Error deleting from cache (key: {key}): {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache
        """
        if not self.redis_client:
            return False
        
        try:
            cache_key = self._generate_key(key)
            return bool(await self.redis_client.exists(cache_key))
            
        except Exception as e:
            logger.error(f"Error checking cache existence (key: {key}): {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        """
        if not self.redis_client:
            return {"status": "disabled", "connection": False}
        
        try:
            info = await self.redis_client.info()
            
            return {
                "status": "active",
                "connection": True,
                "used_memory": info.get('used_memory_human', 'unknown'),
                "connected_clients": info.get('connected_clients', 0),
                "total_commands_processed": info.get('total_commands_processed', 0),
                "hits": info.get('keyspace_hits', 0),
                "misses": info.get('keyspace_misses', 0),
                "keys": await self._count_service_keys()
            }
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"status": "error", "connection": False, "error": str(e)}
    
    async def _count_service_keys(self) -> int:
        """Count keys belonging to this service"""
        try:
            pattern = f"{self.cache_prefix}:*"
            keys = await self.redis_client.keys(pattern)
            return len(keys)
        except Exception:
            return 0
    
    async def clear_service_cache(self) -> int:
        """
        Clear all cache entries for this service
        """
        if not self.redis_client:
            return 0
        
        try:
            pattern = f"{self.cache_prefix}:*"
            keys = await self.redis_client.keys(pattern)
            
            if keys:
                deleted = await self.redis_client.delete(*keys)
                logger.info(f"Cleared {deleted} cache entries")
                return deleted
            
            return 0
            
        except Exception as e:
            logger.error(f"Error clearing service cache: {e}")
            return 0
    
    def generate_image_hash(self, image_data: bytes) -> str:
        """
        Generate a hash for image data to use as cache key
        """
        return hashlib.md5(image_data).hexdigest()
    
    async def cache_skin_tone_result(
        self, 
        image_data: bytes, 
        result: Dict[str, Any], 
        ttl: Optional[int] = None
    ) -> str:
        """
        Cache skin tone analysis result using image hash as key
        """
        image_hash = self.generate_image_hash(image_data)
        cache_key = f"skin_tone:{image_hash}"
        
        await self.set(cache_key, result, ttl)
        return cache_key
    
    async def get_cached_skin_tone_result(self, image_data: bytes) -> Optional[Dict[str, Any]]:
        """
        Get cached skin tone result using image hash
        """
        image_hash = self.generate_image_hash(image_data)
        cache_key = f"skin_tone:{image_hash}"
        
        return await self.get(cache_key)
