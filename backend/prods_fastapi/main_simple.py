# Simplified FastAPI application for Render deployment
from fastapi import FastAPI, Query, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import json
import math
import os
from typing import List, Optional, Dict
import numpy as np
import cv2
from webcolors import hex_to_rgb, rgb_to_hex
import io
from PIL import Image
import logging
import random
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Fashion Backend",
    version="1.0.0",
    description="AI Fashion recommendation system with skin tone analysis"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Monk skin tone scale
MONK_SKIN_TONES = {
    'Monk 1': '#f6ede4',
    'Monk 2': '#f3e7db', 
    'Monk 3': '#f7ead0',
    'Monk 4': '#eadaba',
    'Monk 5': '#d7bd96',
    'Monk 6': '#a07e56',
    'Monk 7': '#825c43',
    'Monk 8': '#604134',
    'Monk 9': '#3a312a',
    'Monk 10': '#292420'
}

# Basic color mapping
color_mapping = {
    "Red": "Red",
    "Blue": "Blue", 
    "Green": "Green",
    "Black": "Black",
    "White": "White",
    "Pink": "Pink",
    "Yellow": "Yellow",
    "Purple": "Purple",
    "Orange": "Orange",
    "Brown": "Brown"
}

@app.get("/")
def home():
    return {"message": "Welcome to the AI Fashion API!", "status": "healthy"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "AI Fashion Backend is running"}

@app.get("/color-suggestions")
def get_color_suggestions(skin_tone: str = Query(None)):
    """Get color suggestions for a specific skin tone."""
    suggestions = [
        {"skin_tone": "Fair", "suitable_colors": "Navy Blue, Emerald Green, Ruby Red, Cool Pink"},
        {"skin_tone": "Medium", "suitable_colors": "Warm Brown, Orange, Coral, Olive Green"},
        {"skin_tone": "Dark", "suitable_colors": "Bright Yellow, Royal Blue, Magenta, White"},
        {"skin_tone": "Deep", "suitable_colors": "Vibrant Colors, Jewel Tones, Bright Contrasts"}
    ]
    
    if skin_tone:
        filtered = [s for s in suggestions if skin_tone.lower() in s["skin_tone"].lower()]
        return {"data": filtered, "total_items": len(filtered)}
    
    return {"data": suggestions, "total_items": len(suggestions)}

@app.get("/data/")
def get_makeup_data(
    mst: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(24, ge=1, le=100)
):
    """Get makeup products with pagination."""
    # Generate sample makeup products
    brands = ["Fenty Beauty", "MAC", "NARS", "Maybelline", "L'Oreal", "Dior"]
    products = ["Foundation", "Concealer", "Lipstick", "Mascara", "Blush", "Highlighter"]
    
    sample_data = []
    for i in range(100):  # Generate 100 sample products
        brand = random.choice(brands)
        product_type = random.choice(products)
        price = f"${random.randint(15, 50)}.{random.randint(10, 99)}"
        
        sample_data.append({
            "product_name": f"{brand} {product_type}",
            "brand": brand,
            "price": price,
            "image_url": f"https://via.placeholder.com/150/FF{random.randint(1000, 9999)}/FFFFFF?text={brand.replace(' ', '+')}",
            "mst": mst or f"Monk{random.randint(1, 10):02d}",
            "desc": f"Beautiful {product_type.lower()} from {brand}"
        })
    
    # Apply pagination
    total_items = len(sample_data)
    total_pages = math.ceil(total_items / limit)
    start_idx = (page - 1) * limit
    end_idx = min(start_idx + limit, total_items)
    
    paginated_data = sample_data[start_idx:end_idx]
    
    return {
        "data": paginated_data,
        "total_items": total_items,
        "total_pages": total_pages,
        "page": page,
        "limit": limit
    }

@app.get("/apparel")
def get_apparel(
    gender: str = Query(None),
    color: List[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(24, ge=1, le=100)
):
    """Get apparel products."""
    # Generate sample apparel
    brands = ["H&M", "Zara", "Nike", "Adidas", "Uniqlo", "Gap"]
    types = ["T-Shirt", "Jeans", "Dress", "Jacket", "Sweater", "Pants"]
    colors = ["Black", "White", "Blue", "Red", "Green", "Gray"]
    
    sample_data = []
    for i in range(50):
        brand = random.choice(brands)
        product_type = random.choice(types)
        base_color = random.choice(colors)
        price = f"${random.randint(20, 80)}.{random.randint(10, 99)}"
        
        sample_data.append({
            "Product Name": f"{brand} {product_type}",
            "Price": price,
            "Image URL": f"https://via.placeholder.com/150/{random.randint(100000, 999999)}/FFFFFF?text={product_type.replace(' ', '+')}",
            "Product Type": product_type,
            "baseColour": base_color,
            "brand": brand,
            "gender": gender or random.choice(["Men", "Women", "Unisex"])
        })
    
    # Apply pagination
    total_items = len(sample_data)
    total_pages = math.ceil(total_items / limit)
    start_idx = (page - 1) * limit
    end_idx = min(start_idx + limit, total_items)
    
    paginated_data = sample_data[start_idx:end_idx]
    
    return {
        "data": paginated_data,
        "page": page,
        "limit": limit,
        "total_items": total_items,
        "total_pages": total_pages
    }

@app.get("/api/color-recommendations")
async def get_color_recommendations(
    skin_tone: str = Query(None),
    hex_color: str = Query(None)
):
    """Get color recommendations based on skin tone."""
    
    # Default color recommendations
    color_palettes = {
        "Monk01": [
            {"name": "Soft Pink", "hex": "#FFB6C1"},
            {"name": "Light Blue", "hex": "#ADD8E6"},
            {"name": "Cream", "hex": "#F5F5DC"},
            {"name": "Lavender", "hex": "#E6E6FA"}
        ],
        "Monk05": [
            {"name": "Warm Coral", "hex": "#FF7F50"},
            {"name": "Golden Yellow", "hex": "#FFD700"},
            {"name": "Olive Green", "hex": "#808000"},
            {"name": "Rust", "hex": "#B7410E"}
        ],
        "Monk10": [
            {"name": "Bright Yellow", "hex": "#FFFF00"},
            {"name": "Royal Blue", "hex": "#4169E1"},
            {"name": "Emerald Green", "hex": "#50C878"},
            {"name": "Magenta", "hex": "#FF00FF"}
        ]
    }
    
    # Default universal colors
    default_colors = [
        {"name": "Navy Blue", "hex": "#000080"},
        {"name": "Forest Green", "hex": "#228B22"},
        {"name": "Burgundy", "hex": "#800020"},
        {"name": "Charcoal Gray", "hex": "#36454F"},
        {"name": "Cream White", "hex": "#F5F5DC"},
        {"name": "Soft Pink", "hex": "#FFB6C1"}
    ]
    
    # Determine which colors to return
    if skin_tone and skin_tone in color_palettes:
        colors = color_palettes[skin_tone]
    else:
        colors = default_colors
    
    return {
        "colors_that_suit": colors,
        "seasonal_type": "Universal",
        "monk_skin_tone": skin_tone,
        "message": "Color recommendations based on your skin tone"
    }

def advanced_preprocessing(image_array: np.ndarray) -> np.ndarray:
    """Advanced image preprocessing with multiple techniques for optimal skin tone detection."""
    try:
        # 1. Noise reduction using bilateral filter
        denoised = cv2.bilateralFilter(image_array, 9, 75, 75)
        
        # 2. White balance correction using Gray World assumption
        balanced = apply_white_balance(denoised)
        
        # 3. Multi-scale CLAHE in LAB color space
        lab_corrected = apply_advanced_clahe(balanced)
        
        # 4. Shadow removal and illumination normalization
        shadow_removed = remove_shadows(lab_corrected)
        
        # 5. Color cast removal
        color_corrected = remove_color_cast(shadow_removed)
        
        return color_corrected
        
    except Exception as e:
        logger.warning(f"Advanced preprocessing failed: {e}, using original image")
        return image_array

def apply_white_balance(image: np.ndarray) -> np.ndarray:
    """Apply white balance correction using multiple methods."""
    # Gray World White Balance
    result = image.copy().astype(np.float32)
    
    # Calculate mean for each channel
    mean_r = np.mean(result[:, :, 0])
    mean_g = np.mean(result[:, :, 1]) 
    mean_b = np.mean(result[:, :, 2])
    
    # Calculate overall mean
    mean_gray = (mean_r + mean_g + mean_b) / 3
    
    # Apply correction
    if mean_r > 0: result[:, :, 0] *= mean_gray / mean_r
    if mean_g > 0: result[:, :, 1] *= mean_gray / mean_g
    if mean_b > 0: result[:, :, 2] *= mean_gray / mean_b
    
    # Von Kries chromatic adaptation for fine-tuning
    result = apply_von_kries_adaptation(result)
    
    return np.clip(result, 0, 255).astype(np.uint8)

def apply_von_kries_adaptation(image: np.ndarray) -> np.ndarray:
    """Apply Von Kries chromatic adaptation for better color constancy."""
    # Convert to XYZ color space
    xyz = cv2.cvtColor(image.astype(np.uint8), cv2.COLOR_RGB2XYZ)
    xyz = xyz.astype(np.float32) / 255.0
    
    # Bradford adaptation matrix (more accurate than simple scaling)
    bradford_matrix = np.array([
        [0.8951, 0.2664, -0.1614],
        [-0.7502, 1.7135, 0.0367],
        [0.0389, -0.0685, 1.0296]
    ])
    
    # Apply adaptation (simplified for demonstration)
    adapted = np.dot(xyz.reshape(-1, 3), bradford_matrix.T)
    adapted = adapted.reshape(xyz.shape)
    
    # Convert back to RGB
    result = cv2.cvtColor((adapted * 255).astype(np.uint8), cv2.COLOR_XYZ2RGB)
    return result

def apply_advanced_clahe(image: np.ndarray) -> np.ndarray:
    """Apply fine-tuned CLAHE in LAB color space optimized for skin tones."""
    lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)
    
    # Calculate adaptive clip limit
    avg_brightness = np.mean(l_channel)
    
    if avg_brightness < 100:  # Adjust darker images more
        clip_limit = 4.0
        tile_grid_size = (8, 8)
    elif avg_brightness > 180:  # Adjust lighter images less
        clip_limit = 1.2
        tile_grid_size = (16, 16)
    else:
        clip_limit = 2.5
        tile_grid_size = (12, 12)
    
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    l_corrected = clahe.apply(l_channel)
    
    corrected_lab = cv2.merge([l_corrected, a_channel, b_channel])

    return cv2.cvtColor(corrected_lab, cv2.COLOR_LAB2RGB)

