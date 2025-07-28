"""
Color recommendation domain entity for AI Fashion platform.
"""
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class ColorRecommendation:
    """Domain entity representing a color recommendation."""
    
    id: Optional[str] = None
    hex_color: str = ""
    color_name: str = ""
    season: str = ""  # Spring, Summer, Autumn, Winter
    category: str = ""  # Primary, Secondary, Accent
    confidence_score: float = 0.0
    skin_tone_compatibility: float = 0.0
    complementary_colors: List[str] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.complementary_colors is None:
            self.complementary_colors = []
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    def validate(self) -> bool:
        """Validate the color recommendation data."""
        if not self.hex_color or not self.hex_color.startswith('#'):
            return False
        if not (0.0 <= self.confidence_score <= 1.0):
            return False
        if not (0.0 <= self.skin_tone_compatibility <= 1.0):
            return False
        return True
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'id': self.id,
            'hex_color': self.hex_color,
            'color_name': self.color_name,
            'season': self.season,
            'category': self.category,
            'confidence_score': self.confidence_score,
            'skin_tone_compatibility': self.skin_tone_compatibility,
            'complementary_colors': self.complementary_colors,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
