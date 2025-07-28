import { useState, useEffect, useCallback, useRef } from 'react';
import { useWebSocket } from '../../../hooks/useWebSocket';

export interface SkinToneResult {
  dominantColor: string;
  undertone: string;
  confidence: number;
  monkSkinTone: number;
  recommendations: ColorRecommendation[];
}

export interface ColorRecommendation {
  category: string;
  colors: string[];
  reason: string;
  confidence: number;
}

export interface AnalysisState {
  isAnalyzing: boolean;
  result: SkinToneResult | null;
  error: string | null;
  progress: number;
}

export const useColorAnalysis = () => {
  const [analysisState, setAnalysisState] = useState<AnalysisState>({
    isAnalyzing: false,
    result: null,
    error: null,
    progress: 0,
  });

  const analysisIdRef = useRef<string | null>(null);
  
  // WebSocket for real-time analysis updates
  const { isConnected, sendMessage } = useWebSocket('/api/ws/color-analysis', {
    onMessage: (data) => {
      if (data.type === 'analysis_progress') {
        setAnalysisState(prev => ({
          ...prev,
          progress: data.progress,
        }));
      } else if (data.type === 'analysis_complete') {
        setAnalysisState(prev => ({
          ...prev,
          isAnalyzing: false,
          result: data.result,
          progress: 100,
        }));
      } else if (data.type === 'analysis_error') {
        setAnalysisState(prev => ({
          ...prev,
          isAnalyzing: false,
          error: data.error,
          progress: 0,
        }));
      }
    },
  });

  const analyzeImage = useCallback(async (imageFile: File | string) => {
    try {
      setAnalysisState({
        isAnalyzing: true,
        result: null,
        error: null,
        progress: 0,
      });

      let imageData: string;
      
      if (typeof imageFile === 'string') {
        imageData = imageFile;
      } else {
        // Convert file to base64
        const reader = new FileReader();
        imageData = await new Promise((resolve, reject) => {
          reader.onload = () => resolve(reader.result as string);
          reader.onerror = reject;
          reader.readAsDataURL(imageFile);
        });
      }

      // Start analysis via WebSocket for real-time updates
      if (isConnected) {
        const analysisId = `analysis_${Date.now()}`;
        analysisIdRef.current = analysisId;
        
        sendMessage({
          type: 'start_analysis',
          analysisId,
          imageData,
          options: {
            includePalette: true,
            includeUndertone: true,
            includeRecommendations: true,
          },
        });
      } else {
        // Fallback to traditional API call
        const response = await fetch('/api/color-analysis/analyze', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            image: imageData,
            options: {
              includePalette: true,
              includeUndertone: true,
              includeRecommendations: true,
            },
          }),
        });

        if (!response.ok) {
          throw new Error('Analysis failed');
        }

        const result = await response.json();
        setAnalysisState({
          isAnalyzing: false,
          result,
          error: null,
          progress: 100,
        });
      }
    } catch (error) {
      setAnalysisState({
        isAnalyzing: false,
        result: null,
        error: error instanceof Error ? error.message : 'Analysis failed',
        progress: 0,
      });
    }
  }, [isConnected, sendMessage]);

  const cancelAnalysis = useCallback(() => {
    if (analysisIdRef.current && isConnected) {
      sendMessage({
        type: 'cancel_analysis',
        analysisId: analysisIdRef.current,
      });
    }
    
    setAnalysisState({
      isAnalyzing: false,
      result: null,
      error: null,
      progress: 0,
    });
    
    analysisIdRef.current = null;
  }, [isConnected, sendMessage]);

  const clearResults = useCallback(() => {
    setAnalysisState({
      isAnalyzing: false,
      result: null,
      error: null,
      progress: 0,
    });
  }, []);

  return {
    ...analysisState,
    analyzeImage,
    cancelAnalysis,
    clearResults,
    isConnected,
  };
};

// Advanced ML analysis hook for future enhancement
export const useAdvancedColorAnalysis = () => {
  const [mlModel, setMlModel] = useState<any>(null);
  const [isModelLoading, setIsModelLoading] = useState(false);

  useEffect(() => {
    // Load TensorFlow.js model for client-side analysis
    const loadModel = async () => {
      try {
        setIsModelLoading(true);
        // In future: Load actual TensorFlow.js model
        // const model = await tf.loadLayersModel('/models/skin-tone-analyzer.json');
        // setMlModel(model);
        
        // For now, simulate model loading
        await new Promise(resolve => setTimeout(resolve, 1000));
        setMlModel({ loaded: true });
      } catch (error) {
        console.error('Failed to load ML model:', error);
      } finally {
        setIsModelLoading(false);
      }
    };

    loadModel();
  }, []);

  const analyzeWithML = useCallback(async (imageData: ImageData) => {
    if (!mlModel) {
      throw new Error('ML model not loaded');
    }

    // Future implementation: Use TensorFlow.js for client-side analysis
    // const tensor = tf.browser.fromPixels(imageData);
    // const prediction = await mlModel.predict(tensor);
    // return prediction;

    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          skinTone: 'warm',
          confidence: 0.89,
          undertone: 'golden',
        });
      }, 500);
    });
  }, [mlModel]);

  return {
    mlModel,
    isModelLoading,
    analyzeWithML,
  };
};
