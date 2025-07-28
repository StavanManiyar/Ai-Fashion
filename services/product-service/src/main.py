"""
Product Service - Microservice for product catalog management
"""
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for API
class ProductSearchRequest(BaseModel):
    user_id: Optional[str] = None
    skin_tone: str
    category: str  # makeup, clothing, accessories
    price_range: Optional[tuple] = None
    limit: int = 10

class ProductResponse(BaseModel):
    products: List[Dict[str, Any]]
    total_count: int
    timestamp: str

# Initialize FastAPI app
app = FastAPI(
    title="Product Service",
    description="Microservice for product catalog and recommendations",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Initialize dependencies on startup"""
    logger.info("Starting Product Service...")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Product Service...")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "product-service",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/products", response_model=ProductResponse)
async def get_products(
    skin_tone: str = Query(..., description="User's skin tone"),
    category: str = Query("makeup", description="Product category"),
    limit: int = Query(10, description="Number of products to return"),
    page: int = Query(1, description="Page number")
):
    """
    Get products filtered by skin tone and category
    """
    try:
        # Mock product data - replace with actual database query
        mock_products = [
            {
                "id": "prod_001",
                "name": "Foundation Shade 120",
                "brand": "Beauty Brand",
                "price": 29.99,
                "category": category,
                "skin_tone_match": skin_tone,
                "rating": 4.5,
                "image_url": "https://example.com/product1.jpg"
            },
            {
                "id": "prod_002", 
                "name": "Lipstick Berry Bliss",
                "brand": "Makeup Co",
                "price": 19.99,
                "category": category,
                "skin_tone_match": skin_tone,
                "rating": 4.2,
                "image_url": "https://example.com/product2.jpg"
            }
        ]
        
        return ProductResponse(
            products=mock_products[:limit],
            total_count=len(mock_products),
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        logger.error(f"Error getting products: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Product search failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
