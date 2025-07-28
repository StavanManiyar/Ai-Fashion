"""
Domain Events System for AI Fashion Platform
Implements event-driven architecture and CQRS patterns
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import uuid


class EventType(Enum):
    """Event types for the AI Fashion platform"""
    SKIN_TONE_ANALYZED = "skin_tone_analyzed"
    COLOR_RECOMMENDATION_REQUESTED = "color_recommendation_requested"
    PRODUCT_RECOMMENDATION_GENERATED = "product_recommendation_generated"
    USER_FEEDBACK_RECEIVED = "user_feedback_received"
    USER_PROFILE_UPDATED = "user_profile_updated"
    OUTFIT_COMPATIBILITY_ANALYZED = "outfit_compatibility_analyzed"
    TREND_DATA_UPDATED = "trend_data_updated"


@dataclass
class BaseEvent(ABC):
    """Base class for all domain events"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = field(init=False)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None
    correlation_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @abstractmethod
    def get_payload(self) -> Dict[str, Any]:
        """Return the event payload"""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type.value,
            'timestamp': self.timestamp.isoformat(),
            'user_id': self.user_id,
            'correlation_id': self.correlation_id,
            'metadata': self.metadata,
            'payload': self.get_payload()
        }


@dataclass
class SkinToneAnalyzedEvent(BaseEvent):
    """Event fired when skin tone analysis is completed"""
    analysis_result: Dict[str, Any]
    confidence_score: float
    monk_tone: str
    hex_color: str
    
    def __post_init__(self):
        self.event_type = EventType.SKIN_TONE_ANALYZED
    
    def get_payload(self) -> Dict[str, Any]:
        return {
            'analysis_result': self.analysis_result,
            'confidence_score': self.confidence_score,
            'monk_tone': self.monk_tone,
            'hex_color': self.hex_color
        }


@dataclass
class ColorRecommendationRequestedEvent(BaseEvent):
    """Event fired when color recommendations are requested"""
    skin_tone: str
    user_preferences: Dict[str, Any]
    season: Optional[str] = None
    occasion: Optional[str] = None
    
    def __post_init__(self):
        self.event_type = EventType.COLOR_RECOMMENDATION_REQUESTED
    
    def get_payload(self) -> Dict[str, Any]:
        return {
            'skin_tone': self.skin_tone,
            'user_preferences': self.user_preferences,
            'season': self.season,
            'occasion': self.occasion
        }


@dataclass
class ProductRecommendationGeneratedEvent(BaseEvent):
    """Event fired when product recommendations are generated"""
    recommendations: List[Dict[str, Any]]
    algorithm_used: str
    recommendation_score: float
    filters_applied: Dict[str, Any]
    
    def __post_init__(self):
        self.event_type = EventType.PRODUCT_RECOMMENDATION_GENERATED
    
    def get_payload(self) -> Dict[str, Any]:
        return {
            'recommendations': self.recommendations,
            'algorithm_used': self.algorithm_used,
            'recommendation_score': self.recommendation_score,
            'filters_applied': self.filters_applied
        }


@dataclass
class UserFeedbackReceivedEvent(BaseEvent):
    """Event fired when user provides feedback"""
    feedback_type: str  # 'like', 'dislike', 'rating', 'comment'
    target_type: str    # 'product', 'color', 'recommendation'
    target_id: str
    feedback_value: Any
    context: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        self.event_type = EventType.USER_FEEDBACK_RECEIVED
    
    def get_payload(self) -> Dict[str, Any]:
        return {
            'feedback_type': self.feedback_type,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'feedback_value': self.feedback_value,
            'context': self.context
        }


@dataclass
class UserProfileUpdatedEvent(BaseEvent):
    """Event fired when user profile is updated"""
    profile_changes: Dict[str, Any]
    update_source: str  # 'user_input', 'ml_inference', 'feedback_analysis'
    previous_values: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        self.event_type = EventType.USER_PROFILE_UPDATED
    
    def get_payload(self) -> Dict[str, Any]:
        return {
            'profile_changes': self.profile_changes,
            'update_source': self.update_source,
            'previous_values': self.previous_values
        }


class EventHandler(ABC):
    """Base class for event handlers"""
    
    @abstractmethod
    async def handle(self, event: BaseEvent) -> None:
        """Handle the event"""
        pass
    
    @abstractmethod
    def can_handle(self, event_type: EventType) -> bool:
        """Check if this handler can process the event type"""
        pass


class EventBus:
    """Event bus for publishing and subscribing to domain events"""
    
    def __init__(self):
        self._handlers: Dict[EventType, List[EventHandler]] = {}
        self._event_store: List[BaseEvent] = []
    
    def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """Subscribe a handler to an event type"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    async def publish(self, event: BaseEvent) -> None:
        """Publish an event to all subscribers"""
        # Store event for audit/replay purposes
        self._event_store.append(event)
        
        # Notify handlers
        if event.event_type in self._handlers:
            for handler in self._handlers[event.event_type]:
                try:
                    await handler.handle(event)
                except Exception as e:
                    # Log error but don't stop other handlers
                    print(f"Error handling event {event.event_id}: {e}")
    
    def get_events(self, user_id: Optional[str] = None, 
                   event_type: Optional[EventType] = None,
                   limit: int = 100) -> List[BaseEvent]:
        """Retrieve events from the store"""
        events = self._event_store
        
        if user_id:
            events = [e for e in events if e.user_id == user_id]
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        return events[-limit:]  # Most recent events
