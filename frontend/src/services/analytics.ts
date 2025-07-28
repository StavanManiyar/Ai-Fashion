import mixpanel from 'mixpanel-browser';
import { useAnalyticsStore } from '../store';

// Initialize Mixpanel
mixpanel.init(import.meta.env.VITE_MIXPANEL_TOKEN || 'demo-token', {
  debug: import.meta.env.DEV,
  track_pageview: true,
  persistence: 'localStorage',
});

// Initialize Google Analytics 4
declare global {
  interface Window {
    gtag: (...args: any[]) => void;
    dataLayer: any[];
  }
}

// Load GA4 script
if (typeof window !== 'undefined' && import.meta.env.VITE_GA4_MEASUREMENT_ID) {
  const script = document.createElement('script');
  script.async = true;
  script.src = `https://www.googletagmanager.com/gtag/js?id=${import.meta.env.VITE_GA4_MEASUREMENT_ID}`;
  document.head.appendChild(script);

  window.dataLayer = window.dataLayer || [];
  window.gtag = function gtag() {
    window.dataLayer.push(arguments);
  };
  window.gtag('js', new Date());
  window.gtag('config', import.meta.env.VITE_GA4_MEASUREMENT_ID);
}

export interface AnalyticsEvent {
  name: string;
  properties?: Record<string, any>;
  userId?: string;
}

export interface UserProperties {
  skinTone?: string;
  favoriteColors?: string[];
  style?: string;
  age?: number;
  location?: string;
  subscriptionTier?: string;
}

export class AnalyticsService {
  private static instance: AnalyticsService;
  private isInitialized = false;
  private userId: string | null = null;

  private constructor() {
    this.initialize();
  }

  public static getInstance(): AnalyticsService {
    if (!AnalyticsService.instance) {
      AnalyticsService.instance = new AnalyticsService();
    }
    return AnalyticsService.instance;
  }

  private initialize() {
    if (this.isInitialized) return;

    // Set up error tracking
    window.addEventListener('error', (event) => {
      this.trackError({
        message: event.message,
        filename: event.filename,
        line: event.lineno,
        column: event.colno,
        stack: event.error?.stack,
      });
    });

    // Set up unhandled promise rejection tracking
    window.addEventListener('unhandledrejection', (event) => {
      this.trackError({
        message: 'Unhandled Promise Rejection',
        reason: event.reason,
      });
    });

    this.isInitialized = true;
  }

  // User identification
  public identify(userId: string, properties?: UserProperties) {
    this.userId = userId;
    
    // Mixpanel identify
    mixpanel.identify(userId);
    if (properties) {
      mixpanel.people.set(properties);
    }

    // GA4 identify
    if (window.gtag) {
      window.gtag('config', import.meta.env.VITE_GA4_MEASUREMENT_ID, {
        user_id: userId,
        custom_map: properties,
      });
    }

    // Store in local analytics store
    const store = useAnalyticsStore.getState();
    store.addEvent({
      id: `event_${Date.now()}`,
      type: 'user_identified',
      data: { userId, properties },
      timestamp: new Date().toISOString(),
    });
  }

  // Track events
  public track(event: AnalyticsEvent) {
    const { name, properties = {}, userId } = event;
    
    // Add session and timing data
    const enrichedProperties = {
      ...properties,
      sessionId: useAnalyticsStore.getState().sessionId,
      timestamp: new Date().toISOString(),
      userId: userId || this.userId,
      page: window.location.pathname,
      referrer: document.referrer,
      userAgent: navigator.userAgent,
    };

    // Mixpanel track
    mixpanel.track(name, enrichedProperties);

    // GA4 track
    if (window.gtag) {
      window.gtag('event', name, enrichedProperties);
    }

    // Store in local analytics store
    const store = useAnalyticsStore.getState();
    store.addEvent({
      id: `event_${Date.now()}`,
      type: name,
      data: enrichedProperties,
      timestamp: new Date().toISOString(),
    });
  }

  // Track page views
  public trackPageView(page: string, properties?: Record<string, any>) {
    const pageData = {
      page,
      timestamp: new Date().toISOString(),
      ...properties,
    };

    // Mixpanel track
    mixpanel.track('Page View', pageData);

    // GA4 track
    if (window.gtag) {
      window.gtag('event', 'page_view', {
        page_title: document.title,
        page_location: window.location.href,
        ...pageData,
      });
    }

    // Store in local analytics store
    const store = useAnalyticsStore.getState();
    store.addPageView({
      page,
      timestamp: new Date().toISOString(),
    });
  }

  // Track user interactions
  public trackInteraction(
    type: 'click' | 'scroll' | 'form_submit' | 'search' | 'product_view',
    element: string,
    data?: Record<string, any>
  ) {
    const interaction = {
      type,
      element,
      data,
      timestamp: new Date().toISOString(),
    };

    this.track({
      name: `user_${type}`,
      properties: interaction,
    });

    // Store in local analytics store
    const store = useAnalyticsStore.getState();
    store.addInteraction(interaction);
  }

  // Track errors
  public trackError(error: {
    message: string;
    filename?: string;
    line?: number;
    column?: number;
    stack?: string;
    reason?: any;
  }) {
    this.track({
      name: 'error_occurred',
      properties: {
        ...error,
        userId: this.userId,
        page: window.location.pathname,
      },
    });
  }

