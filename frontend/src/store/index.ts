import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { devtools } from 'zustand/middleware';

// User state
interface UserState {
  user: User | null;
  isAuthenticated: boolean;
  preferences: UserPreferences;
  setUser: (user: User | null) => void;
  updatePreferences: (preferences: Partial<UserPreferences>) => void;
  logout: () => void;
}

interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  createdAt: string;
}

interface UserPreferences {
  skinTone?: string;
  favoriteColors: string[];
  style: 'casual' | 'formal' | 'trendy' | 'classic';
  notifications: {
    email: boolean;
    push: boolean;
    recommendations: boolean;
  };
  analytics: {
    trackingEnabled: boolean;
    personalizedAds: boolean;
  };
}

// Color Analysis state
interface ColorAnalysisState {
  currentAnalysis: SkinToneResult | null;
  analysisHistory: SkinToneResult[];
  isAnalyzing: boolean;
  progress: number;
  error: string | null;
  setCurrentAnalysis: (result: SkinToneResult | null) => void;
  addToHistory: (result: SkinToneResult) => void;
  setAnalyzing: (isAnalyzing: boolean, progress?: number) => void;
  setError: (error: string | null) => void;
  clearHistory: () => void;
}

interface SkinToneResult {
  id: string;
  dominantColor: string;
  undertone: string;
  confidence: number;
  monkSkinTone: number;
  recommendations: ColorRecommendation[];
  timestamp: string;
  imageUrl?: string;
}

interface ColorRecommendation {
  category: string;
  colors: string[];
  reason: string;
  confidence: number;
}

// Product state
interface ProductState {
  favorites: string[];
  cart: CartItem[];
  recentlyViewed: string[];
  recommendations: Product[];
  filters: ProductFilters;
  addToFavorites: (productId: string) => void;
  removeFromFavorites: (productId: string) => void;
  addToCart: (item: CartItem) => void;
  removeFromCart: (productId: string) => void;
  updateCartQuantity: (productId: string, quantity: number) => void;
  addToRecentlyViewed: (productId: string) => void;
  setRecommendations: (products: Product[]) => void;
  updateFilters: (filters: Partial<ProductFilters>) => void;
  clearCart: () => void;
}

interface CartItem {
  productId: string;
  quantity: number;
  selectedVariant?: string;
  addedAt: string;
}

interface Product {
  id: string;
  name: string;
  brand: string;
  price: number;
  image: string;
  category: string;
  colors: string[];
  rating: number;
  reviewCount: number;
}

interface ProductFilters {
  category: string[];
  priceRange: [number, number];
  colors: string[];
  brands: string[];
  rating: number;
  sortBy: 'relevance' | 'price-low' | 'price-high' | 'rating' | 'newest';
}

// Analytics state
interface AnalyticsState {
  events: AnalyticsEvent[];
  sessionId: string;
  startTime: string;
  pageViews: PageView[];
  interactions: UserInteraction[];
  addEvent: (event: AnalyticsEvent) => void;
  addPageView: (page: PageView) => void;
  addInteraction: (interaction: UserInteraction) => void;
  clearEvents: () => void;
}

interface AnalyticsEvent {
  id: string;
  type: string;
  data: Record<string, any>;
  timestamp: string;
}

interface PageView {
  page: string;
  timestamp: string;
  duration?: number;
}

interface UserInteraction {
  type: 'click' | 'scroll' | 'form_submit' | 'search' | 'product_view';
  element: string;
  data?: Record<string, any>;
  timestamp: string;
}

