import React, { useState, useEffect, useRef } from 'react';
import VideoPlayer from './VideoPlayer';
import { useIntersectionObserver, useCache } from '../hooks/useIntersectionObserver';

const VideoGallery = ({ 
  category = null, 
  guruType = null, 
  className = '',
  showUploadButton = false,
  onVideoUpload = null 
}) => {
  const [videos, setVideos] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState(category);
  const [selectedGuru, setSelectedGuru] = useState(guruType);
  
  const loadMoreRef = useRef(null);
  const isLoadMoreInView = useIntersectionObserver(loadMoreRef);
  
  // Cache for video data
  const cacheKey = `videos_${selectedCategory}_${selectedGuru}_${searchQuery}`;
  const { data: cachedVideos, set: setCachedVideos, isStale } = useCache(cacheKey, 300000); // 5 minutes

  useEffect(() => {
    if (cachedVideos && !isStale) {
      setVideos(cachedVideos);
    } else {
      loadVideos(true);
    }
  }, [selectedCategory, selectedGuru, searchQuery]);

  useEffect(() => {
    if (isLoadMoreInView && hasMore && !isLoading) {
      loadVideos(false);
    }
  }, [isLoadMoreInView, hasMore, isLoading]);

  const loadVideos = async (reset = false) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const currentPage = reset ? 1 : page;
      let url = '/api/videos';
      const params = new URLSearchParams({
        page: currentPage,
        per_page: 12
      });

      if (searchQuery) {
        url = '/api/videos/search';
        params.append('q', searchQuery);
      } else if (selectedCategory) {
        url = `/api/videos/category/${selectedCategory}`;
      }

      if (selectedGuru) {
        params.append('guru_type', selectedGuru);
      }

      const response = await fetch(`${url}?${params}`);
      if (!response.ok) {
        throw new Error('Failed to load videos');
      }

      const data = await response.json();
      const newVideos = data.videos || [];

      if (reset) {
        setVideos(newVideos);
        setCachedVideos(newVideos);
        setPage(2);
      } else {
        const updatedVideos = [...videos, ...newVideos];
        setVideos(updatedVideos);
        setCachedVideos(updatedVideos);
        setPage(currentPage + 1);
      }

      setHasMore(newVideos.length === 12); // Assuming 12 per page
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = (query) => {
    setSearchQuery(query);
    setPage(1);
    setHasMore(true);
  };

  const handleCategoryChange = (category) => {
    setSelectedCategory(category);
    setPage(1);
    setHasMore(true);
    setSearchQuery('');
  };

  const handleGuruChange = (guru) => {
    setSelectedGuru(guru);
    setPage(1);
    setHasMore(true);
  };

  const categories = [
    'meditation', 'teaching', 'music', 'yoga', 'spiritual', 'general'
  ];

  const gurus = [
    'karma', 'bhakti', 'meditation', 'yoga', 'spiritual', 'sloka'
  ];

  // Video thumbnail component with lazy loading
  const VideoThumbnail = ({ video, onClick }) => {
    const [thumbnailLoaded, setThumbnailLoaded] = useState(false);
    const [thumbnailError, setThumbnailError] = useState(false);
    const thumbnailRef = useRef(null);
    const isInView = useIntersectionObserver(thumbnailRef);

    return (
      <div 
        ref={thumbnailRef}
        className="bg-gray-200 rounded-lg overflow-hidden shadow-md hover:shadow-lg transition-shadow cursor-pointer"
        onClick={onClick}
      >
        <div className="aspect-video relative">
          {isInView && (
            <>
              <img
                src={video.thumbnail_url || '/placeholder-video.jpg'}
                alt={video.title}
                className={`w-full h-full object-cover transition-opacity duration-300 ${
                  thumbnailLoaded ? 'opacity-100' : 'opacity-0'
                }`}
                onLoad={() => setThumbnailLoaded(true)}
                onError={() => setThumbnailError(true)}
              />
              {!thumbnailLoaded && !thumbnailError && (
                <div className="absolute inset-0 bg-gray-300 animate-pulse flex items-center justify-center">
                  <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                          d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              )}
            </>
          )}
          
          {/* Duration overlay */}
          {video.duration && (
            <div className="absolute bottom-2 right-2 bg-black bg-opacity-70 text-white text-xs px-2 py-1 rounded">
              {Math.floor(video.duration / 60)}:{String(video.duration % 60).padStart(2, '0')}
            </div>
          )}
          
          {/* Processing status indicator */}
          {video.processing_status === 'processing' && (
            <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
              <div className="text-white text-sm">Processing...</div>
            </div>
          )}
        </div>
        
        <div className="p-4">
          <h3 className="font-semibold text-gray-900 mb-2 line-clamp-2">{video.title}</h3>
          {video.description && (
            <p className="text-gray-600 text-sm line-clamp-2 mb-2">{video.description}</p>
          )}
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>{video.view_count} views</span>
            <span>{new Date(video.created_at).toLocaleDateString()}</span>
          </div>
          {video.category && (
            <div className="mt-2">
              <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
                {video.category}
              </span>
            </div>
          )}
        </div>
      </div>
    );
  };

  // Loading skeleton
  const LoadingSkeleton = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {[...Array(8)].map((_, i) => (
        <div key={i} className="bg-gray-200 rounded-lg overflow-hidden animate-pulse">
          <div className="aspect-video bg-gray-300"></div>
          <div className="p-4">
            <div className="h-4 bg-gray-300 rounded mb-2"></div>
            <div className="h-3 bg-gray-300 rounded mb-2"></div>
            <div className="h-3 bg-gray-300 rounded w-2/3"></div>
          </div>
        </div>
      ))}
    </div>
  );

  return (
    <div className={`max-w-7xl mx-auto p-6 ${className}`}>
      {/* Header */}
      <div className="mb-8">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4 md:mb-0">
            Spiritual Videos
          </h2>
          
          {showUploadButton && onVideoUpload && (
            <button
              onClick={onVideoUpload}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Upload Video
            </button>
          )}
        </div>

        {/* Search and Filters */}
        <div className="flex flex-col lg:flex-row gap-4">
          {/* Search */}
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search videos..."
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Category Filter */}
          <select
            value={selectedCategory || ''}
            onChange={(e) => handleCategoryChange(e.target.value || null)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Categories</option>
            {categories.map(cat => (
              <option key={cat} value={cat}>
                {cat.charAt(0).toUpperCase() + cat.slice(1)}
              </option>
            ))}
          </select>

          {/* Guru Filter */}
          <select
            value={selectedGuru || ''}
            onChange={(e) => handleGuruChange(e.target.value || null)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Gurus</option>
            {gurus.map(guru => (
              <option key={guru} value={guru}>
                {guru.charAt(0).toUpperCase() + guru.slice(1)}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
          <p>Error loading videos: {error}</p>
          <button 
            onClick={() => loadVideos(true)}
            className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
          >
            Retry
          </button>
        </div>
      )}

      {/* Videos Grid */}
      {videos.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {videos.map((video) => (
            <VideoThumbnail
              key={video.id}
              video={video}
              onClick={() => {
                // Handle video click - could open modal or navigate
                console.log('Video clicked:', video.id);
              }}
            />
          ))}
        </div>
      ) : !isLoading ? (
        <div className="text-center py-12">
          <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                  d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
          <p className="text-gray-500 text-lg">No videos found</p>
          <p className="text-gray-400">Try adjusting your search or filter criteria</p>
        </div>
      ) : null}

      {/* Loading Skeleton */}
      {isLoading && videos.length === 0 && <LoadingSkeleton />}

      {/* Load More Trigger */}
      {hasMore && videos.length > 0 && (
        <div ref={loadMoreRef} className="mt-8 flex justify-center">
          {isLoading ? (
            <div className="flex items-center space-x-2 text-gray-600">
              <div className="w-5 h-5 border-2 border-gray-600 border-t-transparent rounded-full animate-spin"></div>
              <span>Loading more videos...</span>
            </div>
          ) : (
            <button
              onClick={() => loadVideos(false)}
              className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
            >
              Load More Videos
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default VideoGallery;