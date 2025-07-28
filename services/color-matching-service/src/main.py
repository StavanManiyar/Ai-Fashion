"""
Color Matching Service - Microservice for color analysis and matching
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging
import redis.asyncio as redis
import json
from datetime import datetime
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis cache client
redis_client = None

# Pydantic models for API
class ColorMatchRequest(BaseModel):
    user_id: Optional[str] = None
    skin_tone: str
    purpose: str  # clothing, makeup, accessories

class ColorMatchResponse(BaseModel):
    recommendations: list[Dict[str, Any]]
    timestamp: str

# Initialize FastAPI app
app = FastAPI(
    title="Color Matching Service",
    description="Microservice for color analysis and palette recommendations",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Initialize dependencies on startup"""
    global redis_client
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
    try:
        redis_client = redis.from_url(redis_url)
        await redis_client.ping()
        logger.info("Connected to Redis successfully")
    except Exception as e:
        logger.warning(f"Could not connect to Redis: {e}")
        redis_client = None
    
    logger.info("Starting Color Matching Service...")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Color Matching Service...")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "color-matching-service",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

async def get_cached_recommendations(skin_tone: str, purpose: str) -> Optional[List[Dict[str, Any]]]:
    """Get cached color recommendations"""
    if not redis_client:
        return None
    
    cache_key = f"color_match:{skin_tone}:{purpose}"
    try:
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
    except Exception as e:
        logger.warning(f"Cache retrieval failed: {e}")
    return None

async def cache_recommendations(skin_tone: str, purpose: str, recommendations: List[Dict[str, Any]]) -> None:
    """Cache color recommendations for 30 minutes"""
    if not redis_client:
        return
    
    cache_key = f"color_match:{skin_tone}:{purpose}"
    try:
        await redis_client.setex(cache_key, 1800, json.dumps(recommendations))
        logger.info(f"Cached recommendations for {skin_tone}:{purpose}")
    except Exception as e:
        logger.warning(f"Cache storage failed: {e}")

def get_color_recommendations_by_monk_tone(monk_tone: str, purpose: str) -> List[Dict[str, Any]]:
    """Get color recommendations based on Monk skin tone scale"""
    
    # Color palettes for different monk tones and purposes
    COLOR_PALETTES = {
        "1": {  # Lightest tones
            "makeup": [
                {"color": "#F4C2A1", "name": "Light Peach", "confidence": 0.95, "type": "foundation"},
                {"color": "#E8B4CB", "name": "Soft Pink", "confidence": 0.9, "type": "blush"},
                {"color": "#D4A574", "name": "Golden Beige", "confidence": 0.85, "type": "eyeshadow"}
            ],
            "clothing": [
                {"color": "#FF6B6B", "name": "Coral Red", "confidence": 0.9, "type": "accent"},
                {"color": "#4ECDC4", "name": "Teal", "confidence": 0.85, "type": "primary"},
                {"color": "#45B7D1", "name": "Sky Blue", "confidence": 0.8, "type": "secondary"}
            ]
        },
        "5": {  # Medium tones
            "makeup": [
                {"color": "#D2B48C", "name": "Tan", "confidence": 0.95, "type": "foundation"},
                {"color": "#CD853F", "name": "Peru", "confidence": 0.9, "type": "bronzer"},
                {"color": "#8B4513", "name": "Saddle Brown", "confidence": 0.85, "type": "eyeshadow"}
            ],
            "clothing": [
                {"color": "#FF8C00", "name": "Dark Orange", "confidence": 0.9, "type": "accent"},
                {"color": "#32CD32", "name": "Lime Green", "confidence": 0.85, "type": "primary"},
                {"color": "#9370DB", "name": "Medium Purple", "confidence": 0.8, "type": "secondary"}
            ]
        },
        "10": {  # Darkest tones
            "makeup": [
                {"color": "#8B4513", "name": "Saddle Brown", "confidence": 0.95, "type": "foundation"},
                {"color": "#A0522D", "name": "Sienna", "confidence": 0.9, "type": "bronzer"},
                {"color": "#CD853F", "name": "Peru", "confidence": 0.85, "type": "highlight"}
            ],
            "clothing": [
                {"color": "#FFD700", "name": "Gold", "confidence": 0.95, "type": "accent"},
                {"color": "#FF4500", "name": "Orange Red", "confidence": 0.9, "type": "primary"},
                {"color": "#00CED1", "name": "Dark Turquoise", "confidence": 0.85, "type": "secondary"}
            ]
        }
    }
    
    # Get recommendations for the specific monk tone and purpose
    if monk_tone in COLOR_PALETTES and purpose in COLOR_PALETTES[monk_tone]:
        return COLOR_PALETTES[monk_tone][purpose]
    
    # Fallback to medium tone if specific tone not found
    if "5" in COLOR_PALETTES and purpose in COLOR_PALETTES["5"]:
        return COLOR_PALETTES["5"][purpose]
    
    # Ultimate fallback
    return [
        {"color": "#808080", "name": "Gray", "confidence": 0.5, "type": "neutral"}
    ]

@app.post("/match-colors", response_model=ColorMatchResponse)
async def match_colors(request: ColorMatchRequest):
    """
    Match colors based on the user's skin tone and purpose
    """
    try:
        # Check cache first
        cached_recommendations = await get_cached_recommendations(request.skin_tone, request.purpose)
        if cached_recommendations:
            logger.info(f"Returning cached recommendations for {request.skin_tone}:{request.purpose}")
            return ColorMatchResponse(
                recommendations=cached_recommendations,
                timestamp=datetime.utcnow().isoformat()
            )
        
        # Generate new recommendations
        recommendations = get_color_recommendations_by_monk_tone(request.skin_tone, request.purpose)
        
        # Add metadata
        for rec in recommendations:
            rec['category'] = request.purpose
            rec['monk_tone'] = request.skin_tone
            rec['generated_at'] = datetime.utcnow().isoformat()
        
        # Cache the results
        await cache_recommendations(request.skin_tone, request.purpose, recommendations)
        
        logger.info(f"Generated {len(recommendations)} recommendations for {request.skin_tone}:{request.purpose}")
        
        return ColorMatchResponse(
            recommendations=recommendations,
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        logger.error(f"Error matching colors: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Color matching failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
