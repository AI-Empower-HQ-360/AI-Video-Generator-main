import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useIntersectionObserver } from '../hooks/useIntersectionObserver';

const VideoPlayer = ({ 
  videoId, 
  autoplay = false, 
  controls = true, 
  lazy = true,
  preload = 'metadata',
  onViewRecord = null,
  className = '',
  poster = null
}) => {
  const [videoData, setVideoData] = useState(null);
  const [selectedQuality, setSelectedQuality] = useState('auto');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hasStartedPlaying, setHasStartedPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  
  const videoRef = useRef(null);
  const containerRef = useRef(null);
  const viewRecordedRef = useRef(false);
  
  // Intersection observer for lazy loading
  const isInView = useIntersectionObserver(containerRef, {
    threshold: 0.1,
    rootMargin: '50px'
  });
  
  // Load video data when component mounts or comes into view
  useEffect(() => {
    if (!lazy || isInView) {
      loadVideoData();
    }
  }, [videoId, isInView, lazy]);
  
  const loadVideoData = async () => {
    if (!videoId) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`/api/videos/${videoId}`);
      if (!response.ok) {
        throw new Error('Failed to load video');
      }
      
      const data = await response.json();
      setVideoData(data.video);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Get video source URL based on selected quality
  const getVideoSource = useCallback(() => {
    if (!videoData) return null;
    
    if (selectedQuality === 'auto' || selectedQuality === 'hls') {
      // Use HLS for adaptive bitrate
      return videoData.hls_playlist_url;
    }
    
    // Find specific quality
    const quality = videoData.qualities?.find(q => q.quality === selectedQuality);
    return quality?.cdn_url || videoData.qualities?.[0]?.cdn_url;
  }, [videoData, selectedQuality]);
  
  // Record video view
  const recordView = useCallback(async () => {
    if (viewRecordedRef.current || !onViewRecord) return;
    
    viewRecordedRef.current = true;
    
    try {
      await fetch(`/api/videos/${videoId}/view`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: localStorage.getItem('sessionId') || `anon_${Date.now()}`,
          quality: selectedQuality
        })
      });
      
      if (onViewRecord) {
        onViewRecord(videoId);
      }
    } catch (err) {
      console.error('Failed to record view:', err);
    }
  }, [videoId, selectedQuality, onViewRecord]);
  
  // Video event handlers
  const handlePlay = () => {
    if (!hasStartedPlaying) {
      setHasStartedPlaying(true);
      recordView();
    }
  };
  
  const handleTimeUpdate = () => {
    if (videoRef.current) {
      const current = videoRef.current.currentTime;
      setCurrentTime(current);
      
      // Record progress periodically
      if (Math.floor(current) % 30 === 0) { // Every 30 seconds
        recordProgress(current);
      }
    }
  };
  
  const handleLoadedMetadata = () => {
    if (videoRef.current) {
      setDuration(videoRef.current.duration);
    }
  };
  
  const recordProgress = async (currentTime) => {
    if (!duration || duration === 0) return;
    
    const completionPercentage = (currentTime / duration) * 100;
    
    try {
      await fetch(`/api/videos/${videoId}/view`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: localStorage.getItem('sessionId') || `anon_${Date.now()}`,
          watch_duration: Math.floor(currentTime),
          completion_percentage: completionPercentage,
          last_position: Math.floor(currentTime),
          quality: selectedQuality
        })
      });
    } catch (err) {
      console.error('Failed to record progress:', err);
    }
  };
  
  // Quality selector component
  const QualitySelector = () => {
    if (!videoData?.qualities?.length) return null;
    
    return (
      <div className="absolute top-2 right-2 bg-black bg-opacity-70 rounded p-2">
        <select
          value={selectedQuality}
          onChange={(e) => setSelectedQuality(e.target.value)}
          className="bg-transparent text-white text-sm border-none outline-none"
        >
          <option value="auto">Auto</option>
          {videoData.qualities.map(quality => (
            <option key={quality.quality} value={quality.quality}>
              {quality.quality} ({quality.bitrate}kbps)
            </option>
          ))}
        </select>
      </div>
    );
  };
  
  // Loading skeleton
  const LoadingSkeleton = () => (
    <div className={`bg-gray-300 animate-pulse rounded-lg ${className}`}>
      <div className="aspect-video w-full bg-gray-400 rounded-lg flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-gray-500 border-t-white rounded-full animate-spin"></div>
      </div>
    </div>
  );
  
  // Error display
  const ErrorDisplay = () => (
    <div className={`bg-red-100 border border-red-400 rounded-lg p-4 ${className}`}>
      <div className="flex items-center justify-center text-red-600">
        <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>Error loading video: {error}</span>
      </div>
      <button 
        onClick={loadVideoData}
        className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
      >
        Retry
      </button>
    </div>
  );
  
  if (error) {
    return <ErrorDisplay />;
  }
  
  if (isLoading || !videoData) {
    return <LoadingSkeleton />;
  }
  
  const videoSource = getVideoSource();
  
  return (
    <div ref={containerRef} className={`relative ${className}`}>
      <div className="relative group">
        <video
          ref={videoRef}
          className="w-full h-auto rounded-lg"
          controls={controls}
          autoPlay={autoplay}
          preload={preload}
          poster={poster || videoData.thumbnail_url}
          onPlay={handlePlay}
          onTimeUpdate={handleTimeUpdate}
          onLoadedMetadata={handleLoadedMetadata}
          crossOrigin="anonymous"
        >
          {selectedQuality === 'auto' || selectedQuality === 'hls' ? (
            // HLS source for adaptive bitrate
            <source src={videoSource} type="application/x-mpegURL" />
          ) : (
            // Progressive download for specific quality
            <source src={videoSource} type="video/mp4" />
          )}
          
          {/* Fallback sources */}
          {videoData.qualities?.map(quality => (
            <source 
              key={quality.quality}
              src={quality.cdn_url} 
              type="video/mp4"
              data-quality={quality.quality}
            />
          ))}
          
          <p className="text-gray-500">
            Your browser does not support the video tag.
          </p>
        </video>
        
        {/* Quality selector overlay */}
        <QualitySelector />
        
        {/* Video metadata overlay */}
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black to-transparent p-4 opacity-0 group-hover:opacity-100 transition-opacity">
          <h3 className="text-white font-semibold text-lg">{videoData.title}</h3>
          {videoData.description && (
            <p className="text-gray-300 text-sm mt-1 line-clamp-2">{videoData.description}</p>
          )}
          <div className="flex items-center justify-between mt-2 text-xs text-gray-400">
            <span>{Math.floor(duration / 60)}:{String(Math.floor(duration % 60)).padStart(2, '0')}</span>
            <span>{videoData.view_count} views</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VideoPlayer;