"""
Use case for analyzing skin tone from uploaded images.
"""
import asyncio
from typing import Protocol
from shared.domain.entities.skin_tone import SkinToneAnalysis
from shared.domain.events.events import SkinToneAnalyzedEvent


class ImageProcessor(Protocol):
    """Protocol for image processing implementations."""
    
    async def process(self, image_data: bytes) -> dict:
        """Process raw image data."""
        ...
    
    async def analyze_skin_tone(self, processed_image: dict) -> SkinToneAnalysis:
        """Analyze skin tone from processed image."""
        ...


class SkinToneRepository(Protocol):
    """Protocol for skin tone data persistence."""
    
    async def save(self, analysis: SkinToneAnalysis) -> None:
        """Save skin tone analysis."""
        ...


class EventPublisher(Protocol):
    """Protocol for publishing domain events."""
    
    async def publish(self, event: SkinToneAnalyzedEvent) -> None:
        """Publish an event."""
        ...


class AnalyzeSkinToneUseCase:
    """Use case for analyzing skin tone from images."""
    
    def __init__(self, 
                 image_processor: ImageProcessor,
                 skin_tone_repository: SkinToneRepository,
                 event_publisher: EventPublisher):
        self._image_processor = image_processor
        self._skin_tone_repository = skin_tone_repository
        self._event_publisher = event_publisher
    
    async def execute(self, image_data: bytes, user_id: str) -> SkinToneAnalysis:
        """Execute the skin tone analysis use case."""
        # Process the image
        processed_image = await self._image_processor.process(image_data)
        
        # Analyze skin tone
        analysis = await self._image_processor.analyze_skin_tone(processed_image)
        
        # Save the analysis result
        await self._skin_tone_repository.save(analysis)
        
        # Publish domain event
        event = SkinToneAnalyzedEvent(analysis, user_id)
        await self._event_publisher.publish(event)
        
        return analysis