def remove_shadows(image: np.ndarray) -> np.ndarray:
    """Remove shadows using morphological operations and illumination estimation."""
    # Convert to grayscale for shadow detection
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    
    # Create illumination map using morphological opening
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    background = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
    
    # Estimate illumination
    background = cv2.medianBlur(background, 21)
    
    # Normalize illumination
    normalized = np.zeros_like(image, dtype=np.float32)
    for i in range(3):
        channel = image[:, :, i].astype(np.float32)
        # Avoid division by zero
        background_safe = np.maximum(background.astype(np.float32), 1.0)
        normalized[:, :, i] = (channel / background_safe) * 128
    
    return np.clip(normalized, 0, 255).astype(np.uint8)

def remove_color_cast(image: np.ndarray) -> np.ndarray:
    """Remove color cast using statistical color correction."""
    image_float = image.astype(np.float32)
    
    # Calculate color statistics
    for channel in range(3):
        channel_data = image_float[:, :, channel]
        
        # Remove extreme values (outliers)
        p1, p99 = np.percentile(channel_data, [1, 99])
        channel_data = np.clip(channel_data, p1, p99)
        
        # Normalize to full range
        channel_min, channel_max = channel_data.min(), channel_data.max()
        if channel_max > channel_min:
            image_float[:, :, channel] = ((channel_data - channel_min) /
                                        (channel_max - channel_min)) * 255
    
    return np.clip(image_float, 0, 255).astype(np.uint8)

def detect_face_regions(image_array: np.ndarray) -> List[tuple]:
    """Advanced face detection using multiple cascades and geometric analysis."""
    try:
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
        
        # Try multiple face detection methods
        face_regions = []
        
        # Method 1: Haar Cascade (if available)
        try:
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            for (x, y, w, h) in faces:
                face_regions.append((x, y, w, h))
        except:
            pass
        
        # Method 2: DNN-based detection (simplified)
        if not face_regions:
            # Fallback: geometric assumption for face region
            h, w = image_array.shape[:2]
            # Assume face is in center 60% of image
            face_x = int(w * 0.2)
            face_y = int(h * 0.15)
            face_w = int(w * 0.6)
            face_h = int(h * 0.7)
            face_regions.append((face_x, face_y, face_w, face_h))
        
        return face_regions
        
    except Exception as e:
        logger.warning(f"Face detection failed: {e}")
        # Return default face region
        h, w = image_array.shape[:2]
        return [(int(w*0.2), int(h*0.15), int(w*0.6), int(h*0.7))]

def extract_skin_pixels_advanced(image_array: np.ndarray, face_regions: List[tuple]) -> np.ndarray:
    """Extract skin pixels using multiple color space analysis and statistical methods."""
    all_skin_pixels = []
    
    for face_x, face_y, face_w, face_h in face_regions:
        # Extract face region
        face_region = image_array[face_y:face_y+face_h, face_x:face_x+face_w]
        
        if face_region.size == 0:
            continue
            
        # Method 1: RGB-based skin detection
        rgb_skin = detect_skin_rgb(face_region)
        
        # Method 2: HSV-based skin detection
        hsv_skin = detect_skin_hsv(face_region)
        
        # Method 3: YCrCb-based skin detection
        ycrcb_skin = detect_skin_ycrcb(face_region)
        
        # Combine all methods using intersection
        combined_mask = rgb_skin & hsv_skin & ycrcb_skin
        
        # If intersection is too restrictive, use union of best two
        if np.sum(combined_mask) < 100:
            combined_mask = rgb_skin | hsv_skin
        
        # Extract skin pixels
        if np.sum(combined_mask) > 50:
            skin_pixels = face_region[combined_mask]
            all_skin_pixels.extend(skin_pixels)
    
    return np.array(all_skin_pixels) if all_skin_pixels else np.array([])

