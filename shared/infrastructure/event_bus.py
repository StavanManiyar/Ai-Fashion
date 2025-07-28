"""
Event bus implementation using Redis for message brokering.
"""
from typing import Type, Callable, Dict
import asyncio
import redis.asyncio as redis
from shared.domain.events.base_events import Event


class RedisMessageBroker:
    """Redis implementation of a message broker."""
    
    def __init__(self, redis_url: str):
        self._redis = redis.StrictRedis.from_url(redis_url)

    async def publish(self, channel: str, message: str) -> None:
        """Publish a message to a Redis channel."""
        await self._redis.publish(channel, message)

    async def subscribe(self, channel: str) -> redis.client.PubSub:
        """Subscribe to a Redis channel."""
        pubsub = self._redis.pubsub()
        await pubsub.subscribe(channel)
        return pubsub


class EventBus:
    """Event bus for managing domain events."""

    def __init__(self, broker: RedisMessageBroker):
        self._broker = broker
        self._handlers: Dict[Type[Event], Callable[[Event], None]] = {}

    async def publish(self, event: Event) -> None:
        """Publish an event using the message broker."""
        await self._broker.publish(event.__class__.__name__, event.json())

    def subscribe(self, event_type: Type[Event], handler: Callable[[Event], None]) -> None:
        """Subscribe to a specific event type and associate a handler."""
        self._handlers[event_type] = handler

    async def start_listening(self, channel: str) -> None:
        """Start listening to a Redis channel for events."""
        pubsub = await self._broker.subscribe(channel)

        async for message in pubsub.listen():
            if message['type'] == 'message':
                event_data = message['data']
                event_type = message['channel']

                if event_type in self._handlers:
                    event_class = self._handlers[event_type]
                    event = event_class.parse_raw(event_data)
                    event()

    def handle_event(self, event: Event) -> None:
        """Handle an incoming event."""
        handler = self._handlers.get(type(event))
        if handler:
            handler(event)

