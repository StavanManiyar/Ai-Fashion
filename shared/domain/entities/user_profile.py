"""
User Profile Domain Entity for AI Fashion Platform
Implements clean architecture domain layer for user personalization
"""
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class StylePreference(Enum):
    CASUAL = "casual"
    FORMAL = "formal"
    TRENDY = "trendy"
    CLASSIC = "classic"
    BOHEMIAN = "bohemian"
    MINIMALIST = "minimalist"


class SkinUndertone(Enum):
    WARM = "warm"
    COOL = "cool"
    NEUTRAL = "neutral"


@dataclass
class ColorPreference:
    """User's color preferences and history"""
    liked_colors: List[str]
    disliked_colors: List[str]
    preferred_seasons: List[str]
    confidence_score: float
    
    def __post_init__(self):
        if not 0 <= self.confidence_score <= 1:
            raise ValueError("Confidence score must be between 0 and 1")


@dataclass
class UserProfile:
    """Core user profile entity containing preferences and behavior data"""
    user_id: str
    skin_tone_analysis: Optional[Dict]
    color_preferences: Optional[ColorPreference]
    style_preferences: List[StylePreference]
    size_preferences: Dict[str, str]  # {"tops": "M", "bottoms": "L", etc.}
    budget_range: tuple[float, float]  # (min, max)
    preferred_brands: List[str]
    interaction_history: List[Dict]
    created_at: datetime
    updated_at: datetime
    
    def __post_init__(self):
        self.validate()
    
    def validate(self):
        """Validate user profile data"""
        if not self.user_id:
            raise ValueError("User ID cannot be empty")
        
        if self.budget_range[0] < 0 or self.budget_range[1] < self.budget_range[0]:
            raise ValueError("Invalid budget range")
        
        if not self.style_preferences:
            self.style_preferences = [StylePreference.CASUAL]  # Default
    
    def add_interaction(self, interaction: Dict):
        """Add user interaction to history"""
        interaction['timestamp'] = datetime.utcnow()
        self.interaction_history.append(interaction)
        self.updated_at = datetime.utcnow()
        
        # Keep only last 100 interactions
        if len(self.interaction_history) > 100:
            self.interaction_history = self.interaction_history[-100:]
    
    def update_color_preferences(self, liked_color: str = None, disliked_color: str = None):
        """Update color preferences based on user feedback"""
        if not self.color_preferences:
            self.color_preferences = ColorPreference([], [], [], 0.5)
        
        if liked_color and liked_color not in self.color_preferences.liked_colors:
            self.color_preferences.liked_colors.append(liked_color)
            # Remove from disliked if present
            if liked_color in self.color_preferences.disliked_colors:
                self.color_preferences.disliked_colors.remove(liked_color)
        
        if disliked_color and disliked_color not in self.color_preferences.disliked_colors:
            self.color_preferences.disliked_colors.append(disliked_color)
            # Remove from liked if present
            if disliked_color in self.color_preferences.liked_colors:
                self.color_preferences.liked_colors.remove(disliked_color)
        
        self.updated_at = datetime.utcnow()
    
    def get_preference_vector(self) -> Dict:
        """Generate a preference vector for ML recommendations"""
        return {
            'style_preferences': [pref.value for pref in self.style_preferences],
            'liked_colors': self.color_preferences.liked_colors if self.color_preferences else [],
            'disliked_colors': self.color_preferences.disliked_colors if self.color_preferences else [],
            'budget_min': self.budget_range[0],
            'budget_max': self.budget_range[1],
            'preferred_brands': self.preferred_brands,
            'interaction_count': len(self.interaction_history)
        }