def detect_skin_rgb(image: np.ndarray) -> np.ndarray:
    """Detect skin pixels using RGB color space rules optimized for all skin tones including very fair skin."""
    r, g, b = image[:, :, 0], image[:, :, 1], image[:, :, 2]
    
    # Calculate average brightness to adapt rules
    avg_brightness = np.mean([r, g, b])
    
    # For very fair skin (high brightness), use relaxed rules
    if avg_brightness > 200:
        # Very fair skin rules
        rule1 = (r >= g) & (g >= b)  # Allow equal values for very fair skin
        rule2 = (r > 180) & (g > 160) & (b > 140)  # Much higher thresholds for fair skin
        rule3 = True  # Skip contrast requirement for very fair skin
        rule4 = np.abs(r.astype(np.int16) - g.astype(np.int16)) >= 5  # Much lower difference requirement
        rule5 = (r >= g) & (r >= b)  # Allow equal values
        
        # Additional fair skin specific rules
        brightness_rule = (r + g + b) > 450  # Very bright pixels
        uniformity_rule = (np.maximum(np.maximum(r, g), b) - np.minimum(np.minimum(r, g), b)) < 40  # More uniform colors
        
        skin_mask = rule1 & rule2 & rule4 & rule5 & brightness_rule & uniformity_rule
        
    elif avg_brightness > 150:
        # Fair skin rules (relaxed)
        rule1 = (r > g) & (g >= b)  # Slightly relaxed
        rule2 = (r > 120) & (g > 80) & (b > 60)  # Lower thresholds for fair skin
        rule3 = (np.maximum(np.maximum(r, g), b) - np.minimum(np.minimum(r, g), b)) > 8  # Lower contrast requirement
        rule4 = np.abs(r.astype(np.int16) - g.astype(np.int16)) > 8  # Lower difference requirement
        rule5 = (r > g) & (r > b)
        
        skin_mask = rule1 & rule2 & rule3 & rule4 & rule5
        
    else:
        # Standard rules for medium to dark skin
        rule1 = (r > g) & (g > b)
        rule2 = (r > 95) & (g > 40) & (b > 20)
        rule3 = (np.maximum(np.maximum(r, g), b) - np.minimum(np.minimum(r, g), b)) > 15
        rule4 = np.abs(r.astype(np.int16) - g.astype(np.int16)) > 15
        rule5 = (r > g) & (r > b)
        
        skin_mask = rule1 & rule2 & rule3 & rule4 & rule5
    
    return skin_mask

def detect_skin_hsv(image: np.ndarray) -> np.ndarray:
    """Detect skin pixels using HSV color space."""
    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    h, s, v = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
    
    # HSV skin detection (Phung et al.)
    # Hue: 0-50 or 160-179 (wrapping around)
    hue_condition = ((h >= 0) & (h <= 50)) | ((h >= 160) & (h <= 179))
    
    # Saturation: 23-68 for different lighting conditions
    sat_condition = (s >= 23) & (s <= 68)
    
    # Value: greater than 35 to avoid very dark pixels
    val_condition = v >= 35
    
    skin_mask = hue_condition & sat_condition & val_condition
    
    return skin_mask

def detect_skin_ycrcb(image: np.ndarray) -> np.ndarray:
    """Detect skin pixels using YCrCb color space."""
    ycrcb = cv2.cvtColor(image, cv2.COLOR_RGB2YCrCb)
    y, cr, cb = ycrcb[:, :, 0], ycrcb[:, :, 1], ycrcb[:, :, 2]
    
    # YCrCb skin detection (optimal thresholds)
    # Y: 0-255 (no constraint on luminance)
    # Cr: 133-173
    # Cb: 77-127
    
    cr_condition = (cr >= 133) & (cr <= 173)
    cb_condition = (cb >= 77) & (cb <= 127)
    
    # Additional constraint: Cr > Cb (typical for skin)
    cr_cb_condition = cr > cb
    
    skin_mask = cr_condition & cb_condition & cr_cb_condition
    
    return skin_mask

def statistical_color_analysis(skin_pixels: np.ndarray) -> Dict:
    """Perform statistical analysis on skin pixels for better color characterization."""
    if len(skin_pixels) == 0:
        return {}
    
    analysis = {}
    
    # Basic statistics
    analysis['mean_rgb'] = np.mean(skin_pixels, axis=0)
    analysis['median_rgb'] = np.median(skin_pixels, axis=0)
    analysis['std_rgb'] = np.std(skin_pixels, axis=0)
    
    # Percentile analysis
    analysis['p25_rgb'] = np.percentile(skin_pixels, 25, axis=0)
    analysis['p75_rgb'] = np.percentile(skin_pixels, 75, axis=0)
    analysis['iqr_rgb'] = analysis['p75_rgb'] - analysis['p25_rgb']
    
    # Dominant color using K-means clustering
    try:
        from sklearn.cluster import KMeans
        
        # Reduce to 3 dominant colors
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        kmeans.fit(skin_pixels)
        
        # Get cluster centers (dominant colors)
        centers = kmeans.cluster_centers_
        labels = kmeans.labels_
        
        # Find most frequent cluster (most dominant color)
        unique, counts = np.unique(labels, return_counts=True)
        dominant_idx = unique[np.argmax(counts)]
        analysis['dominant_color'] = centers[dominant_idx]
        
        # Secondary colors
        sorted_indices = np.argsort(counts)[::-1]
        analysis['color_palette'] = [centers[unique[i]] for i in sorted_indices]
        analysis['color_weights'] = [counts[i] / len(labels) for i in sorted_indices]
        
    except ImportError:
        # Fallback without sklearn
        analysis['dominant_color'] = analysis['mean_rgb']
        analysis['color_palette'] = [analysis['mean_rgb']]
        analysis['color_weights'] = [1.0]
    
    # Color consistency score
    analysis['consistency_score'] = 1.0 / (1.0 + np.mean(analysis['std_rgb']))
    
    # Brightness analysis
    brightness = np.mean(skin_pixels, axis=1)
    analysis['brightness_mean'] = np.mean(brightness)
    analysis['brightness_std'] = np.std(brightness)
    analysis['brightness_uniformity'] = 1.0 / (1.0 + analysis['brightness_std'])
    
    return analysis

def advanced_monk_tone_matching(color_stats: Dict, raw_pixels: np.ndarray) -> tuple:
    """Advanced Monk tone matching using statistical analysis and multiple color spaces."""
    if 'dominant_color' not in color_stats:
        # Fallback
        return find_closest_monk_tone_enhanced(np.mean(raw_pixels, axis=0) if len(raw_pixels) > 0 else np.array([200, 180, 160]))
    
    dominant_color = color_stats['dominant_color']
    
    # Convert to multiple color spaces for comprehensive analysis
    lab_color = cv2.cvtColor(np.uint8([[dominant_color]]), cv2.COLOR_RGB2LAB)[0][0]
    hsv_color = cv2.cvtColor(np.uint8([[dominant_color]]), cv2.COLOR_RGB2HSV)[0][0]
    
    min_distance = float('inf')
    closest_monk = "Monk 2"
    detailed_scores = {}
    
    for monk_name, hex_color in MONK_SKIN_TONES.items():
        monk_rgb = np.array(hex_to_rgb(hex_color))
        monk_lab = cv2.cvtColor(np.uint8([[monk_rgb]]), cv2.COLOR_RGB2LAB)[0][0]
        monk_hsv = cv2.cvtColor(np.uint8([[monk_rgb]]), cv2.COLOR_RGB2HSV)[0][0]
        
        # Multi-space distance calculation
        rgb_distance = np.sqrt(np.sum((dominant_color - monk_rgb) ** 2))
        lab_distance = np.sqrt(np.sum((lab_color - monk_lab) ** 2))
        
        # Perceptual weighting (LAB is more perceptually uniform)
        combined_distance = rgb_distance * 0.3 + lab_distance * 0.7
        
        # Consistency bonus (reward consistent colors)
        consistency_bonus = color_stats.get('consistency_score', 0.5) * 10
        
        # Brightness similarity bonus
        brightness_diff = abs(color_stats.get('brightness_mean', 128) - np.mean(monk_rgb))
        brightness_bonus = max(0, 20 - brightness_diff/5)
        
        # Final score (lower is better)
        final_score = combined_distance - consistency_bonus - brightness_bonus
        
        detailed_scores[monk_name] = {
            'rgb_distance': rgb_distance,
            'lab_distance': lab_distance,
            'combined_distance': combined_distance,
            'final_score': final_score
        }
        
        if final_score < min_distance:
            min_distance = final_score
            closest_monk = monk_name
    
    return closest_monk, min_distance, detailed_scores