  // E-commerce tracking
  public trackPurchase(transactionData: {
    transactionId: string;
    value: number;
    currency: string;
    items: Array<{
      itemId: string;
      itemName: string;
      category: string;
      quantity: number;
      price: number;
    }>;
  }) {
    // Mixpanel track
    mixpanel.track('Purchase', transactionData);

    // GA4 Enhanced E-commerce
    if (window.gtag) {
      window.gtag('event', 'purchase', {
        transaction_id: transactionData.transactionId,
        value: transactionData.value,
        currency: transactionData.currency,
        items: transactionData.items.map(item => ({
          item_id: item.itemId,
          item_name: item.itemName,
          category: item.category,
          quantity: item.quantity,
          price: item.price,
        })),
      });
    }
  }

  // Color analysis specific tracking
  public trackColorAnalysis(data: {
    analysisId: string;
    skinTone?: string;
    confidence?: number;
    processingTime?: number;
    imageSize?: number;
    method?: string;
  }) {
    this.track({
      name: 'color_analysis_completed',
      properties: data,
    });
  }

  // Product recommendation tracking
  public trackRecommendation(data: {
    recommendationType: string;
    productIds: string[];
    skinTone?: string;
    confidence?: number;
    source: string;
  }) {
    this.track({
      name: 'recommendation_generated',
      properties: data,
    });
  }

  // A/B Testing support
  public trackExperiment(experimentName: string, variant: string, properties?: Record<string, any>) {
    this.track({
      name: 'experiment_viewed',
      properties: {
        experimentName,
        variant,
        ...properties,
      },
    });
  }

  // Funnel tracking
  public trackFunnelStep(funnelName: string, step: number, stepName: string, properties?: Record<string, any>) {
    this.track({
      name: 'funnel_step',
      properties: {
        funnelName,
        step,
        stepName,
        ...properties,
      },
    });
  }

  // User engagement tracking
  public trackEngagement(duration: number, scrollDepth: number, interactions: number) {
    this.track({
      name: 'page_engagement',
      properties: {
        duration,
        scrollDepth,
        interactions,
        page: window.location.pathname,
      },
    });
  }

  // Revenue tracking
  public trackRevenue(data: {
    amount: number;
    currency: string;
    source: string;
    category: string;
  }) {
    // Mixpanel revenue tracking
    mixpanel.people.track_charge(data.amount, {
      $time: new Date(),
      source: data.source,
      category: data.category,
    });

    this.track({
      name: 'revenue_generated',
      properties: data,
    });
  }

  // User properties update
  public updateUserProperties(properties: UserProperties) {
    // Mixpanel
    mixpanel.people.set(properties);

    // GA4
    if (window.gtag) {
      window.gtag('config', import.meta.env.VITE_GA4_MEASUREMENT_ID, {
        custom_map: properties,
      });
    }
  }

  // Reset user session
  public reset() {
    this.userId = null;
    mixpanel.reset();
    
    const store = useAnalyticsStore.getState();
    store.clearEvents();
  }

  // Get analytics dashboard data
  public async getDashboardData(): Promise<{
    totalEvents: number;
    uniqueUsers: number;
    pageViews: number;
    topPages: Array<{ page: string; views: number }>;
    userFlow: Array<{ step: string; users: number; conversionRate: number }>;
  }> {
    const store = useAnalyticsStore.getState();
    const { events, pageViews } = store;

    // This would typically come from your analytics backend
    return {
      totalEvents: events.length,
      uniqueUsers: new Set(events.map(e => e.data.userId).filter(Boolean)).size,
      pageViews: pageViews.length,
      topPages: this.getTopPages(pageViews),
      userFlow: this.calculateUserFlow(events),
    };
  }

  private getTopPages(pageViews: Array<{ page: string; timestamp: string }>): Array<{ page: string; views: number }> {
    const pageCount = pageViews.reduce((acc, view) => {
      acc[view.page] = (acc[view.page] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return Object.entries(pageCount)
      .map(([page, views]) => ({ page, views }))
      .sort((a, b) => b.views - a.views)
      .slice(0, 10);
  }

  private calculateUserFlow(events: Array<{ type: string; data: any; timestamp: string }>): Array<{ step: string; users: number; conversionRate: number }> {
    // Simplified user flow calculation
    const funnelSteps = ['page_view', 'color_analysis_started', 'color_analysis_completed', 'product_viewed', 'purchase'];
    const stepCounts = funnelSteps.map(step => ({
      step,
      users: events.filter(e => e.type === step).length,
      conversionRate: 0,
    }));

    // Calculate conversion rates
    for (let i = 1; i < stepCounts.length; i++) {
      if (stepCounts[i - 1].users > 0) {
        stepCounts[i].conversionRate = (stepCounts[i].users / stepCounts[i - 1].users) * 100;
      }
    }

    return stepCounts;
  }
}

// Export singleton instance
export const analytics = AnalyticsService.getInstance();

// React hook for analytics
export const useAnalytics = () => {
  return {
    track: analytics.track.bind(analytics),
    identify: analytics.identify.bind(analytics),
    trackPageView: analytics.trackPageView.bind(analytics),
    trackInteraction: analytics.trackInteraction.bind(analytics),
    trackColorAnalysis: analytics.trackColorAnalysis.bind(analytics),
    trackRecommendation: analytics.trackRecommendation.bind(analytics),
    trackPurchase: analytics.trackPurchase.bind(analytics),
    updateUserProperties: analytics.updateUserProperties.bind(analytics),
    getDashboardData: analytics.getDashboardData.bind(analytics),
  };
};
