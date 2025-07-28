"""
Image Processing Service - Microservice for skin tone analysis and image processing
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import asyncio
import logging
from datetime import datetime
import uuid
import sys
import os

# Add shared module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared'))

from domain.entities.skin_tone import SkinTone, ColorRecommendation
from image_processor import ImageProcessor
from skin_tone_analyzer import SkinToneAnalyzer
from event_publisher import EventPublisher
from cache_service import CacheService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for API
class ImageAnalysisRequest(BaseModel):
    user_id: Optional[str] = None
    analysis_type: str = "skin_tone"  # skin_tone, color_palette, full_analysis
    
class ImageAnalysisResponse(BaseModel):
    analysis_id: str
    skin_tone: Dict[str, Any]
    confidence: float
    processing_time_ms: int
    timestamp: str

class AnalysisStatusResponse(BaseModel):
    analysis_id: str
    status: str  # processing, completed, failed
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Initialize FastAPI app
app = FastAPI(
    title="Image Processing Service",
    description="Microservice for AI-powered skin tone analysis and image processing",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service dependencies
image_processor = ImageProcessor()
skin_tone_analyzer = SkinToneAnalyzer()
event_publisher = EventPublisher()
cache_service = CacheService()

# In-memory storage for demo (replace with Redis/Database in production)
analysis_results = {}
processing_queue = {}

@app.on_event("startup")
async def startup_event():
    """Initialize service dependencies on startup"""
    logger.info("Starting Image Processing Service...")
    await event_publisher.initialize()
    await cache_service.initialize()
    logger.info("Image Processing Service started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Image Processing Service...")
    await event_publisher.close()
    await cache_service.close()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "image-processing-service",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.post("/analyze/skin-tone", response_model=ImageAnalysisResponse)
async def analyze_skin_tone(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: Optional[str] = None
):
    """
    Analyze skin tone from uploaded image
    """
    try:
        # Generate unique analysis ID
        analysis_id = str(uuid.uuid4())
        
        # Validate file
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read image data
        image_data = await file.read()
        
        # Check cache first
        cache_key = f"skin_tone:{hash(image_data)}"
        cached_result = await cache_service.get(cache_key)
        
        if cached_result:
            logger.info(f"Returning cached result for analysis {analysis_id}")
            return ImageAnalysisResponse(
                analysis_id=analysis_id,
                skin_tone=cached_result['skin_tone'],
                confidence=cached_result['confidence'],
                processing_time_ms=cached_result['processing_time_ms'],
                timestamp=datetime.utcnow().isoformat()
            )
        
        # Start background processing
        background_tasks.add_task(
            process_skin_tone_analysis,
            analysis_id,
            image_data,
            user_id,
            cache_key
        )
        
        # Mark as processing
        processing_queue[analysis_id] = {
            'status': 'processing',
            'started_at': datetime.utcnow(),
            'user_id': user_id
        }
        
        # For demo, process synchronously (in production, return immediately)
        result = await process_skin_tone_sync(analysis_id, image_data, user_id, cache_key)
        
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing skin tone: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/analysis/{analysis_id}/status", response_model=AnalysisStatusResponse)
async def get_analysis_status(analysis_id: str):
    """
    Get the status of a skin tone analysis
    """
    if analysis_id in analysis_results:
        result = analysis_results[analysis_id]
        return AnalysisStatusResponse(
            analysis_id=analysis_id,
            status="completed",
            result=result
        )
    elif analysis_id in processing_queue:
        return AnalysisStatusResponse(
            analysis_id=analysis_id,
            status="processing"
        )
    else:
        raise HTTPException(status_code=404, detail="Analysis not found")

async def process_skin_tone_sync(
    analysis_id: str,
    image_data: bytes,
    user_id: Optional[str],
    cache_key: str
) -> ImageAnalysisResponse:
    """
    Process skin tone analysis synchronously
    """
    start_time = datetime.utcnow()
    
    try:
        # Process image
        processed_image = await image_processor.process_image(image_data)
        
        # Analyze skin tone
        skin_tone_result = await skin_tone_analyzer.analyze_skin_tone(processed_image)
        
        # Create domain entity
        skin_tone = SkinTone(
            monk_scale=skin_tone_result['monk_scale'],
            hex_color=skin_tone_result['hex_color'],
            confidence=skin_tone_result['confidence'],
            season_type=skin_tone_result.get('season_type'),
            undertone=skin_tone_result.get('undertone')
        )
        
        # Calculate processing time
        end_time = datetime.utcnow()
        processing_time_ms = int((end_time - start_time).total_seconds() * 1000)
        
        # Create response
        response_data = {
            'skin_tone': skin_tone.to_dict(),
            'confidence': skin_tone.confidence,
            'processing_time_ms': processing_time_ms
        }
        
        # Cache result
        await cache_service.set(cache_key, response_data, ttl=3600)  # 1 hour
        
        # Store result
        analysis_results[analysis_id] = response_data
        
        # Remove from processing queue
        if analysis_id in processing_queue:
            del processing_queue[analysis_id]
        
        # Publish event
        await event_publisher.publish_skin_tone_analyzed(
            analysis_id=analysis_id,
            user_id=user_id,
            skin_tone=skin_tone
        )
        
        return ImageAnalysisResponse(
            analysis_id=analysis_id,
            skin_tone=skin_tone.to_dict(),
            confidence=skin_tone.confidence,
            processing_time_ms=processing_time_ms,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error processing skin tone analysis {analysis_id}: {str(e)}")
        
        # Mark as failed
        if analysis_id in processing_queue:
            processing_queue[analysis_id]['status'] = 'failed'
            processing_queue[analysis_id]['error'] = str(e)
        
        raise

async def process_skin_tone_analysis(
    analysis_id: str,
    image_data: bytes,
    user_id: Optional[str],
    cache_key: str
):
    """
    Background task for processing skin tone analysis
    """
    try:
        await process_skin_tone_sync(analysis_id, image_data, user_id, cache_key)
        logger.info(f"Completed skin tone analysis {analysis_id}")
    except Exception as e:
        logger.error(f"Failed to process skin tone analysis {analysis_id}: {str(e)}")

@app.get("/metrics")
async def get_metrics():
    """Get service metrics"""
    return {
        "active_analyses": len(processing_queue),
        "completed_analyses": len(analysis_results),
        "cache_stats": await cache_service.get_stats(),
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
