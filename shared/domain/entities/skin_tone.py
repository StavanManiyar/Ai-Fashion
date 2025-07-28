"""
Domain entity for skin tone analysis
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime
import re


@dataclass(frozen=True)
class SkinTone:
    """Immutable skin tone entity representing analyzed skin tone data"""
    
    monk_scale: str
    hex_color: str
    confidence: float
    season_type: Optional[str] = None
    undertone: Optional[str] = None
    analysis_timestamp: datetime = None
    
    def __post_init__(self):
        """Validate skin tone data after initialization"""
        if self.analysis_timestamp is None:
            object.__setattr__(self, 'analysis_timestamp', datetime.utcnow())
        
        self._validate()
    
    def _validate(self):
        """Validate skin tone data integrity"""
        # Validate Monk scale (MST1-MST10)
        if not re.match(r'^(Monk|MST)\d{1,2}$', self.monk_scale):
            raise ValueError(f"Invalid Monk scale format: {self.monk_scale}")
        
        # Validate hex color
        if not re.match(r'^#[0-9A-Fa-f]{6}$', self.hex_color):
            raise ValueError(f"Invalid hex color format: {self.hex_color}")
        
        # Validate confidence score
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got: {self.confidence}")
        
        # Validate season type if provided
        valid_seasons = ['Spring', 'Summer', 'Autumn', 'Winter', 'Clear Spring', 'Warm Spring', 'Light Spring']
        if self.season_type and self.season_type not in valid_seasons:
            raise ValueError(f"Invalid season type: {self.season_type}")
        
        # Validate undertone if provided
        valid_undertones = ['warm', 'cool', 'neutral']
        if self.undertone and self.undertone not in valid_undertones:
            raise ValueError(f"Invalid undertone: {self.undertone}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'monk_scale': self.monk_scale,
            'hex_color': self.hex_color,
            'confidence': self.confidence,
            'season_type': self.season_type,
            'undertone': self.undertone,
            'analysis_timestamp': self.analysis_timestamp.isoformat() if self.analysis_timestamp else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SkinTone':
        """Create SkinTone from dictionary"""
        timestamp = None
        if data.get('analysis_timestamp'):
            timestamp = datetime.fromisoformat(data['analysis_timestamp'])
        
        return cls(
            monk_scale=data['monk_scale'],
            hex_color=data['hex_color'],
            confidence=data['confidence'],
            season_type=data.get('season_type'),
            undertone=data.get('undertone'),
            analysis_timestamp=timestamp
        )
    
    def get_monk_number(self) -> int:
        """Extract numeric value from Monk scale"""
        import re
        match = re.search(r'\d+', self.monk_scale)
        return int(match.group()) if match else 1
    
    def is_light_skin(self) -> bool:
        """Check if skin tone is considered light (MST 1-4)"""
        return self.get_monk_number() <= 4
    
    def is_medium_skin(self) -> bool:
        """Check if skin tone is considered medium (MST 5-7)"""
        monk_num = self.get_monk_number()
        return 5 <= monk_num <= 7
    
    def is_dark_skin(self) -> bool:
        """Check if skin tone is considered dark (MST 8-10)"""
        return self.get_monk_number() >= 8


@dataclass(frozen=True)
class ColorRecommendation:
    """Color recommendation entity"""
    
    hex_color: str
    color_name: str
    confidence: float
    category: str  # 'clothing', 'makeup', 'accessories'
    match_reason: str
    contrast_ratio: Optional[float] = None
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self):
        """Validate color recommendation data"""
        if not re.match(r'^#[0-9A-Fa-f]{6}$', self.hex_color):
            raise ValueError(f"Invalid hex color format: {self.hex_color}")
        
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got: {self.confidence}")
        
        valid_categories = ['clothing', 'makeup', 'accessories', 'general']
        if self.category not in valid_categories:
            raise ValueError(f"Invalid category: {self.category}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'hex_color': self.hex_color,
            'color_name': self.color_name,
            'confidence': self.confidence,
            'category': self.category,
            'match_reason': self.match_reason,
            'contrast_ratio': self.contrast_ratio
        }


@dataclass(frozen=True)
class ColorPalette:
    """Color palette entity for seasonal/style recommendations"""
    
    palette_id: str
    name: str
    season_type: str
    colors: list[ColorRecommendation]
    description: Optional[str] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            object.__setattr__(self, 'created_at', datetime.utcnow())
        self._validate()
    
    def _validate(self):
        """Validate color palette data"""
        if not self.colors:
            raise ValueError("Color palette must contain at least one color")
        
        if len(self.colors) > 50:
            raise ValueError("Color palette cannot contain more than 50 colors")
    
    def get_colors_by_category(self, category: str) -> list[ColorRecommendation]:
        """Get colors filtered by category"""
        return [color for color in self.colors if color.category == category]
    
    def get_top_colors(self, limit: int = 10) -> list[ColorRecommendation]:
        """Get top colors sorted by confidence"""
        return sorted(self.colors, key=lambda x: x.confidence, reverse=True)[:limit]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'palette_id': self.palette_id,
            'name': self.name,
            'season_type': self.season_type,
            'colors': [color.to_dict() for color in self.colors],
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
