import { useState, useEffect, useRef } from 'react';

/**
 * Custom hook for intersection observer
 * Used for lazy loading and viewport detection
 */
export const useIntersectionObserver = (
  elementRef,
  { threshold = 0.1, root = null, rootMargin = '0%' } = {}
) => {
  const [isIntersecting, setIsIntersecting] = useState(false);
  const [hasIntersected, setHasIntersected] = useState(false);

  useEffect(() => {
    const element = elementRef?.current;
    if (!element) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        const isElementIntersecting = entry.isIntersecting;
        setIsIntersecting(isElementIntersecting);
        
        if (isElementIntersecting && !hasIntersected) {
          setHasIntersected(true);
        }
      },
      { threshold, root, rootMargin }
    );

    observer.observe(element);

    return () => {
      observer.unobserve(element);
    };
  }, [elementRef, threshold, root, rootMargin, hasIntersected]);

  return isIntersecting;
};

/**
 * Custom hook for lazy loading images
 */
export const useLazyImage = (src, placeholder = '') => {
  const [imageSrc, setImageSrc] = useState(placeholder);
  const [imageRef, setImageRef] = useState();
  const [isLoaded, setIsLoaded] = useState(false);
  const [isError, setIsError] = useState(false);

  useEffect(() => {
    let observer;
    
    if (imageRef && src) {
      if (IntersectionObserver) {
        observer = new IntersectionObserver(
          (entries) => {
            entries.forEach((entry) => {
              if (entry.isIntersecting) {
                setImageSrc(src);
                observer.unobserve(imageRef);
              }
            });
          },
          { threshold: 0.1 }
        );
        observer.observe(imageRef);
      } else {
        // Fallback for browsers without IntersectionObserver
        setImageSrc(src);
      }
    }

    return () => {
      if (observer && observer.unobserve) {
        observer.unobserve(imageRef);
      }
    };
  }, [imageRef, src]);

  const handleLoad = () => {
    setIsLoaded(true);
    setIsError(false);
  };

  const handleError = () => {
    setIsError(true);
    setIsLoaded(false);
  };

  return {
    setImageRef,
    imageSrc,
    isLoaded,
    isError,
    handleLoad,
    handleError
  };
};

/**
 * Custom hook for video lazy loading with progressive enhancement
 */
export const useLazyVideo = (videoData, options = {}) => {
  const {
    autoplay = false,
    preload = 'metadata',
    qualityPreference = 'auto'
  } = options;

  const [isLoaded, setIsLoaded] = useState(false);
  const [selectedQuality, setSelectedQuality] = useState(qualityPreference);
  const [videoSrc, setVideoSrc] = useState(null);
  const videoRef = useRef(null);

  // Determine best video source based on quality preference and available qualities
  const getOptimalVideoSource = () => {
    if (!videoData?.qualities?.length) return null;

    if (selectedQuality === 'auto') {
      // Use HLS for adaptive bitrate if available
      if (videoData.hls_playlist_url) {
        return {
          src: videoData.hls_playlist_url,
          type: 'application/x-mpegURL'
        };
      }
      
      // Fallback to highest quality available
      const sortedQualities = videoData.qualities.sort((a, b) => b.bitrate - a.bitrate);
      return {
        src: sortedQualities[0].cdn_url,
        type: 'video/mp4'
      };
    }

    // Find specific quality
    const quality = videoData.qualities.find(q => q.quality === selectedQuality);
    if (quality) {
      return {
        src: quality.cdn_url,
        type: 'video/mp4'
      };
    }

    // Fallback to first available quality
    return {
      src: videoData.qualities[0].cdn_url,
      type: 'video/mp4'
    };
  };

  useEffect(() => {
    if (videoData) {
      const source = getOptimalVideoSource();
      setVideoSrc(source);
    }
  }, [videoData, selectedQuality]);

  const loadVideo = () => {
    if (videoRef.current && videoSrc && !isLoaded) {
      setIsLoaded(true);
    }
  };

  return {
    videoRef,
    videoSrc,
    isLoaded,
    selectedQuality,
    setSelectedQuality,
    loadVideo,
    availableQualities: videoData?.qualities || []
  };
};

