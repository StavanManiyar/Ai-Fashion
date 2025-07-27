import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Seasons } from '../lib/types/seasons';
import type { SeasonInfo } from '../lib/types/seasons';
import { seasonsData } from '../lib/data/seasons';
import { colorPalettes } from '../lib/data/colorPalettes';
import { ExternalLink, User, Palette } from 'lucide-react';

interface ColorAnalysisProps {
  season?: Seasons;
  detectedSkinTone?: {
    id: string;
    name: string;
    hex_code: string;
    display_name: string;
  };
  skinToneId?: string;
}

interface ColorPaletteData {
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

const ColorAnalysis: React.FC<ColorAnalysisProps> = ({ season, detectedSkinTone, skinToneId }) => {
  const [paletteData, setPaletteData] = useState<ColorPaletteData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch color palette from database when skinToneId is provided
  useEffect(() => {
    if (skinToneId) {
      fetchColorPalette(skinToneId);
    }
  }, [skinToneId]);

  const fetchColorPalette = async (toneId: string) => {
    setLoading(true);
    setError(null);
    
    try {
      // Import API_BASE_URL from config
      const { API_BASE_URL } = await import('../config/api');
      const apiUrl = `${API_BASE_URL}/api/colors/palette/${toneId}?include_skin_tone=true`;
      
      console.log('Fetching color palette from:', apiUrl);
      
      const response = await fetch(apiUrl);
      if (!response.ok) {
        throw new Error(`Failed to fetch color palette: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('Color palette data received:', data);
      setPaletteData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load colors');
      console.error('Error fetching color palette:', err);
    } finally {
      setLoading(false);
    }
  };

  // If we have database palette data, render it
  if (paletteData) {
    return (
      <div className="bg-white rounded-xl p-6 shadow-lg">
        {/* Detected Skin Tone Section */}
        {paletteData.detected_skin_tone && (
          <div className="mb-6 p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg border border-purple-100">
            <div className="flex items-center mb-3">
              <User className="w-5 h-5 text-purple-600 mr-2" />
              <h4 className="text-lg font-semibold text-gray-800">Your Detected Skin Tone</h4>
            </div>
            <div className="flex items-center">
              <div 
                className="w-16 h-16 rounded-full shadow-lg mr-4 border-2 border-white"
                style={{ backgroundColor: paletteData.detected_skin_tone.hex_code }}
              />
              <div>
                <h5 className="text-xl font-bold text-gray-900">
                  {paletteData.detected_skin_tone.display_name}
                </h5>
                <p className="text-gray-600">
                  {paletteData.detected_skin_tone.hex_code}
                </p>
                <span className="inline-block mt-1 px-2 py-1 bg-purple-100 text-purple-800 text-sm rounded-full">
                  {paletteData.detected_skin_tone.name}
                </span>
              </div>
            </div>
          </div>
        )}

        <div className="flex items-center mb-6">
          <Palette className="w-6 h-6 text-purple-600 mr-2" />
          <h3 className="text-2xl font-bold text-gray-900">Your Personalized Color Palette</h3>
        </div>
        
        {loading && (
          <div className="text-center py-4">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto"></div>
            <p className="text-gray-600 mt-2">Loading your color palette...</p>
          </div>
        )}
        
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-800">Error: {error}</p>
          </div>
        )}
        
        {/* Recommended Colors */}
        <div className="mb-6">
          <h4 className="text-lg font-medium text-gray-800 mb-3">
            Colors That Flatter You ({paletteData.total_recommended})
          </h4>
          <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-3 mb-4">
            {paletteData.recommended_colors.slice(0, 12).map((color, index) => (
              <div key={index} className="group">
                <div
                  className="w-12 h-12 rounded-lg shadow-md relative group-hover:scale-105 transition-transform cursor-pointer"
                  style={{ backgroundColor: color.hex_code }}
                  title={`${color.color_name} - ${color.hex_code}`}
                >
                  <div className="absolute inset-0 rounded-lg opacity-0 group-hover:opacity-100 bg-black bg-opacity-50 flex items-center justify-center transition-opacity">
                    <span className="text-white text-xs font-medium">{color.hex_code}</span>
                  </div>
                </div>
                <p className="text-xs text-gray-600 mt-1 text-center truncate">
                  {color.color_name}
                </p>
              </div>
            ))}
          </div>
          {paletteData.recommended_colors.length > 12 && (
            <p className="text-sm text-gray-500 italic">
              +{paletteData.recommended_colors.length - 12} more recommended colors
            </p>
          )}
        </div>
        
        {/* Colors to avoid */}
        <div className="mb-6">
          <h4 className="text-lg font-medium text-gray-800 mb-3">
            Colors to Avoid ({paletteData.total_avoid})
          </h4>
          <div className="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 gap-2">
            {paletteData.colors_to_avoid.slice(0, 8).map((color, index) => (
              <div key={index} className="group">
                <div
                  className="w-8 h-8 rounded-lg shadow-md relative group-hover:scale-105 transition-transform cursor-pointer opacity-75"
                  style={{ backgroundColor: color.hex_code }}
                  title={`${color.color_name} - ${color.hex_code}`}
                >
                  <div className="absolute inset-0 rounded-lg opacity-0 group-hover:opacity-100 bg-black bg-opacity-50 flex items-center justify-center transition-opacity">
                    <span className="text-white text-xs">×</span>
                  </div>
                </div>
                <p className="text-xs text-gray-500 mt-1 text-center truncate">
                  {color.color_name}
                </p>
              </div>
            ))}
          </div>
          {paletteData.colors_to_avoid.length > 8 && (
            <p className="text-sm text-gray-500 italic">
              +{paletteData.colors_to_avoid.length - 8} more colors to avoid
            </p>
          )}
        </div>
        
        {/* Link to detailed palette */}
        {skinToneId && (
          <Link 
            to={`/monk-colors/${skinToneId}`}
            className="inline-flex items-center text-purple-600 font-medium hover:text-purple-800 transition-colors"
          >
            View complete color analysis
            <ExternalLink className="w-4 h-4 ml-2" />
          </Link>
        )}
      </div>
    );
  }

  // Fallback to original seasonal analysis if no database data
  if (!season) return null;

  const seasonInfo: SeasonInfo = seasonsData[season];
  const palette = colorPalettes[season];

  return (
    <div className="bg-white rounded-xl p-6 shadow-lg">
      {/* Show detected skin tone if provided */}
      {detectedSkinTone && (
        <div className="mb-6 p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg border border-purple-100">
          <div className="flex items-center mb-3">
            <User className="w-5 h-5 text-purple-600 mr-2" />
            <h4 className="text-lg font-semibold text-gray-800">Your Detected Skin Tone</h4>
          </div>
          <div className="flex items-center">
            <div 
              className="w-16 h-16 rounded-full shadow-lg mr-4 border-2 border-white"
              style={{ backgroundColor: detectedSkinTone.hex_code }}
            />
            <div>
              <h5 className="text-xl font-bold text-gray-900">
                {detectedSkinTone.display_name}
              </h5>
              <p className="text-gray-600">
                {detectedSkinTone.hex_code}
              </p>
              <span className="inline-block mt-1 px-2 py-1 bg-purple-100 text-purple-800 text-sm rounded-full">
                {detectedSkinTone.name}
              </span>
            </div>
          </div>
        </div>
      )}

      <h3 className={`text-2xl font-bold mb-4 ${seasonInfo.textColor}`}>
        {season}
      </h3>
      <p className="text-gray-600 mb-6">{seasonInfo.description}</p>
      
      {/* Initial color palette */}
      <div className="mb-6">
        <h4 className="text-lg font-medium text-gray-800 mb-3">Your Color Palette</h4>
        <div className="grid grid-cols-6 gap-2 mb-4">
          {palette?.flatteringColors.slice(0, 6).map((color, index) => (
            <div
              key={index}
              className="w-10 h-10 rounded-full shadow-md relative group"
              style={{ backgroundColor: color.hex }}
            >
              <div className="absolute inset-0 rounded-full opacity-0 group-hover:opacity-100 bg-black bg-opacity-50 flex items-center justify-center transition-opacity">
                <span className="text-white text-xs">{color.name}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {/* Colors to avoid */}
      <div className="mb-6">
        <h4 className="text-lg font-medium text-gray-800 mb-3">Colors to Avoid</h4>
        <div className="grid grid-cols-4 gap-2">
          {palette?.colorsToAvoid.slice(0, 4).map((color, index) => (
            <div
              key={index}
              className="w-8 h-8 rounded-full shadow-md relative group"
              style={{ backgroundColor: color.hex }}
            >
              <div className="absolute inset-0 rounded-full opacity-0 group-hover:opacity-100 bg-black bg-opacity-50 flex items-center justify-center transition-opacity">
                <span className="text-white text-xs">{color.name}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {/* Link to detailed color palette page */}
      <Link 
        to={`/colors/${season}`}
        className="inline-flex items-center text-purple-600 font-medium hover:text-purple-800 transition-colors"
      >
        View detailed color palette
        <ExternalLink className="w-4 h-4 ml-2" />
      </Link>
    </div>
  );
};

export default ColorAnalysis; 