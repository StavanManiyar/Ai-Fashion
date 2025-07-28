"""
Skin Tone Analyzer - AI-powered skin tone detection and analysis
"""
import cv2
import numpy as np
from PIL import Image
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class SkinToneAnalyzer:
    """
    Analyzes skin tone from processed images using computer vision and ML
    """
    
    def __init__(self):
        """Initialize the skin tone analyzer with ML models and reference data"""
        self.monk_scale_colors = {
            "Monk01": "#F6EDE4",
            "Monk02": "#F3E7DB", 
            "Monk03": "#F7EAD0",
            "Monk04": "#EADABA",
            "Monk05": "#D08B5B",
            "Monk06": "#AE5D29",
            "Monk07": "#8D4A21",
            "Monk08": "#714D3A",
            "Monk09": "#5D4037",
            "Monk10": "#3E2723"
        }
        
        self.seasonal_mapping = {
            "Monk01": "Light Spring",
            "Monk02": "Light Spring", 
            "Monk03": "Clear Spring",
            "Monk04": "Warm Spring",
            "Monk05": "Warm Autumn",
            "Monk06": "Deep Autumn",
            "Monk07": "Deep Autumn",
            "Monk08": "Deep Winter",
            "Monk09": "Deep Winter",
            "Monk10": "Deep Winter"
        }
        
        self.undertone_mapping = {
            "Monk01": "cool",
            "Monk02": "neutral", 
            "Monk03": "warm",
            "Monk04": "warm",
            "Monk05": "warm",
            "Monk06": "warm",
            "Monk07": "neutral",
            "Monk08": "cool",
            "Monk09": "cool",
            "Monk10": "neutral"
        }

    async def analyze_skin_tone(self, image: Image.Image) -> Dict[str, Any]:
        """
        Analyze skin tone from processed image
        """
        try:
            # Convert PIL image to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Detect skin regions
            skin_mask = self._detect_skin_regions(cv_image)
            
            if skin_mask is None or np.sum(skin_mask) == 0:
                logger.warning("No skin regions detected in image")
                return self._get_default_result()
            
            # Extract average skin color
            average_color = self._extract_average_skin_color(cv_image, skin_mask)
            
            # Convert to hex color
            hex_color = self._rgb_to_hex(average_color)
            
            # Map to Monk scale
            monk_scale, confidence = self._map_to_monk_scale(average_color)
            
            # Get seasonal type and undertone
            season_type = self.seasonal_mapping.get(monk_scale, "Unknown")
            undertone = self.undertone_mapping.get(monk_scale, "neutral")
            
            result = {
                'monk_scale': monk_scale,
                'hex_color': hex_color,
                'confidence': confidence,
                'season_type': season_type,
                'undertone': undertone,
                'rgb_values': {
                    'r': int(average_color[0]),
                    'g': int(average_color[1]),
                    'b': int(average_color[2])
                }
            }
            
            logger.info(f"Skin tone analysis completed: {monk_scale} with confidence {confidence:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Error in skin tone analysis: {str(e)}")
            return self._get_default_result()

    def _detect_skin_regions(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Detect skin regions in the image using color space analysis
        """
        try:
            # Convert to different color spaces for better skin detection
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
            
            # Define skin color ranges in HSV
            lower_hsv = np.array([0, 20, 70], dtype=np.uint8)
            upper_hsv = np.array([20, 255, 255], dtype=np.uint8)
            
            # Define skin color ranges in YCrCb
            lower_ycrcb = np.array([0, 135, 85], dtype=np.uint8)
            upper_ycrcb = np.array([255, 180, 135], dtype=np.uint8)
            
            # Create masks
            mask_hsv = cv2.inRange(hsv, lower_hsv, upper_hsv)
            mask_ycrcb = cv2.inRange(ycrcb, lower_ycrcb, upper_ycrcb)
            
            # Combine masks
            skin_mask = cv2.bitwise_and(mask_hsv, mask_ycrcb)
            
            # Apply morphological operations to clean up the mask
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
            skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_OPEN, kernel)
            skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_CLOSE, kernel)
            
            # Apply Gaussian blur to smooth the mask
            skin_mask = cv2.GaussianBlur(skin_mask, (3, 3), 0)
            
            return skin_mask
            
        except Exception as e:
            logger.error(f"Error detecting skin regions: {str(e)}")
            return None

    def _extract_average_skin_color(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """
        Extract average color from detected skin regions
        """
        try:
            # Apply mask to image
            skin_pixels = image[mask > 0]
            
            if len(skin_pixels) == 0:
                # Fallback to center region if no skin detected
                h, w = image.shape[:2]
                center_region = image[h//4:3*h//4, w//4:3*w//4]
                return np.mean(center_region.reshape(-1, 3), axis=0)
            
            # Calculate average color (BGR format)
            average_bgr = np.mean(skin_pixels, axis=0)
            
            # Convert BGR to RGB
            average_rgb = np.array([average_bgr[2], average_bgr[1], average_bgr[0]])
            
            return average_rgb
            
        except Exception as e:
            logger.error(f"Error extracting average skin color: {str(e)}")
            return np.array([200, 180, 160])  # Default skin color

    def _rgb_to_hex(self, rgb: np.ndarray) -> str:
        """Convert RGB values to hex color string"""
        return "#{:02x}{:02x}{:02x}".format(int(rgb[0]), int(rgb[1]), int(rgb[2]))

    def _map_to_monk_scale(self, rgb_color: np.ndarray) -> tuple[str, float]:
        """
        Map RGB color to closest Monk scale value
        """
        try:
            min_distance = float('inf')
            closest_monk = "Monk05"
            
            for monk_scale, hex_color in self.monk_scale_colors.items():
                # Convert hex to RGB
                reference_rgb = np.array([
                    int(hex_color[1:3], 16),
                    int(hex_color[3:5], 16),
                    int(hex_color[5:7], 16)
                ])
                
                # Calculate Euclidean distance in RGB space
                distance = np.linalg.norm(rgb_color - reference_rgb)
                
                if distance < min_distance:
                    min_distance = distance
                    closest_monk = monk_scale
            
            # Calculate confidence based on distance (closer = higher confidence)
            # Normalize distance to confidence score (0.5 to 1.0)
            max_possible_distance = np.sqrt(3 * 255**2)  # Maximum RGB distance
            confidence = 1.0 - (min_distance / max_possible_distance)
            confidence = max(0.5, min(1.0, confidence))  # Clamp between 0.5 and 1.0
            
            return closest_monk, confidence
            
        except Exception as e:
            logger.error(f"Error mapping to Monk scale: {str(e)}")
            return "Monk05", 0.5

    def _get_default_result(self) -> Dict[str, Any]:
        """Return default skin tone analysis result"""
        return {
            'monk_scale': 'Monk05',
            'hex_color': '#D08B5B',
            'confidence': 0.5,
            'season_type': 'Warm Autumn',
            'undertone': 'warm',
            'rgb_values': {'r': 208, 'g': 139, 'b': 91}
        }

    def get_supported_monk_scales(self) -> list[str]:
        """Return list of supported Monk scale values"""
        return list(self.monk_scale_colors.keys())

    def get_monk_scale_color(self, monk_scale: str) -> Optional[str]:
        """Get hex color for a specific Monk scale value"""
        return self.monk_scale_colors.get(monk_scale)
