import * as Sentry from '@sentry/react';
import { Integrations } from '@sentry/tracing';
import { analytics } from './analytics';

// Initialize Sentry
export const initializeMonitoring = () => {
  if (import.meta.env.PROD && import.meta.env.VITE_SENTRY_DSN) {
    Sentry.init({
      dsn: import.meta.env.VITE_SENTRY_DSN,
      integrations: [
        new Integrations.BrowserTracing({
          // Trace React Router navigation
          routingInstrumentation: Sentry.reactRouterV6Instrumentation(
            React.useEffect,
            useLocation,
            useNavigationType,
            createRoutesFromChildren,
            matchRoutes
          ),
        }),
      ],
      tracesSampleRate: 0.1, // 10% of transactions
      environment: import.meta.env.MODE,
      beforeSend(event) {
        // Filter out known issues or sensitive data
        if (event.exception) {
          const error = event.exception.values?.[0];
          if (error?.value?.includes('Non-Error promise rejection')) {
            return null;
          }
        }
        return event;
      },
    });

    // Set user context
    Sentry.configureScope((scope) => {
      scope.setTag('app.name', 'AI-Fashion');
      scope.setTag('app.version', '3.0.0');
      scope.setContext('device', {
        userAgent: navigator.userAgent,
        language: navigator.language,
        platform: navigator.platform,
      });
    });
  }
};

// Performance monitoring class
export class PerformanceMonitor {
  private static instance: PerformanceMonitor;
  private performanceObserver?: PerformanceObserver;
  private metrics: Map<string, number> = new Map();

  private constructor() {
    this.initializePerformanceObserver();
  }

  public static getInstance(): PerformanceMonitor {
    if (!PerformanceMonitor.instance) {
      PerformanceMonitor.instance = new PerformanceMonitor();
    }
    return PerformanceMonitor.instance;
  }

