import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';

// Mock Zustand stores
const mockUserStore = {
  user: null,
  isAuthenticated: false,
  preferences: {
    favoriteColors: [],
    style: 'casual' as const,
    notifications: {
      email: true,
      push: true,
      recommendations: true,
    },
    analytics: {
      trackingEnabled: true,
      personalizedAds: false,
    },
  },
  setUser: vi.fn(),
  updatePreferences: vi.fn(),
  logout: vi.fn(),
};

const mockColorAnalysisStore = {
  currentAnalysis: null,
  analysisHistory: [],
  isAnalyzing: false,
  progress: 0,
  error: null,
  setCurrentAnalysis: vi.fn(),
  addToHistory: vi.fn(),
  setAnalyzing: vi.fn(),
  setError: vi.fn(),
  clearHistory: vi.fn(),
};

const mockProductStore = {
  favorites: [],
  cart: [],
  recentlyViewed: [],
  recommendations: [],
  filters: {
    category: [],
    priceRange: [0, 1000] as [number, number],
    colors: [],
    brands: [],
    rating: 0,
    sortBy: 'relevance' as const,
  },
  addToFavorites: vi.fn(),
  removeFromFavorites: vi.fn(),
  addToCart: vi.fn(),
  removeFromCart: vi.fn(),
  updateCartQuantity: vi.fn(),
  addToRecentlyViewed: vi.fn(),
  setRecommendations: vi.fn(),
  updateFilters: vi.fn(),
  clearCart: vi.fn(),
};

// Mock store hooks
vi.mock('../store', () => ({
  useUserStore: (selector?: any) => selector ? selector(mockUserStore) : mockUserStore,
  useColorAnalysisStore: (selector?: any) => selector ? selector(mockColorAnalysisStore) : mockColorAnalysisStore,
  useProductStore: (selector?: any) => selector ? selector(mockProductStore) : mockProductStore,
}));

// Create a custom render function that includes providers
const AllTheProviders: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {children}
      </BrowserRouter>
    </QueryClientProvider>
  );
};

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllTheProviders, ...options });

// Mock data factories
export const createMockUser = (overrides = {}) => ({
  id: 'user-1',
  email: 'test@example.com',
  name: 'Test User',
  avatar: 'https://example.com/avatar.jpg',
  createdAt: '2023-01-01T00:00:00Z',
  ...overrides,
});

export const createMockProduct = (overrides = {}) => ({
  id: 'product-1',
  name: 'Test Product',
  brand: 'Test Brand',
  price: 29.99,
  image: 'https://example.com/product.jpg',
  category: 'makeup',
  colors: ['#FF0000', '#00FF00'],
  rating: 4.5,
  reviewCount: 100,
  ...overrides,
});

export const createMockAnalysisResult = (overrides = {}) => ({
  id: 'analysis-1',
  dominantColor: '#8B4513',
  undertone: 'warm',
  confidence: 0.85,
  monkSkinTone: 6,
  recommendations: [
    {
      category: 'makeup',
      colors: ['#FF6B6B', '#4ECDC4'],
      reason: 'These colors complement your warm undertone',
      confidence: 0.9,
    },
  ],
  timestamp: '2023-01-01T00:00:00Z',
  imageUrl: 'https://example.com/analysis.jpg',
  ...overrides,
});

// Helper to mock fetch responses
export const mockFetch = (data: any, ok = true, status = 200) => {
  global.fetch = vi.fn().mockResolvedValue({
    ok,
    status,
    json: () => Promise.resolve(data),
    text: () => Promise.resolve(JSON.stringify(data)),
  });
};

// Helper to mock WebSocket
export const mockWebSocket = () => {
  const mockWs = {
    send: vi.fn(),
    close: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    readyState: WebSocket.OPEN,
  };
  
  global.WebSocket = vi.fn().mockImplementation(() => mockWs);
  return mockWs;
};

// Helper to wait for async operations
export const waitFor = (callback: () => void, timeout = 1000) => {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      reject(new Error('Timeout waiting for condition'));
    }, timeout);

    const check = () => {
      try {
        callback();
        clearTimeout(timer);
        resolve(true);
      } catch (error) {
        setTimeout(check, 10);
      }
    };

    check();
  });
};

// Export everything
export * from '@testing-library/react';
export { customRender as render };
export { mockUserStore, mockColorAnalysisStore, mockProductStore };
