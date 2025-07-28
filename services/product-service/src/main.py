"""
Product Service - Microservice for product catalog management
"""
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging
import redis.asyncio as redis
import json
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis cache client
redis_client = None

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
    global redis_client
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
    try:
        redis_client = redis.from_url(redis_url)
        await redis_client.ping()
        logger.info("Connected to Redis successfully")
    except Exception as e:
        logger.warning(f"Could not connect to Redis: {e}")
        redis_client = None
    
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

async def get_cached_products(skin_tone: str, category: str, limit: int, page: int) -> Optional[List[Dict[str, Any]]]:
    """Get cached product results"""
    if not redis_client:
        return None
    
    cache_key = f"products:{skin_tone}:{category}:{limit}:{page}"
    try:
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
    except Exception as e:
        logger.warning(f"Cache retrieval failed: {e}")
    return None

async def cache_products(skin_tone: str, category: str, limit: int, page: int, products: List[Dict[str, Any]]) -> None:
    """Cache product results for 10 minutes"""
    if not redis_client:
        return
    
    cache_key = f"products:{skin_tone}:{category}:{limit}:{page}"
    try:
        await redis_client.setex(cache_key, 600, json.dumps(products))
        logger.info(f"Cached products for {cache_key}")
    except Exception as e:
        logger.warning(f"Cache storage failed: {e}")

def get_mock_products_by_criteria(skin_tone: str, category: str) -> List[Dict[str, Any]]:
    """Get mock products filtered by skin tone and category"""
    
    # Enhanced mock product database with skin tone compatibility
    PRODUCT_DATABASE = {
        "makeup": {
            "1": [  # Light skin tones
                {
                    "id": "makeup_001",
                    "name": "Porcelain Perfect Foundation",
                    "brand": "Luxury Beauty",
                    "price": 45.99,
                    "category": "makeup",
                    "sub_category": "foundation",
                    "skin_tone_compatibility": ["1", "2"],
                    "rating": 4.8,
                    "review_count": 324,
                    "image_url": "https://example.com/foundation_light.jpg",
                    "description": "Perfect coverage for light skin tones"
                },
                {
                    "id": "makeup_002",
                    "name": "Rose Petal Blush",
                    "brand": "Pink Beauty",
                    "price": 22.99,
                    "category": "makeup",
                    "sub_category": "blush",
                    "skin_tone_compatibility": ["1", "2", "3"],
                    "rating": 4.5,
                    "review_count": 156,
                    "image_url": "https://example.com/blush_rose.jpg",
                    "description": "Natural rose blush for fair complexions"
                }
            ],
            "5": [  # Medium skin tones
                {
                    "id": "makeup_005",
                    "name": "Warm Honey Foundation",
                    "brand": "Inclusive Beauty",
                    "price": 38.99,
                    "category": "makeup",
                    "sub_category": "foundation",
                    "skin_tone_compatibility": ["4", "5", "6"],
                    "rating": 4.7,
                    "review_count": 412,
                    "image_url": "https://example.com/foundation_medium.jpg",
                    "description": "Perfect match for medium skin tones"
                },
                {
                    "id": "makeup_006",
                    "name": "Terracotta Bronzer",
                    "brand": "Sun Beauty",
                    "price": 29.99,
                    "category": "makeup",
                    "sub_category": "bronzer",
                    "skin_tone_compatibility": ["4", "5", "6", "7"],
                    "rating": 4.6,
                    "review_count": 287,
                    "image_url": "https://example.com/bronzer_terracotta.jpg",
                    "description": "Natural bronzing for medium to deep tones"
                }
            ],
            "10": [  # Deep skin tones
                {
                    "id": "makeup_010",
                    "name": "Rich Espresso Foundation",
                    "brand": "Deep Beauty",
                    "price": 42.99,
                    "category": "makeup",
                    "sub_category": "foundation",
                    "skin_tone_compatibility": ["8", "9", "10"],
                    "rating": 4.9,
                    "review_count": 567,
                    "image_url": "https://example.com/foundation_deep.jpg",
                    "description": "Flawless coverage for deep skin tones"
                },
                {
                    "id": "makeup_011",
                    "name": "Golden Highlight",
                    "brand": "Glow Beauty",
                    "price": 31.99,
                    "category": "makeup",
                    "sub_category": "highlighter",
                    "skin_tone_compatibility": ["7", "8", "9", "10"],
                    "rating": 4.8,
                    "review_count": 193,
                    "image_url": "https://example.com/highlight_golden.jpg",
                    "description": "Radiant golden glow for deep complexions"
                }
            ]
        },
        "clothing": {
            "1": [
                {
                    "id": "clothing_001",
                    "name": "Coral Summer Dress",
                    "brand": "Fashion Forward",
                    "price": 89.99,
                    "category": "clothing",
                    "sub_category": "dress",
                    "skin_tone_compatibility": ["1", "2", "3"],
                    "rating": 4.3,
                    "review_count": 78,
                    "image_url": "https://example.com/dress_coral.jpg",
                    "description": "Beautiful coral dress perfect for light skin"
                }
            ],
            "5": [
                {
                    "id": "clothing_005",
                    "name": "Emerald Green Blouse",
                    "brand": "Style House",
                    "price": 65.99,
                    "category": "clothing",
                    "sub_category": "blouse",
                    "skin_tone_compatibility": ["4", "5", "6"],
                    "rating": 4.5,
                    "review_count": 142,
                    "image_url": "https://example.com/blouse_emerald.jpg",
                    "description": "Stunning emerald blouse for medium tones"
                }
            ],
            "10": [
                {
                    "id": "clothing_010",
                    "name": "Golden Silk Scarf",
                    "brand": "Luxury Accessories",
                    "price": 125.99,
                    "category": "clothing",
                    "sub_category": "accessory",
                    "skin_tone_compatibility": ["8", "9", "10"],
                    "rating": 4.7,
                    "review_count": 89,
                    "image_url": "https://example.com/scarf_golden.jpg",
                    "description": "Luxurious golden scarf for deep skin tones"
                }
            ]
        }
    }
    
    # Get products for the specific category and skin tone
    if category in PRODUCT_DATABASE and skin_tone in PRODUCT_DATABASE[category]:
        return PRODUCT_DATABASE[category][skin_tone]
    
    # Fallback to medium tone products
    if category in PRODUCT_DATABASE and "5" in PRODUCT_DATABASE[category]:
        return PRODUCT_DATABASE[category]["5"]
    
    # Ultimate fallback
    return []

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
        # Check cache first
        cached_products = await get_cached_products(skin_tone, category, limit, page)
        if cached_products:
            logger.info(f"Returning cached products for {skin_tone}:{category}")
            return ProductResponse(
                products=cached_products,
                total_count=len(cached_products),
                timestamp=datetime.utcnow().isoformat()
            )
        
        # Get products from mock database
        products = get_mock_products_by_criteria(skin_tone, category)
        
        # Apply pagination
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_products = products[start_idx:end_idx]
        
        # Add compatibility scoring
        for product in paginated_products:
            product['compatibility_score'] = 0.95 if skin_tone in product.get('skin_tone_compatibility', []) else 0.7
            product['recommended_for_skin_tone'] = skin_tone
            product['fetched_at'] = datetime.utcnow().isoformat()
        
        # Cache the results
        await cache_products(skin_tone, category, limit, page, paginated_products)
        
        logger.info(f"Retrieved {len(paginated_products)} products for {skin_tone}:{category}")
        
        return ProductResponse(
            products=paginated_products,
            total_count=len(products),
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        logger.error(f"Error getting products: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Product search failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
