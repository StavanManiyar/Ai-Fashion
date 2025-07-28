"""
OpenCV implementation of the image processor interface.
"""
import cv2
import numpy as np
from typing import Dict, Any
from shared.domain.entities.skin_tone import SkinToneAnalysis


class ProcessedImage:
    """Represents a processed image with metadata."""
    
    def __init__(self, image_array: np.ndarray, metadata: Dict[str, Any]):
        self.image_array = image_array
        self.metadata = metadata


class OpenCVImageProcessor:
    """OpenCV-based implementation of image processing."""
    
    async def process(self, image_data: bytes) -> ProcessedImage:
        """Process raw image data using OpenCV."""
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_data, np.uint8)
        
        # Decode image
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise ValueError("Invalid image data")
        
        # Apply basic preprocessing
        # Convert to RGB (OpenCV loads as BGR by default)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Apply CLAHE for better contrast
        lab = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab)
        
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l_channel = clahe.apply(l_channel)
        
        processed = cv2.merge([l_channel, a_channel, b_channel])
        processed_rgb = cv2.cvtColor(processed, cv2.COLOR_LAB2RGB)
        
        metadata = {
            'original_shape': image.shape,
            'processed_shape': processed_rgb.shape,
            'color_space': 'RGB'
        }
        
        return ProcessedImage(processed_rgb, metadata)
    
    async def analyze_skin_tone(self, processed_image: ProcessedImage) -> SkinToneAnalysis:
        """Analyze skin tone from processed image."""
        image = processed_image.image_array
        
        # Simple skin tone detection (this is a basic implementation)
        # In practice, you'd use more sophisticated ML models
        
        # Convert to different color spaces for analysis
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        
        # Define skin color range in HSV
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        
        # Create skin mask
        skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
        
        # Extract skin pixels
        skin_pixels = image[skin_mask > 0]
        
        if len(skin_pixels) == 0:
            # Fallback: use center region of image
            h, w = image.shape[:2]
            center_region = image[h//4:3*h//4, w//4:3*w//4]
            skin_pixels = center_region.reshape(-1, 3)
        
        # Calculate average color
        avg_color = np.mean(skin_pixels, axis=0)
        
        # Convert to hex color
        hex_color = '#{:02x}{:02x}{:02x}'.format(
            int(avg_color[0]), int(avg_color[1]), int(avg_color[2])
        )
        
        # Simple Monk tone mapping (this would be more sophisticated in practice)
        monk_tone = self._map_to_monk_scale(avg_color)
        
        # Calculate confidence based on skin pixel coverage
        confidence = min(len(skin_pixels) / (image.shape[0] * image.shape[1]) * 10, 1.0)
        
        return SkinToneAnalysis(
            monk_tone=monk_tone,
            confidence=confidence,
            hex_color=hex_color,
            rgb_values=avg_color.tolist()
        )
    
    def _map_to_monk_scale(self, rgb_color: np.ndarray) -> str:
        """Map RGB color to Monk skin tone scale."""
        # This is a simplified mapping - in practice you'd use ML models
        # or more sophisticated color science
        
        # Calculate luminance
        luminance = 0.299 * rgb_color[0] + 0.587 * rgb_color[1] + 0.114 * rgb_color[2]
        
        # Map to Monk scale (1-10)
        if luminance < 50:
            return "10"  # Darker tones
        elif luminance < 80:
            return "9"
        elif luminance < 110:
            return "8"
        elif luminance < 140:
            return "7"
        elif luminance < 170:
            return "6"
        elif luminance < 200:
            return "5"
        elif luminance < 220:
            return "4"
        elif luminance < 240:
            return "3"
        elif luminance < 250:
            return "2"
        else:
            return "1"  # Lighter tones
