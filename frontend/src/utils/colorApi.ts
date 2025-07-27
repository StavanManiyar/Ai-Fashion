import { API_BASE_URL } from '../config/api';

export interface ColorPaletteResponse {
  skin_tone_id: string;
  recommended_colors: Array<{
    hex_code: string;
    color_name: string;
    suitable_skin_tone: string;
    seasonal_palette: string;
    category: string;
  }>;
  colors_to_avoid: Array<{
    hex_code: string;
    color_name: string;
    suitable_skin_tone: string;
    seasonal_palette: string;
    category: string;
  }>;
  detected_skin_tone?: {
    id: string;
    name: string;
    hex_code: string;
    display_name: string;
  };
  total_recommended: number;
  total_avoid: number;
}

export interface ColorRecommendation {
  hex_code: string;
  color_name: string;
  suitable_skin_tone: string;
  seasonal_palette: string;
  category: string;
}

/**
 * Fetch complete color palette for a detected skin tone
 */
export const fetchColorPalette = async (
  skinToneId: string, 
  includeSkinTone: boolean = true
): Promise<ColorPaletteResponse> => {
  const url = `${API_BASE_URL}/api/colors/palette/${skinToneId}?include_skin_tone=${includeSkinTone}`;
  
  const response = await fetch(url);
  
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to fetch color palette: ${response.status} ${errorText}`);
  }
  
  return response.json();
};

/**
 * Fetch color recommendations for a specific skin tone
 */
export const fetchColorRecommendations = async (
  skinTone: string,
  limit: number = 10
): Promise<ColorRecommendation[]> => {
  const url = `${API_BASE_URL}/api/colors/recommendations/${skinTone}?limit=${limit}`;
  
  const response = await fetch(url);
  
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to fetch color recommendations: ${response.status} ${errorText}`);
  }
  
  return response.json();
};

/**
 * Fetch colors by skin tone with optional category filter
 */
export const fetchColorsBySkinTone = async (
  skinTone: string,
  limit: number = 50,
  category?: 'recommended' | 'avoid'
): Promise<ColorRecommendation[]> => {
  let url = `${API_BASE_URL}/api/colors/skin-tone/${skinTone}?limit=${limit}`;
  
  if (category) {
    url += `&category=${category}`;
  }
  
  const response = await fetch(url);
  
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to fetch colors by skin tone: ${response.status} ${errorText}`);
  }
  
  return response.json();
};

/**
 * Fetch color information by hex code
 */
export const fetchColorByHex = async (hexCode: string): Promise<ColorRecommendation> => {
  // Remove # from hex code if present
  const cleanHex = hexCode.replace('#', '');
  const url = `${API_BASE_URL}/api/colors/hex/${cleanHex}`;
  
  const response = await fetch(url);
  
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to fetch color by hex: ${response.status} ${errorText}`);
  }
  
  return response.json();
};

/**
 * Convert detected skin tone result to ColorAnalysis props format
 */
export const formatDetectedSkinTone = (skinToneResult: any) => {
  if (!skinToneResult || !skinToneResult.monk_skin_tone) {
    return undefined;
  }

  return {
    id: skinToneResult.monk_skin_tone,
    name: skinToneResult.monk_tone_display || skinToneResult.monk_skin_tone,
    hex_code: skinToneResult.monk_hex || skinToneResult.derived_hex_code,
    display_name: `Your Detected Skin Tone (${skinToneResult.monk_tone_display || skinToneResult.monk_skin_tone})`
  };
};

/**
 * Error handler for API calls
 */
export const handleApiError = (error: unknown): string => {
  if (error instanceof Error) {
    return error.message;
  }
  
  if (typeof error === 'string') {
    return error;
  }
  
  return 'An unexpected error occurred';
};
