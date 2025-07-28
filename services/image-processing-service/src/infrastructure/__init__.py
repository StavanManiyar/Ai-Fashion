"""Infrastructure layer for image processing service"""

from .opencv_image_processor import OpenCVImageProcessor
from .postgres_skin_tone_repository import PostgresSkinToneRepository

__all__ = [
    'OpenCVImageProcessor',
    'PostgresSkinToneRepository'
]
