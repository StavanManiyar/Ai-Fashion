"""Shared domain entities for AI Fashion platform."""

from .user_profile import UserProfile
from .skin_tone import SkinTone, SkinToneAnalysis
from .color_recommendation import ColorRecommendation
from .product import Product

__all__ = [
    'UserProfile',
    'SkinTone', 
    'SkinToneAnalysis',
    'ColorRecommendation',
    'Product'
]