/**
 * Custom hook for performance monitoring
 */
export const usePerformanceMonitor = () => {
  const [metrics, setMetrics] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  const fetchMetrics = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/performance/dashboard');
      if (response.ok) {
        const data = await response.json();
        setMetrics(data);
      }
    } catch (error) {
      console.error('Failed to fetch performance metrics:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
    
    // Set up periodic refresh
    const interval = setInterval(fetchMetrics, 30000); // Every 30 seconds
    
    return () => clearInterval(interval);
  }, []);

  return { metrics, isLoading, refreshMetrics: fetchMetrics };
};

/**
 * Custom hook for video analytics and tracking
 */
export const useVideoAnalytics = (videoId) => {
  const [analytics, setAnalytics] = useState(null);
  const sessionIdRef = useRef(
    localStorage.getItem('sessionId') || `anon_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  );

  useEffect(() => {
    // Store session ID
    localStorage.setItem('sessionId', sessionIdRef.current);
  }, []);

  const recordView = async (metadata = {}) => {
    try {
      await fetch(`/api/videos/${videoId}/view`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionIdRef.current,
          ...metadata
        })
      });
    } catch (error) {
      console.error('Failed to record video view:', error);
    }
  };

  const recordProgress = async (currentTime, duration, quality = 'auto') => {
    const completionPercentage = duration > 0 ? (currentTime / duration) * 100 : 0;
    
    try {
      await fetch(`/api/videos/${videoId}/view`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionIdRef.current,
          watch_duration: Math.floor(currentTime),
          completion_percentage: Math.round(completionPercentage * 100) / 100,
          last_position: Math.floor(currentTime),
          quality: quality
        })
      });
    } catch (error) {
      console.error('Failed to record video progress:', error);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const response = await fetch(`/api/videos/${videoId}/analytics`);
      if (response.ok) {
        const data = await response.json();
        setAnalytics(data);
      }
    } catch (error) {
      console.error('Failed to fetch video analytics:', error);
    }
  };

  return {
    analytics,
    recordView,
    recordProgress,
    fetchAnalytics,
    sessionId: sessionIdRef.current
  };
};

/**
 * Custom hook for caching with TTL
 */
export const useCache = (key, ttl = 300000) => { // 5 minutes default
  const [data, setData] = useState(null);
  const [isStale, setIsStale] = useState(true);

  const getCacheKey = (key) => `cache_${key}`;
  const getTimestampKey = (key) => `cache_ts_${key}`;

  const get = () => {
    try {
      const cachedData = localStorage.getItem(getCacheKey(key));
      const timestamp = localStorage.getItem(getTimestampKey(key));
      
      if (cachedData && timestamp) {
        const age = Date.now() - parseInt(timestamp);
        if (age < ttl) {
          const parsed = JSON.parse(cachedData);
          setData(parsed);
          setIsStale(false);
          return parsed;
        }
      }
    } catch (error) {
      console.error('Cache get error:', error);
    }
    
    setIsStale(true);
    return null;
  };

  const set = (newData) => {
    try {
      localStorage.setItem(getCacheKey(key), JSON.stringify(newData));
      localStorage.setItem(getTimestampKey(key), Date.now().toString());
      setData(newData);
      setIsStale(false);
    } catch (error) {
      console.error('Cache set error:', error);
    }
  };

  const clear = () => {
    localStorage.removeItem(getCacheKey(key));
    localStorage.removeItem(getTimestampKey(key));
    setData(null);
    setIsStale(true);
  };

  useEffect(() => {
    get();
  }, [key]);

  return { data, isStale, get, set, clear };
};