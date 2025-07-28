"""
Product domain entity for AI Fashion platform.
"""
from dataclasses import dataclass
from typing import List, Optional, Dict
from datetime import datetime


@dataclass
class Product:
    """Domain entity representing a fashion product."""
    
    id: Optional[str] = None
    name: str = ""
    brand: str = ""
    category: str = ""  # makeup, outfit, accessory
    sub_category: str = ""  # lipstick, foundation, dress, etc.
    price: float = 0.0
    currency: str = "USD"
    colors: List[str] = None  # Available colors
    image_url: str = ""
    description: str = ""
    availability: bool = True
    rating: float = 0.0
    review_count: int = 0
    tags: List[str] = None
    attributes: Dict[str, str] = None  # Size, material, etc.
    skin_tone_compatibility: List[str] = None  # Compatible monk skin tones
    seasonal_appropriateness: List[str] = None  # Spring, Summer, etc.
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.colors is None:
            self.colors = []
        if self.tags is None:
            self.tags = []
        if self.attributes is None:
            self.attributes = {}
        if self.skin_tone_compatibility is None:
            self.skin_tone_compatibility = []
        if self.seasonal_appropriateness is None:
            self.seasonal_appropriateness = []
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    def validate(self) -> bool:
        """Validate the product data."""
        if not self.name or not self.brand:
            return False
        if self.price < 0:
            return False
        if not (0.0 <= self.rating <= 5.0):
            return False
        if self.review_count < 0:
            return False
        return True
    
    def is_compatible_with_skin_tone(self, monk_tone: str) -> bool:
        """Check if product is compatible with given skin tone."""
        if not self.skin_tone_compatibility:
            return True  # If not specified, assume compatible
        return monk_tone in self.skin_tone_compatibility
    
    def is_seasonal_appropriate(self, season: str) -> bool:
        """Check if product is appropriate for given season."""
        if not self.seasonal_appropriateness:
            return True  # If not specified, assume year-round
        return season.lower() in [s.lower() for s in self.seasonal_appropriateness]
    
    def calculate_compatibility_score(self, monk_tone: str, season: str) -> float:
        """Calculate overall compatibility score."""
        score = 0.0
        factors = 0
        
        # Base rating factor
        if self.rating > 0:
            score += (self.rating / 5.0) * 0.3
            factors += 0.3
        
        # Skin tone compatibility
        if self.is_compatible_with_skin_tone(monk_tone):
            score += 0.4
        factors += 0.4
        
        # Seasonal appropriateness
        if self.is_seasonal_appropriate(season):
            score += 0.3
        factors += 0.3
        
        return score / factors if factors > 0 else 0.0
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'brand': self.brand,
            'category': self.category,
            'sub_category': self.sub_category,
            'price': self.price,
            'currency': self.currency,
            'colors': self.colors,
            'image_url': self.image_url,
            'description': self.description,
            'availability': self.availability,
            'rating': self.rating,
            'review_count': self.review_count,
            'tags': self.tags,
            'attributes': self.attributes,
            'skin_tone_compatibility': self.skin_tone_compatibility,
            'seasonal_appropriateness': self.seasonal_appropriateness,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