// Create stores
export const useUserStore = create<UserState>()(
  devtools(
    persist(
      (set, get) => ({
        user: null,
        isAuthenticated: false,
        preferences: {
          favoriteColors: [],
          style: 'casual',
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
        setUser: (user) => set({ user, isAuthenticated: !!user }),
        updatePreferences: (newPreferences) =>
          set((state) => ({
            preferences: { ...state.preferences, ...newPreferences },
          })),
        logout: () => set({ user: null, isAuthenticated: false }),
      }),
      {
        name: 'user-storage',
        partialize: (state) => ({
          user: state.user,
          preferences: state.preferences,
        }),
      }
    )
  )
);

export const useColorAnalysisStore = create<ColorAnalysisState>()(
  devtools(
    persist(
      (set) => ({
        currentAnalysis: null,
        analysisHistory: [],
        isAnalyzing: false,
        progress: 0,
        error: null,
        setCurrentAnalysis: (result) => set({ currentAnalysis: result }),
        addToHistory: (result) =>
          set((state) => ({
            analysisHistory: [result, ...state.analysisHistory.slice(0, 9)], // Keep last 10
          })),
        setAnalyzing: (isAnalyzing, progress = 0) =>
          set({ isAnalyzing, progress }),
        setError: (error) => set({ error }),
        clearHistory: () => set({ analysisHistory: [] }),
      }),
      {
        name: 'color-analysis-storage',
        partialize: (state) => ({
          analysisHistory: state.analysisHistory,
        }),
      }
    )
  )
);

export const useProductStore = create<ProductState>()(
  devtools(
    persist(
      (set, get) => ({
        favorites: [],
        cart: [],
        recentlyViewed: [],
        recommendations: [],
        filters: {
          category: [],
          priceRange: [0, 1000],
          colors: [],
          brands: [],
          rating: 0,
          sortBy: 'relevance',
        },
        addToFavorites: (productId) =>
          set((state) => ({
            favorites: state.favorites.includes(productId)
              ? state.favorites
              : [...state.favorites, productId],
          })),
        removeFromFavorites: (productId) =>
          set((state) => ({
            favorites: state.favorites.filter((id) => id !== productId),
          })),
        addToCart: (item) =>
          set((state) => {
            const existingItem = state.cart.find(
              (cartItem) => cartItem.productId === item.productId
            );
            if (existingItem) {
              return {
                cart: state.cart.map((cartItem) =>
                  cartItem.productId === item.productId
                    ? { ...cartItem, quantity: cartItem.quantity + item.quantity }
                    : cartItem
                ),
              };
            }
            return { cart: [...state.cart, item] };
          }),
        removeFromCart: (productId) =>
          set((state) => ({
            cart: state.cart.filter((item) => item.productId !== productId),
          })),
        updateCartQuantity: (productId, quantity) =>
          set((state) => ({
            cart: state.cart.map((item) =>
              item.productId === productId ? { ...item, quantity } : item
            ),
          })),
        addToRecentlyViewed: (productId) =>
          set((state) => ({
            recentlyViewed: [
              productId,
              ...state.recentlyViewed.filter((id) => id !== productId),
            ].slice(0, 20), // Keep last 20
          })),
        setRecommendations: (recommendations) => set({ recommendations }),
        updateFilters: (newFilters) =>
          set((state) => ({
            filters: { ...state.filters, ...newFilters },
          })),
        clearCart: () => set({ cart: [] }),
      }),
      {
        name: 'product-storage',
        partialize: (state) => ({
          favorites: state.favorites,
          cart: state.cart,
          recentlyViewed: state.recentlyViewed,
        }),
      }
    )
  )
);

export const useAnalyticsStore = create<AnalyticsState>()(
  devtools((set) => ({
    events: [],
    sessionId: `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    startTime: new Date().toISOString(),
    pageViews: [],
    interactions: [],
    addEvent: (event) =>
      set((state) => ({
        events: [...state.events, event],
      })),
    addPageView: (page) =>
      set((state) => ({
        pageViews: [...state.pageViews, page],
      })),
    addInteraction: (interaction) =>
      set((state) => ({
        interactions: [...state.interactions, interaction],
      })),
    clearEvents: () => set({ events: [], pageViews: [], interactions: [] }),
  }))
);
