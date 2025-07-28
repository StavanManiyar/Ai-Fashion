"""
Event Publisher - Publishes events to other microservices
"""
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import aioredis
import asyncio

logger = logging.getLogger(__name__)

class EventPublisher:
    """
    Publishes events to message broker for inter-service communication
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client = None
        self.channel_prefix = "ai_fashion_events"
    
    async def initialize(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = aioredis.from_url(self.redis_url, decode_responses=True)
            await self.redis_client.ping()
            logger.info("Event publisher initialized successfully")
        except Exception as e:
            logger.warning(f"Could not connect to Redis: {e}. Events will be logged only.")
            self.redis_client = None
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
    
    async def publish_event(self, event_type: str, event_data: Dict[str, Any]):
        """
        Publish an event to the message broker
        """
        try:
            event = {
                "event_type": event_type,
                "event_id": f"{event_type}_{datetime.utcnow().timestamp()}",
                "timestamp": datetime.utcnow().isoformat(),
                "service": "image-processing-service",
                "data": event_data
            }
            
            # Publish to Redis if available
            if self.redis_client:
                channel = f"{self.channel_prefix}:{event_type}"
                await self.redis_client.publish(channel, json.dumps(event))
                logger.info(f"Published event {event_type} to channel {channel}")
            else:
                # Log event if Redis not available
                logger.info(f"Event logged (Redis unavailable): {event_type} - {event_data}")
                
        except Exception as e:
            logger.error(f"Failed to publish event {event_type}: {e}")
    
    async def publish_skin_tone_analyzed(
        self, 
        analysis_id: str, 
        user_id: Optional[str], 
        skin_tone: 'SkinTone'
    ):
        """
        Publish skin tone analysis completed event
        """
        event_data = {
            "analysis_id": analysis_id,
            "user_id": user_id,
            "skin_tone": skin_tone.to_dict(),
            "processing_service": "image-processing-service"
        }
        
        await self.publish_event("skin_tone_analyzed", event_data)
    
    async def publish_analysis_started(self, analysis_id: str, user_id: Optional[str]):
        """
        Publish analysis started event
        """
        event_data = {
            "analysis_id": analysis_id,
            "user_id": user_id,
            "started_at": datetime.utcnow().isoformat()
        }
        
        await self.publish_event("analysis_started", event_data)
    
    async def publish_analysis_failed(
        self, 
        analysis_id: str, 
        user_id: Optional[str], 
        error_message: str
    ):
        """
        Publish analysis failed event
        """
        event_data = {
            "analysis_id": analysis_id,
            "user_id": user_id,
            "error_message": error_message,
            "failed_at": datetime.utcnow().isoformat()
        }
        
        await self.publish_event("analysis_failed", event_data)