def extract_multi_region_colors(image_array: np.ndarray) -> List[np.ndarray]:
    """Extract skin colors using advanced face detection and multi-region analysis."""
    # Detect face regions
    face_regions = detect_face_regions(image_array)
    
    # Extract skin pixels using advanced methods
    skin_pixels = extract_skin_pixels_advanced(image_array, face_regions)
    
    if len(skin_pixels) == 0:
        # Fallback to geometric regions
        return extract_geometric_regions(image_array)
    
    # Perform statistical analysis
    color_stats = statistical_color_analysis(skin_pixels)
    
    # Return dominant colors from statistical analysis
    if 'color_palette' in color_stats:
        return color_stats['color_palette'][:3]  # Top 3 colors
    else:
        return [color_stats.get('mean_rgb', np.array([200, 180, 160]))]

def extract_geometric_regions(image_array: np.ndarray) -> List[np.ndarray]:
    """Fallback method using geometric regions when face detection fails."""
    h, w = image_array.shape[:2]
    
    # Define multiple face regions (optimized for all skin tones)
    regions = [
        # Forehead
        image_array[h//8:h//3, w//3:2*w//3],
        # Upper cheeks
        image_array[h//3:h//2, w//4:3*w//4],
        # Nose bridge
        image_array[h//3:2*h//3, 2*w//5:3*w//5],
        # Lower cheeks
        image_array[h//2:2*h//3, w//4:3*w//4],
        # Chin area
        image_array[2*h//3:5*h//6, 2*w//5:3*w//5]
    ]
    
    region_colors = []
    
    for region in regions:
        if region.size > 100:  # Ensure region has enough pixels
            # Use median for better outlier resistance
            region_color = np.median(region.reshape(-1, 3), axis=0)
            region_colors.append(region_color)
    
    return region_colors

def calculate_confidence_score(image_array: np.ndarray, final_color: np.ndarray, closest_distance: float) -> float:
    """Calculate confidence score based on multiple factors."""
    try:
        # Base confidence from color distance (closer = higher confidence)
        distance_confidence = max(0, 1 - (closest_distance / 200))  # Normalize to 0-1
        
        # Check image quality (sharpness)
        gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
        sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
        sharpness_confidence = min(1.0, sharpness / 500)  # Good sharpness > 500
        
        # Check brightness consistency (for light skin detection)
        brightness_std = np.std(final_color)
        consistency_confidence = max(0, 1 - (brightness_std / 50))  # Lower std = more consistent
        
        # Overall brightness check (light skin should be bright)
        avg_brightness = np.mean(final_color)
        if avg_brightness > 200:  # Very light skin
            brightness_bonus = 0.2
        elif avg_brightness > 180:  # Light skin
            brightness_bonus = 0.1
        else:
            brightness_bonus = 0
        
        # Weighted combination
        final_confidence = (
            distance_confidence * 0.4 +
            sharpness_confidence * 0.3 +
            consistency_confidence * 0.3 +
            brightness_bonus
        )
        
        return min(1.0, final_confidence)  # Cap at 1.0
        
    except Exception as e:
        logger.warning(f"Confidence calculation failed: {e}")
        return 0.5  # Default confidence

def find_closest_monk_tone_enhanced(rgb_color: np.ndarray) -> tuple:
    """Refined Monk tone matching for fair skin tones."""
    min_distance = float('inf')
    closest_monk = "Monk 2"
    
    # Refine brightness calculation
    avg_brightness = np.mean(rgb_color)

    # Adjust color space weights
    for monk_name, hex_color in MONK_SKIN_TONES.items():
        monk_rgb = np.array(hex_to_rgb(hex_color))

        # Euclidean distance
        euclidean_distance = np.sqrt(np.sum((rgb_color - monk_rgb) ** 2))

        # Adjust weighting for very light skin tones
        brightness_weight = 2.0 if avg_brightness > 220 else 1.0 if avg_brightness > 180 else 0.5
        combined_distance = euclidean_distance * 0.5 + brightness_weight * abs(avg_brightness - np.mean(monk_rgb))

        if combined_distance < min_distance:
            min_distance = combined_distance
            closest_monk = monk_name
    
    return closest_monk, min_distance

def analyze_skin_tone_ultra_advanced(image_array: np.ndarray) -> Dict:
    """Ultra-advanced skin tone analysis with comprehensive computer vision techniques."""
    try:
        logger.info("Starting ultra-advanced skin tone analysis...")
        
        # Step 1: Advanced preprocessing pipeline
        preprocessed_image = advanced_preprocessing(image_array)
        
        # Step 2: Face detection and skin pixel extraction
        face_regions = detect_face_regions(preprocessed_image)
        skin_pixels = extract_skin_pixels_advanced(preprocessed_image, face_regions)
        
        # Step 3: Statistical analysis of skin pixels
        if len(skin_pixels) > 0:
            color_stats = statistical_color_analysis(skin_pixels)
            
            # Step 4: Advanced Monk tone matching
            if color_stats:
                closest_monk, min_distance, detailed_scores = advanced_monk_tone_matching(color_stats, skin_pixels)
                dominant_color = color_stats['dominant_color']
            else:
                # Fallback
                closest_monk, min_distance = find_closest_monk_tone_enhanced(np.mean(skin_pixels, axis=0))
                dominant_color = np.mean(skin_pixels, axis=0)
                detailed_scores = {}
        else:
            # Fallback to geometric analysis
            logger.warning("No skin pixels detected, falling back to geometric analysis")
            region_colors = extract_geometric_regions(preprocessed_image)
            
            if region_colors:
                region_colors_array = np.array(region_colors)
                dominant_color = np.mean(region_colors_array, axis=0)
            else:
                # Ultimate fallback
                h, w = preprocessed_image.shape[:2]
                center_region = preprocessed_image[h//4:3*h//4, w//4:3*w//4]
                dominant_color = np.mean(center_region.reshape(-1, 3), axis=0)
            
            closest_monk, min_distance = find_closest_monk_tone_enhanced(dominant_color)
            color_stats = {}
            detailed_scores = {}
        
        # Step 5: Enhanced confidence calculation
        confidence = calculate_advanced_confidence(image_array, dominant_color, min_distance, color_stats, len(skin_pixels))
        
        # Step 6: Quality assessment
        quality_metrics = assess_image_quality(image_array)
        
        # Format response
        monk_number = closest_monk.split()[1]
        monk_id = f"Monk{monk_number.zfill(2)}"
        derived_hex = rgb_to_hex((int(dominant_color[0]), int(dominant_color[1]), int(dominant_color[2])))
        
        logger.info(f"Ultra-advanced analysis result: {monk_id}, confidence: {confidence:.2f}")
        
        return {
            'monk_skin_tone': monk_id,
            'monk_tone_display': closest_monk,
            'monk_hex': MONK_SKIN_TONES[closest_monk],
            'derived_hex_code': derived_hex,
            'dominant_rgb': dominant_color.astype(int).tolist(),
            'confidence': round(confidence, 2),
            'success': True,
            'analysis_method': 'ultra_advanced_multi_colorspace_ml',
            'skin_pixels_analyzed': len(skin_pixels),
            'face_regions_detected': len(face_regions),
            'color_statistics': {
                'mean_rgb': color_stats.get('mean_rgb', dominant_color).astype(int).tolist() if hasattr(color_stats.get('mean_rgb', dominant_color), 'astype') else list(color_stats.get('mean_rgb', dominant_color)),
                'consistency_score': round(color_stats.get('consistency_score', 0.5), 3),
                'brightness_uniformity': round(color_stats.get('brightness_uniformity', 0.5), 3)
            },
            'quality_metrics': quality_metrics,
            'detailed_scores': {k: round(v.get('final_score', 0), 2) for k, v in detailed_scores.items()} if detailed_scores else {}
        }
        
    except Exception as e:
        logger.error(f"Error in ultra-advanced skin tone analysis: {e}")
        return {
            'monk_skin_tone': 'Monk02',
            'monk_tone_display': 'Monk 2',
            'monk_hex': MONK_SKIN_TONES['Monk 2'],
            'derived_hex_code': '#f3e7db',
            'dominant_rgb': [243, 231, 219],
            'confidence': 0.3,
            'success': False,
            'error': str(e),
            'analysis_method': 'ultra_advanced_fallback'
        }

def calculate_advanced_confidence(image_array: np.ndarray, dominant_color: np.ndarray, 
                                closest_distance: float, color_stats: Dict, skin_pixel_count: int) -> float:
    """Calculate advanced confidence score using multiple factors."""
    try:
        confidence_factors = []
        
        # 1. Color distance confidence (closer = better)
        distance_confidence = max(0, 1 - (closest_distance / 150))
        confidence_factors.append(('distance', distance_confidence, 0.25))
        
        # 2. Image quality (sharpness)
        gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
        sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
        sharpness_confidence = min(1.0, sharpness / 300)
        confidence_factors.append(('sharpness', sharpness_confidence, 0.15))
        
        # 3. Color consistency
        consistency_score = color_stats.get('consistency_score', 0.5)
        confidence_factors.append(('consistency', consistency_score, 0.2))
        
        # 4. Skin pixel coverage
        pixel_coverage = min(1.0, skin_pixel_count / 5000)  # Normalize to max 5000 pixels
        confidence_factors.append(('coverage', pixel_coverage, 0.15))
        
        # 5. Brightness uniformity
        brightness_uniformity = color_stats.get('brightness_uniformity', 0.5)
        confidence_factors.append(('uniformity', brightness_uniformity, 0.1))
        
        # 6. Color space stability (check if color is reasonable)
        avg_brightness = np.mean(dominant_color)
        if 50 <= avg_brightness <= 250:  # Reasonable range
            stability_score = 1.0
        else:
            stability_score = 0.5
        confidence_factors.append(('stability', stability_score, 0.15))
        
        # Calculate weighted confidence
        total_confidence = sum(score * weight for _, score, weight in confidence_factors)
        
        # Apply bonus for very consistent results
        if consistency_score > 0.8 and brightness_uniformity > 0.7:
            total_confidence += 0.1
        
        return min(1.0, total_confidence)
        
    except Exception as e:
        logger.warning(f"Advanced confidence calculation failed: {e}")
        return 0.5

def assess_image_quality(image_array: np.ndarray) -> Dict:
    """Assess various image quality metrics."""
    try:
        metrics = {}
        
        # Convert to grayscale for analysis
        gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
        
        # 1. Sharpness (Laplacian variance)
        sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
        metrics['sharpness'] = round(sharpness, 2)
        metrics['sharpness_quality'] = 'excellent' if sharpness > 1000 else 'good' if sharpness > 500 else 'fair' if sharpness > 100 else 'poor'
        
        # 2. Brightness statistics
        brightness_mean = np.mean(gray)
        brightness_std = np.std(gray)
        metrics['brightness_mean'] = round(brightness_mean, 2)
        metrics['brightness_std'] = round(brightness_std, 2)
        metrics['brightness_quality'] = 'good' if 50 <= brightness_mean <= 200 else 'fair'
        
        # 3. Contrast (RMS contrast)
        contrast = np.sqrt(np.mean((gray - brightness_mean) ** 2))
        metrics['contrast'] = round(contrast, 2)
        metrics['contrast_quality'] = 'excellent' if contrast > 40 else 'good' if contrast > 25 else 'fair' if contrast > 15 else 'poor'
        
        # 4. Noise level (using high-pass filter)
        kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
        noise_image = cv2.filter2D(gray, -1, kernel)
        noise_level = np.std(noise_image)
        metrics['noise_level'] = round(noise_level, 2)
        metrics['noise_quality'] = 'excellent' if noise_level < 10 else 'good' if noise_level < 20 else 'fair' if noise_level < 30 else 'poor'
        
        # 5. Overall quality score
        quality_scores = {
            'excellent': 4, 'good': 3, 'fair': 2, 'poor': 1
        }
        
        total_score = sum(quality_scores.get(metrics[key], 2) for key in ['sharpness_quality', 'brightness_quality', 'contrast_quality', 'noise_quality'])
        avg_score = total_score / 4
        
        if avg_score >= 3.5:
            metrics['overall_quality'] = 'excellent'
        elif avg_score >= 2.5:
            metrics['overall_quality'] = 'good'
        elif avg_score >= 1.5:
            metrics['overall_quality'] = 'fair'
        else:
            metrics['overall_quality'] = 'poor'
            
        return metrics
        
    except Exception as e:
        logger.warning(f"Image quality assessment failed: {e}")
        return {'overall_quality': 'unknown', 'error': str(e)}

def analyze_skin_tone_enhanced(image_array: np.ndarray) -> Dict:
    """Direct face color extraction with accurate Monk tone matching."""
    try:
        logger.info("Starting direct face color analysis...")
        
        h, w = image_array.shape[:2]
        
        # Step 1: Extract face color directly from safe regions
        face_color = extract_face_color_direct(image_array)
        
        # Step 2: Match to Monk tones using brightness-first approach
        closest_monk, min_distance = match_monk_tone_brightness_first(face_color)
        
        # Format response
        monk_number = closest_monk.split()[1]
        monk_id = f"Monk{monk_number.zfill(2)}"
        derived_hex = rgb_to_hex((int(face_color[0]), int(face_color[1]), int(face_color[2])))
        
        # Calculate confidence based on distance
        confidence = max(0.5, 1.0 - min_distance / 200)
        
        logger.info(f"Direct analysis result: {monk_id}, confidence: {confidence:.2f}, color: {derived_hex}")
        
        return {
            'monk_skin_tone': monk_id,
            'monk_tone_display': closest_monk,
            'monk_hex': MONK_SKIN_TONES[closest_monk],
            'derived_hex_code': derived_hex,
            'dominant_rgb': face_color.astype(int).tolist(),
            'confidence': round(confidence, 2),
            'success': True,
            'analysis_method': 'direct_face_color_brightness_first'
        }
        
    except Exception as e:
        logger.error(f"Error in direct face color analysis: {e}")
        return {
            'monk_skin_tone': 'Monk01',
            'monk_tone_display': 'Monk 1',
            'monk_hex': MONK_SKIN_TONES['Monk 1'],
            'derived_hex_code': '#f6ede4',
            'dominant_rgb': [246, 237, 228],
            'confidence': 0.3,
            'success': False,
            'error': str(e)
        }

def extract_face_color_direct(image_array: np.ndarray) -> np.ndarray:
    """Directly extract face color from the most reliable regions."""
    h, w = image_array.shape[:2]
    
    # Define the safest face regions (avoiding eyes, mouth, hair)
    regions = [
        # Center forehead
        image_array[h//6:h//3, 2*w//5:3*w//5],
        # Upper cheeks  
        image_array[2*h//5:h//2, w//4:2*w//5],    # Left cheek
        image_array[2*h//5:h//2, 3*w//5:3*w//4],  # Right cheek
        # Nose bridge (small area)
        image_array[h//3:2*h//5, 9*w//20:11*w//20]
    ]
    
    all_colors = []
    
    for region in regions:
        if region.size > 50:  # Ensure region has enough pixels
            # Get median color of this region (robust against outliers)
            region_pixels = region.reshape(-1, 3)
            
            # Remove extreme outliers (likely shadows/highlights)
            brightness = np.mean(region_pixels, axis=1)
            q25, q75 = np.percentile(brightness, [25, 75])
            
            # Keep pixels within reasonable brightness range
            valid_mask = (brightness >= q25) & (brightness <= q75)
            
            if np.sum(valid_mask) > 20:
                valid_pixels = region_pixels[valid_mask]
                region_color = np.median(valid_pixels, axis=0)
                all_colors.append(region_color)
    
    if len(all_colors) > 0:
        # Return median of all region colors
        return np.median(all_colors, axis=0)
    else:
        # Ultimate fallback - center of image
        center = image_array[h//3:2*h//3, w//3:2*w//3]
        return np.median(center.reshape(-1, 3), axis=0)

def match_monk_tone_brightness_first(face_color: np.ndarray) -> tuple:
    """Match Monk tone prioritizing brightness similarity for extreme tones."""
    
    face_brightness = np.mean(face_color)
    min_distance = float('inf')
    closest_monk = "Monk 1"
    
    logger.info(f"Face brightness: {face_brightness}, Face RGB: {face_color}")
    
    # Create brightness-ordered list for better extreme tone detection
    monk_brightness = {}
    for monk_name, hex_color in MONK_SKIN_TONES.items():
        monk_rgb = np.array(hex_to_rgb(hex_color))
        monk_brightness[monk_name] = np.mean(monk_rgb)
    
    # Sort Monk tones by brightness
    sorted_monks = sorted(monk_brightness.items(), key=lambda x: x[1])
    
    # For very bright face colors, strongly favor lighter Monk tones
    if face_brightness > 200:
        logger.info("Very bright face detected - prioritizing light Monk tones")
        # Check Monk 1-3 first with heavy brightness weighting
        priority_monks = ['Monk 1', 'Monk 2', 'Monk 3']
        for monk_name in priority_monks:
            hex_color = MONK_SKIN_TONES[monk_name]
            monk_rgb = np.array(hex_to_rgb(hex_color))
            
            # Heavily weight brightness similarity for fair skin
            color_distance = np.sqrt(np.sum((face_color - monk_rgb) ** 2))
            brightness_distance = abs(face_brightness - np.mean(monk_rgb))
            
            # For very fair skin, brightness is most important
            combined_distance = color_distance * 0.2 + brightness_distance * 3.0
            
            if combined_distance < min_distance:
                min_distance = combined_distance
                closest_monk = monk_name
    
    # For very dark face colors, strongly favor darker Monk tones        
    elif face_brightness < 80:
        logger.info("Very dark face detected - prioritizing deep Monk tones")
        # Check Monk 8-10 first with heavy brightness weighting
        priority_monks = ['Monk 10', 'Monk 9', 'Monk 8']
        for monk_name in priority_monks:
            hex_color = MONK_SKIN_TONES[monk_name]
            monk_rgb = np.array(hex_to_rgb(hex_color))
            
            # Heavily weight brightness similarity for deep skin
            color_distance = np.sqrt(np.sum((face_color - monk_rgb) ** 2))
            brightness_distance = abs(face_brightness - np.mean(monk_rgb))
            
            # For very deep skin, brightness is most important
            combined_distance = color_distance * 0.2 + brightness_distance * 3.0
            
            if combined_distance < min_distance:
                min_distance = combined_distance
                closest_monk = monk_name
    
    # If no extreme match found, or for medium tones, check all tones
    if min_distance == float('inf') or 80 <= face_brightness <= 200:
        logger.info("Checking all Monk tones with standard weighting")
        for monk_name, hex_color in MONK_SKIN_TONES.items():
            monk_rgb = np.array(hex_to_rgb(hex_color))
            
            # Standard distance calculation
            color_distance = np.sqrt(np.sum((face_color - monk_rgb) ** 2))
            brightness_distance = abs(face_brightness - np.mean(monk_rgb))
            
            # Balanced weighting for medium tones
            combined_distance = color_distance * 0.6 + brightness_distance * 0.8
            
            if combined_distance < min_distance:
                min_distance = combined_distance
                closest_monk = monk_name
    
    logger.info(f"Selected: {closest_monk}, Distance: {min_distance}")
    return closest_monk, min_distance

def extract_pure_face_skin(image_array: np.ndarray) -> np.ndarray:
    """Extract only pure face skin pixels using ultra-conservative approach."""
    h, w = image_array.shape[:2]
    
    # Define very small, safe face regions to avoid eyes, hair, clothing
    safe_regions = [
        # Forehead center (very small)
        image_array[h//5:h//3, 2*w//5:3*w//5],
        # Upper cheek (small patches)
        image_array[2*h//5:h//2, w//4:2*w//5],   # Left upper cheek
        image_array[2*h//5:h//2, 3*w//5:3*w//4], # Right upper cheek
        # Nose area (tiny region)
        image_array[h//3:2*h//5, 9*w//20:11*w//20],
    ]
    
    all_skin_pixels = []
    
    for region in safe_regions:
        if region.size == 0:
            continue
            
        # Extract skin using very strict criteria
        skin_pixels = extract_skin_strict(region)
        if len(skin_pixels) > 5:
            all_skin_pixels.extend(skin_pixels)
    
    return np.array(all_skin_pixels) if all_skin_pixels else np.array([])

def extract_skin_strict(region: np.ndarray) -> np.ndarray:
    """Extract skin pixels using very strict, reliable criteria."""
    if region.size == 0:
        return np.array([])
        
    r, g, b = region[:, :, 0], region[:, :, 1], region[:, :, 2]
    
    # Calculate overall brightness to adapt rules
    total_brightness = np.mean([r, g, b])
    
    if total_brightness > 180:  # Very bright region - likely fair skin
        # Ultra-permissive for fair skin
        skin_mask = (
            (r >= g * 0.9) &  # R >= 90% of G (very relaxed)
            (g >= b * 0.85) & # G >= 85% of B (very relaxed) 
            (r > 100) & (g > 90) & (b > 80) &  # Minimum brightness for fair skin
            (r + g + b > 350) &  # Total brightness check
            (r + g + b < 720) &  # Not overexposed
            (r < 255) & (g < 255) & (b < 255)  # Not pure white
        )
        
    elif total_brightness < 80:  # Very dark region - likely deep skin
        # Specialized for deep skin
        skin_mask = (
            (r >= g * 0.7) &  # R >= 70% of G (relaxed for deep skin)
            (r >= b * 0.6) &  # R >= 60% of B (relaxed for deep skin)
            (r > 15) & (g > 12) & (b > 8) &   # Minimum values for deep skin
            (r + g + b > 45) &   # Minimum total brightness
            (r + g + b < 240) &  # Maximum for deep skin
            (r < 120) & (g < 100) & (b < 80)  # Upper limits for deep skin
        )
        
    else:  # Medium range
        # Standard skin detection
        skin_mask = (
            (r >= g) & (r >= b) &  # Basic skin ratios
            (r > 50) & (g > 35) & (b > 25) &  # Minimum thresholds
            (r + g + b > 120) & (r + g + b < 500) &  # Brightness range
            (r < 200) & (g < 180) & (b < 160)  # Upper limits
        )
    
    if np.sum(skin_mask) > 3:
        return region[skin_mask]
    else:
        return np.array([])

def get_representative_skin_color(skin_pixels: np.ndarray) -> np.ndarray:
    """Get the most representative skin color from extracted pixels."""
    if len(skin_pixels) == 0:
        return np.array([200, 180, 160])  # Default fallback
    
    # Remove outliers using IQR method
    brightness = np.mean(skin_pixels, axis=1)
    q25, q75 = np.percentile(brightness, [25, 75])
    iqr = q75 - q25
    
    # Keep pixels within 1.5 * IQR of the median
    median_brightness = np.median(brightness)
    valid_range_mask = (
        (brightness >= median_brightness - 1.5 * iqr) & 
        (brightness <= median_brightness + 1.5 * iqr)
    )
    
    if np.sum(valid_range_mask) > 5:
        filtered_pixels = skin_pixels[valid_range_mask]
        return np.median(filtered_pixels, axis=0)
    else:
        return np.median(skin_pixels, axis=0)

def find_monk_tone_brightness_aware(rgb_color: np.ndarray) -> tuple:
    """Find closest Monk tone with brightness-aware matching for extreme tones."""
    min_distance = float('inf')
    closest_monk = "Monk 1"
    
    avg_brightness = np.mean(rgb_color)
    
    for monk_name, hex_color in MONK_SKIN_TONES.items():
        monk_rgb = np.array(hex_to_rgb(hex_color))
        
        # Standard Euclidean distance
        color_distance = np.sqrt(np.sum((rgb_color - monk_rgb) ** 2))
        
        # Brightness difference
        brightness_diff = abs(avg_brightness - np.mean(monk_rgb))
        
        # For extreme tones, heavily weight brightness similarity
        if avg_brightness > 200:  # Very bright - likely Monk 1-2
            # For very fair skin, prioritize brightness matching
            combined_distance = color_distance * 0.3 + brightness_diff * 2.0
        elif avg_brightness < 80:  # Very dark - likely Monk 9-10
            # For very deep skin, prioritize brightness matching
            combined_distance = color_distance * 0.3 + brightness_diff * 2.0
        else:  # Medium range
            # Standard matching
            combined_distance = color_distance * 0.7 + brightness_diff * 0.5
        
        if combined_distance < min_distance:
            min_distance = combined_distance
            closest_monk = monk_name
    
    return closest_monk, min_distance

def extract_skin_pixels_precision(image_array: np.ndarray) -> tuple:
    """Precision skin pixel extraction optimized for extreme tones."""
    h, w = image_array.shape[:2]
    
    # Define multiple precision regions for different analysis
    regions = {
        'forehead': image_array[h//8:h//3, 2*w//5:3*w//5],
        'left_cheek': image_array[2*h//5:3*h//5, w//6:2*w//5],
        'right_cheek': image_array[2*h//5:3*h//5, 3*w//5:5*w//6],
        'nose_bridge': image_array[h//3:h//2, 2*w//5:3*w//5],
        'chin': image_array[3*h//5:4*h//5, 2*w//5:3*w//5]
    }
    
    all_skin_pixels = []
    region_stats = {}
    
    for region_name, region in regions.items():
        if region.size == 0:
            continue
            
        # Extract skin pixels using adaptive thresholds
        skin_pixels = extract_from_region_adaptive(region)
        
        if len(skin_pixels) > 10:
            all_skin_pixels.extend(skin_pixels)
            
            # Calculate region statistics
            region_stats[region_name] = {
                'mean_rgb': np.mean(skin_pixels, axis=0),
                'median_rgb': np.median(skin_pixels, axis=0),
                'brightness': np.mean(skin_pixels),
                'pixel_count': len(skin_pixels)
            }
    
    return np.array(all_skin_pixels), region_stats

def extract_from_region_adaptive(region: np.ndarray) -> np.ndarray:
    """Extract skin pixels from region using adaptive rules based on brightness."""
    if region.size == 0:
        return np.array([])
        
    r, g, b = region[:, :, 0], region[:, :, 1], region[:, :, 2]
    
    # Calculate region brightness to determine which rules to apply
    avg_brightness = np.mean([r, g, b])
    
    if avg_brightness > 200:  # Very bright - likely fair skin
        # Extremely permissive rules for very fair skin
        skin_mask = (
            (r + g + b > 400) &  # Very bright pixels
            (r + g + b < 750) &  # Not overexposed
            (r >= g * 0.95) &    # R slightly >= G (very relaxed)
            (g >= b * 0.9) &     # G >= B (very relaxed)
            (r < 255) & (g < 255) & (b < 255) &  # Not pure white
            (np.abs(r.astype(np.int16) - g.astype(np.int16)) < 50) &
            (np.abs(r.astype(np.int16) - b.astype(np.int16)) < 70)
        )
        
    elif avg_brightness < 100:  # Very dark - likely deep skin
        # Specialized rules for very deep skin
        skin_mask = (
            (r + g + b > 60) &   # Minimum brightness for skin
            (r + g + b < 300) &  # Maximum for deep skin
            (r >= g * 0.8) &     # R >= G (relaxed for deep skin)
            (r >= b * 0.7) &     # R >= B (relaxed for deep skin)
            (r > 20) & (g > 15) & (b > 10) &  # Minimum thresholds
            (np.abs(r.astype(np.int16) - g.astype(np.int16)) < 40) &
            (np.abs(r.astype(np.int16) - b.astype(np.int16)) < 50)
        )
        
    else:  # Medium range
        # Standard skin detection rules
        skin_mask = (
            (r >= g) & (r >= b) &
            (r > 60) & (g > 40) & (b > 30) &
            (r < 255) & (g < 255) & (b < 255) &
            ((r + g + b) > 150) & ((r + g + b) < 600) &
            (np.abs(r.astype(np.int16) - g.astype(np.int16)) < 60) &
            (np.abs(r.astype(np.int16) - b.astype(np.int16)) < 80)
        )
    
    if np.sum(skin_mask) > 5:
        return region[skin_mask]
    else:
        return np.array([])

def find_closest_monk_tone_simple(rgb_color: np.ndarray) -> tuple:
    """Simple Monk tone matching using direct Euclidean distance."""
    min_distance = float('inf')
    closest_monk = "Monk 1"  # Default to lightest tone for fair skin
    
    for monk_name, hex_color in MONK_SKIN_TONES.items():
        monk_rgb = np.array(hex_to_rgb(hex_color))
        
        # Simple Euclidean distance
        distance = np.sqrt(np.sum((rgb_color - monk_rgb) ** 2))
        
        if distance < min_distance:
            min_distance = distance
            closest_monk = monk_name
    
    return closest_monk, min_distance

# Keep the simple version as fallback
def analyze_skin_tone_precision(image_array: np.ndarray) -> Dict:
    """Precision skin tone analysis targeting extreme tones (Monk 1 and Monk 10)."""
    try:
        logger.info("Starting precision skin tone analysis for extreme tones...")
        
        # Step 1: Extract skin pixels using precision method
        skin_pixels, region_stats = extract_skin_pixels_precision(image_array)
        
        if len(skin_pixels) < 10:
            logger.warning("Insufficient skin pixels detected, using fallback")
            # Fallback to simple region extraction
            h, w = image_array.shape[:2]
            center_region = image_array[h//3:2*h//3, w//3:2*w//3]
            representative_color = np.median(center_region.reshape(-1, 3), axis=0)
        else:
            # Step 2: Get representative color from extracted pixels
            representative_color = get_representative_skin_color(skin_pixels)
        
        # Step 3: Match to Monk tone using brightness-aware approach
        closest_monk, min_distance = find_monk_tone_brightness_aware(representative_color)
        
        # Step 4: Calculate confidence based on analysis quality
        confidence = calculate_precision_confidence(
            representative_color, min_distance, len(skin_pixels), region_stats
        )
        
        # Format response
        monk_number = closest_monk.split()[1]
        monk_id = f"Monk{monk_number.zfill(2)}"
        derived_hex = rgb_to_hex((int(representative_color[0]), int(representative_color[1]), int(representative_color[2])))
        
        logger.info(f"Precision analysis result: {monk_id}, confidence: {confidence:.2f}, pixels analyzed: {len(skin_pixels)}")
        
        return {
            'monk_skin_tone': monk_id,
            'monk_tone_display': closest_monk,
            'monk_hex': MONK_SKIN_TONES[closest_monk],
            'derived_hex_code': derived_hex,
            'dominant_rgb': representative_color.astype(int).tolist(),
            'confidence': round(confidence, 2),
            'success': True,
            'analysis_method': 'precision_extreme_tone_targeting',
            'skin_pixels_analyzed': len(skin_pixels),
            'regions_analyzed': len(region_stats),
            'region_statistics': {k: {
                'brightness': round(v['brightness'], 1),
                'pixel_count': v['pixel_count']
            } for k, v in region_stats.items()}
        }
        
    except Exception as e:
        logger.error(f"Error in precision skin tone analysis: {e}")
        return {
            'monk_skin_tone': 'Monk01',
            'monk_tone_display': 'Monk 1',
            'monk_hex': MONK_SKIN_TONES['Monk 1'],
            'derived_hex_code': '#f6ede4',
            'dominant_rgb': [246, 237, 228],
            'confidence': 0.3,
            'success': False,
            'error': str(e),
            'analysis_method': 'precision_fallback'
        }

def calculate_precision_confidence(representative_color: np.ndarray, min_distance: float, 
                                 pixel_count: int, region_stats: Dict) -> float:
    """Calculate confidence for precision analysis."""
    try:
        # Base confidence from distance (closer = better)
        distance_confidence = max(0, 1 - (min_distance / 100))
        
        # Pixel count confidence (more pixels = better)
        pixel_confidence = min(1.0, pixel_count / 1000)  # Ideal: 1000+ pixels
        
        # Region consistency (if multiple regions have similar colors)
        if len(region_stats) > 1:
            brightnesses = [stats['brightness'] for stats in region_stats.values()]
            brightness_std = np.std(brightnesses)
            consistency_confidence = max(0, 1 - (brightness_std / 50))
        else:
            consistency_confidence = 0.5
        
        # Brightness appropriateness for detected skin
        avg_brightness = np.mean(representative_color)
        if 30 <= avg_brightness <= 240:  # Reasonable skin brightness range
            brightness_confidence = 1.0
        else:
            brightness_confidence = 0.7
        
        # Weighted combination
        final_confidence = (
            distance_confidence * 0.4 +
            pixel_confidence * 0.25 +
            consistency_confidence * 0.2 +
            brightness_confidence * 0.15
        )
        
        return min(1.0, final_confidence)
        
    except Exception as e:
        logger.warning(f"Precision confidence calculation failed: {e}")
        return 0.5

def analyze_skin_tone_simple(image_array: np.ndarray) -> Dict:
    """Simplified skin tone analysis (fallback method)."""
    try:
        # Get average color of the image center
        h, w = image_array.shape[:2]
        center_region = image_array[h//4:3*h//4, w//4:3*w//4]
        
        # Calculate average RGB
        avg_color = np.mean(center_region.reshape(-1, 3), axis=0)
        
        # Find closest Monk skin tone
        min_distance = float('inf')
        closest_monk = "Monk 2"  # Default to lighter tone
        
        for monk_name, hex_color in MONK_SKIN_TONES.items():
            monk_rgb = np.array(hex_to_rgb(hex_color))
            distance = np.sqrt(np.sum((avg_color - monk_rgb) ** 2))
            
            if distance < min_distance:
                min_distance = distance
                closest_monk = monk_name
        
        # Format response
        monk_number = closest_monk.split()[1]
        monk_id = f"Monk{monk_number.zfill(2)}"
        derived_hex = rgb_to_hex((int(avg_color[0]), int(avg_color[1]), int(avg_color[2])))
        
        return {
            'monk_skin_tone': monk_id,
            'monk_tone_display': closest_monk,
            'monk_hex': MONK_SKIN_TONES[closest_monk],
            'derived_hex_code': derived_hex,
            'dominant_rgb': avg_color.astype(int).tolist(),
            'confidence': 0.6,
            'success': True,
            'analysis_method': 'simple_rgb'
        }
        
    except Exception as e:
        logger.error(f"Error in simple skin tone analysis: {e}")
        return {
            'monk_skin_tone': 'Monk02',
            'monk_tone_display': 'Monk 2',
            'monk_hex': MONK_SKIN_TONES['Monk 2'],
            'derived_hex_code': '#f3e7db',
            'dominant_rgb': [243, 231, 219],
            'confidence': 0.3,
            'success': False,
            'error': str(e)
        }

@app.post("/analyze-skin-tone")
async def analyze_skin_tone(file: UploadFile = File(...)):
    """Analyze skin tone from uploaded image."""
    try:
        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read and process image
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        image_array = np.array(image)
        
        # Try precision analysis first, then enhanced, then simple
        try:
            result = analyze_skin_tone_precision(image_array)
            if result['success']:
                return result
        except Exception as e:
            logger.warning(f"Precision analysis failed: {e}, falling back to enhanced analysis")
        
        try:
            result = analyze_skin_tone_enhanced(image_array)
            if result['success']:
                return result
        except Exception as e:
            logger.warning(f"Enhanced analysis failed: {e}, falling back to simple analysis")
        
        # Fallback to simple analysis
        result = analyze_skin_tone_simple(image_array)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in analyze_skin_tone endpoint: {e}")
        return {
            'monk_skin_tone': 'Monk05',
            'monk_tone_display': 'Monk 5',
            'monk_hex': '#d7bd96',
            'derived_hex_code': '#d7bd96',
            'dominant_rgb': [215, 189, 150],
            'confidence': 0.5,
            'success': False,
            'error': str(e)
        }

# Additional endpoints for compatibility
@app.get("/products")
def get_products(product_type: str = Query(None), random: bool = Query(False)):
    """Get H&M style products."""
    return []

@app.get("/makeup-types")
def get_makeup_types():
    """Get available makeup types."""
    return {
        "types": ["Foundation", "Concealer", "Lipstick", "Mascara", "Blush", "Highlighter", "Eyeshadow"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
