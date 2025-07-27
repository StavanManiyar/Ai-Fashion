#!/usr/bin/env python3
"""
Debug script to test the precision skin tone analysis algorithm
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from main_simple import (
    find_monk_tone_brightness_aware,
    calculate_precision_confidence,
    MONK_SKIN_TONES
)
import numpy as np
from webcolors import hex_to_rgb, rgb_to_hex
import cv2

def test_precision_monk_matching():
    """Test the precision brightness-aware Monk tone matching"""
    
    print("=== Precision Monk Skin Tone Analysis Debug ===\n")
    
    # Test cases designed to challenge the algorithm with extreme tones
    test_cases = [
        ("Very Fair (Expected Monk 1)", [252, 245, 238]),  # Very light skin
        ("Fair (Expected Monk 2)", [245, 232, 220]),       # Light skin
        ("Light (Expected Monk 3)", [230, 210, 195]),      # Light-medium
        ("Medium Light (Expected Monk 4)", [210, 180, 160]), # Medium light
        ("Medium (Expected Monk 5)", [180, 150, 125]),     # Medium
        ("Medium Tan (Expected Monk 6)", [150, 120, 95]),  # Medium-dark
        ("Tan (Expected Monk 7)", [130, 92, 67]),          # Reference Monk 7
        ("Dark (Expected Monk 8)", [96, 65, 52]),          # Dark
        ("Deep (Expected Monk 9)", [65, 48, 40]),          # Very dark
        ("Very Deep (Expected Monk 10)", [41, 36, 32]),    # Deepest tone
    ]
    
    print("Testing precision brightness-aware matching:\n")
    
    for description, rgb_values in test_cases:
        print(f"Testing {description}: RGB{tuple(rgb_values)}")
        
        # Convert to numpy array
        rgb_array = np.array(rgb_values, dtype=np.float64)
        
        # Test brightness-aware matching
        result = find_monk_tone_brightness_aware(rgb_array)
        
        print(f"  Result: {result['monk_name']} (ID: {result['monk_id']})")
        print(f"  Brightness: {result['brightness']:.2f}")
        print(f"  Distance: {result['color_distance']:.2f}")
        print(f"  Hex: {result['monk_hex']} -> Derived: {result['derived_hex']}")
        print()
    
    # Test with exact Monk tone RGB values
    print("\nTesting with exact Monk tone RGB values:\n")
    
    for monk_name, monk_hex in MONK_SKIN_TONES.items():
        monk_rgb = np.array(hex_to_rgb(monk_hex), dtype=np.float64)
        result = find_monk_tone_brightness_aware(monk_rgb)
        
        expected_match = monk_name == result['monk_name']
        status = "✓" if expected_match else "✗"
        
        print(f"{status} {monk_name}: RGB{tuple(monk_rgb.astype(int))} -> {result['monk_name']}")
        if not expected_match:
            print(f"    Expected: {monk_name}, Got: {result['monk_name']}")
            print(f"    Distance: {result['color_distance']:.2f}, Brightness: {result['brightness']:.2f}")
    
    print("\n=== Precision Analysis Complete ===")

def test_confidence_calculation():
    """Test the precision confidence score calculation"""
    
    print("\n=== Testing Confidence Score Calculation ===\n")
    
    # Mock skin pixels for testing
    test_cases = [
        ("High Quality - Consistent Fair Skin", np.array([[250, 240, 230], [248, 238, 228], [252, 242, 232]])),
        ("Medium Quality - Some Variation", np.array([[180, 150, 120], [185, 155, 125], [175, 145, 115]])),
        ("Low Quality - High Variation", np.array([[100, 80, 60], [150, 120, 90], [80, 60, 40]])),
    ]
    
    for description, skin_pixels in test_cases:
        print(f"Testing {description}:")
        
        # Calculate average color
        avg_color = np.mean(skin_pixels, axis=0)
        
        # Find closest Monk tone
        monk_result = find_monk_tone_brightness_aware(avg_color)
        
        # Calculate confidence
        confidence = calculate_precision_confidence(
            skin_pixels=skin_pixels,
            monk_result=monk_result,
            image_quality=0.8,  # Mock quality
            pixel_coverage=0.15  # Mock coverage
        )
        
        print(f"  Average RGB: {tuple(avg_color.astype(int))}")
        print(f"  Monk Result: {monk_result['monk_name']}")
        print(f"  Confidence: {confidence:.3f}")
        print(f"  Color Stability: {1.0 - (np.std(skin_pixels) / 255):.3f}")
        print()
    
    print("=== Confidence Testing Complete ===")

if __name__ == "__main__":
    test_precision_monk_matching()
    test_confidence_calculation()
