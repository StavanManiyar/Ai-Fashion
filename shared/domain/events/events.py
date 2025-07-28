"""
Classes representing domain events for the AI Fashion platform.
"""

from datetime import datetime

class SkinToneAnalyzedEvent:
    def __init__(self, analysis, user_id):
        self.analysis = analysis
        self.user_id = user_id
        self.timestamp = datetime.utcnow()

class ColorRecommendationRequestedEvent:
    def __init__(self, skin_tone, user_preferences):
        self.skin_tone = skin_tone
        self.user_preferences = user_preferences
        self.timestamp = datetime.utcnow()
