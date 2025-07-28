"""
Color Matching Service - Microservice for color analysis and matching
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

@app.post("/match-colors", response_model=ColorMatchResponse)
async def match_colors(request: ColorMatchRequest):
    """
    Match colors based on the user's skin tone and purpose
    """
    try:
        # Example color matching logic
        recommendations = [
            {"color": "#ff6347", "name": "Tomato", "confidence": 0.95, "category": request.purpose},
            {"color": "#4682b4", "name": "Steel Blue", "confidence": 0.9, "category": request.purpose},
            {"color": "#3cb371", "name": "Medium Sea Green", "confidence": 0.85, "category": request.purpose}
        ]
        
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