  private initializePerformanceObserver() {
    if ('PerformanceObserver' in window) {
      this.performanceObserver = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
          this.processPerformanceEntry(entry);
        });
      });

      // Observe different types of performance entries
      try {
        this.performanceObserver.observe({ entryTypes: ['navigation', 'resource', 'paint', 'largest-contentful-paint'] });
      } catch (error) {
        console.warn('Performance Observer not fully supported:', error);
      }
    }
  }

  private processPerformanceEntry(entry: PerformanceEntry) {
    switch (entry.entryType) {
      case 'navigation':
        this.trackNavigationTiming(entry as PerformanceNavigationTiming);
        break;
      case 'resource':
        this.trackResourceTiming(entry as PerformanceResourceTiming);
        break;
      case 'paint':
        this.trackPaintTiming(entry);
        break;
      case 'largest-contentful-paint':
        this.trackLCP(entry);
        break;
    }
  }

  private trackNavigationTiming(entry: PerformanceNavigationTiming) {
    const metrics = {
      'page.load_time': entry.loadEventEnd - entry.loadEventStart,
      'page.dom_content_loaded': entry.domContentLoadedEventEnd - entry.domContentLoadedEventStart,
      'page.dns_lookup': entry.domainLookupEnd - entry.domainLookupStart,
      'page.tcp_connection': entry.connectEnd - entry.connectStart,
      'page.server_response': entry.responseEnd - entry.requestStart,
    };

    Object.entries(metrics).forEach(([key, value]) => {
      if (value > 0) {
        this.metrics.set(key, value);
        this.reportMetric(key, value);
      }
    });
  }

  private trackResourceTiming(entry: PerformanceResourceTiming) {
    const duration = entry.responseEnd - entry.requestStart;
    
    if (entry.name.includes('.js')) {
      this.reportMetric('resource.javascript_load_time', duration);
    } else if (entry.name.includes('.css')) {
      this.reportMetric('resource.css_load_time', duration);
    } else if (entry.name.match(/\.(jpg|png|gif|webp|svg)$/)) {
      this.reportMetric('resource.image_load_time', duration);
    }
  }

  private trackPaintTiming(entry: PerformanceEntry) {
    if (entry.name === 'first-paint') {
      this.reportMetric('paint.first_paint', entry.startTime);
    } else if (entry.name === 'first-contentful-paint') {
      this.reportMetric('paint.first_contentful_paint', entry.startTime);
    }
  }

  private trackLCP(entry: PerformanceEntry) {
    this.reportMetric('paint.largest_contentful_paint', entry.startTime);
  }

  private reportMetric(name: string, value: number) {
    // Report to Sentry
    if (Sentry.getCurrentHub().getClient()) {
      Sentry.addBreadcrumb({
        category: 'performance',
        message: `${name}: ${value}ms`,
        level: 'info',
        data: { metric: name, value },
      });
    }

    // Report to analytics
    analytics.track({
      name: 'performance_metric',
      properties: {
        metric_name: name,
        metric_value: value,
        page: window.location.pathname,
      },
    });
  }

  // Custom timing methods
  public startTiming(name: string) {
    performance.mark(`${name}-start`);
  }

  public endTiming(name: string) {
    performance.mark(`${name}-end`);
    performance.measure(name, `${name}-start`, `${name}-end`);
    
    const measure = performance.getEntriesByName(name)[0];
    if (measure) {
      this.reportMetric(`custom.${name}`, measure.duration);
    }
  }

  // Web Vitals tracking
  public trackWebVitals() {
    // Track Core Web Vitals
    this.trackCLS();
    this.trackFID();
    this.trackTTFB();
  }

  private trackCLS() {
    let clsValue = 0;
    let sessionValue = 0;
    let sessionEntries: PerformanceEventTiming[] = [];

    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries() as PerformanceEventTiming[]) {
        // Only count layout shifts without recent user input
        if (!entry.hadRecentInput) {
          const firstSessionEntry = sessionEntries[0];
          const lastSessionEntry = sessionEntries[sessionEntries.length - 1];

          // If the entry occurred less than 1 second after the previous entry
          // and less than 5 seconds after the first entry in the session,
          // include it in the current session. Otherwise, start a new session.
          if (sessionValue &&
              entry.startTime - lastSessionEntry.startTime < 1000 &&
              entry.startTime - firstSessionEntry.startTime < 5000) {
            sessionValue += entry.value;
            sessionEntries.push(entry);
          } else {
            sessionValue = entry.value;
            sessionEntries = [entry];
          }

          // If the current session value is larger than the current CLS value,
          // update CLS and the entries contributing to it.
          if (sessionValue > clsValue) {
            clsValue = sessionValue;
          }
        }
      }
    });

    observer.observe({ type: 'layout-shift', buffered: true });

    // Report CLS when the page is hidden
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'hidden') {
        this.reportMetric('vitals.cumulative_layout_shift', clsValue);
      }
    });
  }

  private trackFID() {
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.entryType === 'first-input') {
          const fid = entry.processingStart - entry.startTime;
          this.reportMetric('vitals.first_input_delay', fid);
          observer.disconnect();
        }
      }
    });

    observer.observe({ type: 'first-input', buffered: true });
  }

  private trackTTFB() {
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.entryType === 'navigation') {
          const nav = entry as PerformanceNavigationTiming;
          const ttfb = nav.responseStart - nav.requestStart;
          this.reportMetric('vitals.time_to_first_byte', ttfb);
        }
      }
    });

    observer.observe({ type: 'navigation', buffered: true });
  }

  // Error tracking
  public captureException(error: Error, context?: Record<string, any>) {
    console.error('Captured exception:', error);
    
    if (Sentry.getCurrentHub().getClient()) {
      Sentry.captureException(error, {
        contexts: {
          custom: context,
        },
      });
    }

    analytics.track({
      name: 'error_occurred',
      properties: {
        error_message: error.message,
        error_stack: error.stack,
        ...context,
      },
    });
  }

  // User feedback
  public showUserFeedback() {
    if (Sentry.getCurrentHub().getClient()) {
      Sentry.showReportDialog();
    }
  }

  // Memory monitoring
  public trackMemoryUsage() {
    if ('memory' in performance) {
      const memory = (performance as any).memory;
      this.reportMetric('memory.used_js_heap_size', memory.usedJSHeapSize);
      this.reportMetric('memory.total_js_heap_size', memory.totalJSHeapSize);
      this.reportMetric('memory.js_heap_size_limit', memory.jsHeapSizeLimit);
    }
  }

  // Cleanup
  public disconnect() {
    if (this.performanceObserver) {
      this.performanceObserver.disconnect();
    }
  }

  // Get current metrics
  public getMetrics(): Record<string, number> {
    return Object.fromEntries(this.metrics);
  }
}

// Export singleton instance
export const performanceMonitor = PerformanceMonitor.getInstance();

// React hook for performance monitoring
export const usePerformanceMonitoring = () => {
  React.useEffect(() => {
    performanceMonitor.trackWebVitals();
    performanceMonitor.trackMemoryUsage();

    return () => {
      performanceMonitor.disconnect();
    };
  }, []);

  return {
    startTiming: performanceMonitor.startTiming.bind(performanceMonitor),
    endTiming: performanceMonitor.endTiming.bind(performanceMonitor),
    captureException: performanceMonitor.captureException.bind(performanceMonitor),
    showUserFeedback: performanceMonitor.showUserFeedback.bind(performanceMonitor),
    getMetrics: performanceMonitor.getMetrics.bind(performanceMonitor),
  };
};
