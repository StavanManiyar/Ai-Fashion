"""
Message broker implementations for inter-service communication.
"""
import redis.asyncio as redis
from typing import Protocol


class MessageBroker(Protocol):
    """Protocol for message broker implementations."""
    
    async def publish(self, channel: str, message: str) -> None:
        """Publish a message to a channel."""
        ...
    
    async def subscribe(self, channel: str):
        """Subscribe to a channel."""
        ...


class RedisMessageBroker:
    """Redis implementation of message broker."""
    
    def __init__(self, redis_url: str):
        self._redis = redis.StrictRedis.from_url(redis_url)
    
    async def publish(self, channel: str, message: str) -> None:
        """Publish a message to Redis channel."""
        await self._redis.publish(channel, message)
    
    async def subscribe(self, channel: str):
        """Subscribe to Redis channel."""
        pubsub = self._redis.pubsub()
        await pubsub.subscribe(channel)
        return pubsub
