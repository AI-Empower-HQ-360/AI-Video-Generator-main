import React, { useState, useEffect } from 'react';
import { 
  MagnifyingGlassIcon, 
  FunnelIcon, 
  PlayIcon,
  ShareIcon,
  TrashIcon,
  PencilIcon,
  HeartIcon,
  EyeIcon
} from '@heroicons/react/24/outline';
import { HeartIcon as HeartSolidIcon } from '@heroicons/react/24/solid';

const VideoGallery = () => {
  const [videos, setVideos] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [sortBy, setSortBy] = useState('newest');
  const [showFilters, setShowFilters] = useState(false);
  const [favoriteVideos, setFavoriteVideos] = useState(new Set());

  // Mock video data
  useEffect(() => {
    const mockVideos = [
      {
        id: 'video-1',
        title: 'Morning Meditation Guide',
        description: 'A peaceful 10-minute morning meditation to start your day with clarity and intention.',
        thumbnail: '🧘‍♀️',
        duration: '10:23',
        category: 'spiritual',
        tags: ['meditation', 'morning', 'mindfulness'],
        createdAt: new Date('2024-01-15'),
        views: 1245,
        likes: 89,
        isPublic: true,
        author: 'Spiritual Guide'
      },
      {
        id: 'video-2',
        title: 'Sanskrit Sloka Recitation',
        description: 'Beautiful recitation of ancient Sanskrit slokas with meaning and pronunciation guide.',
        thumbnail: '🕉️',
        duration: '8:45',
        category: 'educational',
        tags: ['sanskrit', 'slokas', 'pronunciation'],
        createdAt: new Date('2024-01-12'),
        views: 892,
        likes: 67,
        isPublic: true,
        author: 'Sloka Guru'
      },
      {
        id: 'video-3',
        title: 'Heart Chakra Healing',
        description: 'Guided visualization and energy work for opening and healing the heart chakra.',
        thumbnail: '💚',
        duration: '15:30',
        category: 'spiritual',
        tags: ['chakra', 'healing', 'visualization'],
        createdAt: new Date('2024-01-10'),
        views: 2103,
        likes: 156,
        isPublic: true,
        author: 'Energy Healer'
      },
      {
        id: 'video-4',
        title: 'Yoga Flow for Beginners',
        description: 'Gentle yoga flow perfect for beginners, focusing on breath and basic poses.',
        thumbnail: '🧘‍♀️',
        duration: '20:15',
        category: 'wellness',
        tags: ['yoga', 'beginners', 'flow'],
        createdAt: new Date('2024-01-08'),
        views: 3456,
        likes: 234,
        isPublic: true,
        author: 'Yoga Instructor'
      },
      {
        id: 'video-5',
        title: 'Bhakti Devotional Songs',
        description: 'Collection of beautiful devotional songs to inspire love and devotion.',
        thumbnail: '💝',
        duration: '25:12',
        category: 'spiritual',
        tags: ['bhakti', 'devotional', 'songs'],
        createdAt: new Date('2024-01-05'),
        views: 1876,
        likes: 123,
        isPublic: true,
        author: 'Bhakti Guru'
      },
      {
        id: 'video-6',
        title: 'Karma and Dharma Explained',
        description: 'Deep dive into the concepts of karma and dharma with practical examples.',
        thumbnail: '⚖️',
        duration: '18:30',
        category: 'educational',
        tags: ['karma', 'dharma', 'philosophy'],
        createdAt: new Date('2024-01-03'),
        views: 2567,
        likes: 189,
        isPublic: true,
        author: 'Philosophy Teacher'
      }
    ];
    setVideos(mockVideos);
  }, []);

  const categories = [
    { id: 'all', name: 'All Videos', icon: '📹' },
    { id: 'spiritual', name: 'Spiritual', icon: '🕉️' },
    { id: 'educational', name: 'Educational', icon: '📚' },
    { id: 'wellness', name: 'Wellness', icon: '🌱' },
    { id: 'meditation', name: 'Meditation', icon: '🧘' }
  ];

  const sortOptions = [
    { id: 'newest', name: 'Newest First' },
    { id: 'oldest', name: 'Oldest First' },
    { id: 'mostViewed', name: 'Most Viewed' },
    { id: 'mostLiked', name: 'Most Liked' },
    { id: 'duration', name: 'Duration' }
  ];

  const filteredAndSortedVideos = videos
    .filter(video => {
      const matchesSearch = video.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           video.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           video.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
      const matchesCategory = selectedCategory === 'all' || video.category === selectedCategory;
      return matchesSearch && matchesCategory;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'newest':
          return new Date(b.createdAt) - new Date(a.createdAt);
        case 'oldest':
          return new Date(a.createdAt) - new Date(b.createdAt);
        case 'mostViewed':
          return b.views - a.views;
        case 'mostLiked':
          return b.likes - a.likes;
        case 'duration':
          return a.duration.localeCompare(b.duration);
        default:
          return 0;
      }
    });

  const toggleFavorite = (videoId) => {
    setFavoriteVideos(prev => {
      const newFavorites = new Set(prev);
      if (newFavorites.has(videoId)) {
        newFavorites.delete(videoId);
      } else {
        newFavorites.add(videoId);
      }
      return newFavorites;
    });
  };

  const formatDate = (date) => {
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    }).format(date);
  };

  const formatViews = (views) => {
    if (views >= 1000000) {
      return `${(views / 1000000).toFixed(1)}M`;
    } else if (views >= 1000) {
      return `${(views / 1000).toFixed(1)}K`;
    }
    return views.toString();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-white mb-4">
          📹 Video Gallery
        </h1>
        <p className="text-xl text-white/80">
          Discover and manage your spiritual video collection
        </p>
      </div>

      {/* Search and Filters */}
      <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6">
        <div className="flex flex-col lg:flex-row gap-4 items-center justify-between">
          {/* Search Bar */}
          <div className="relative flex-1 max-w-md">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search videos, tags, or descriptions..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-3 bg-white/20 border border-white/30 rounded-xl text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
          </div>

          {/* Controls */}
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                showFilters ? 'bg-blue-600 text-white' : 'bg-white/20 text-white hover:bg-white/30'
              }`}
            >
              <FunnelIcon className="h-4 w-4" />
              <span>Filters</span>
            </button>

            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-4 py-2 bg-white/20 border border-white/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-400"
            >
              {sortOptions.map(option => (
                <option key={option.id} value={option.id} className="bg-gray-800">
                  {option.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Category Filters */}
        {showFilters && (
          <div className="mt-6 pt-6 border-t border-white/20">
            <div className="flex flex-wrap gap-3">
              {categories.map(category => (
                <button
                  key={category.id}
                  onClick={() => setSelectedCategory(category.id)}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-full transition-colors ${
                    selectedCategory === category.id
                      ? 'bg-blue-600 text-white'
                      : 'bg-white/20 text-white hover:bg-white/30'
                  }`}
                >
                  <span>{category.icon}</span>
                  <span>{category.name}</span>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Results Count */}
      <div className="text-white/70">
        {filteredAndSortedVideos.length} video{filteredAndSortedVideos.length !== 1 ? 's' : ''} found
      </div>

      {/* Video Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {filteredAndSortedVideos.map(video => (
          <div
            key={video.id}
            className="bg-white/10 backdrop-blur-md rounded-2xl overflow-hidden border border-white/20 hover:border-white/40 transition-all duration-300 hover:scale-105"
          >
            {/* Thumbnail */}
            <div className="relative h-48 bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
              <span className="text-6xl">{video.thumbnail}</span>
              
              {/* Play Overlay */}
              <div className="absolute inset-0 bg-black/50 opacity-0 hover:opacity-100 transition-opacity flex items-center justify-center">
                <button className="w-16 h-16 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center hover:bg-white/30 transition-colors">
                  <PlayIcon className="h-8 w-8 text-white ml-1" />
                </button>
              </div>

              {/* Duration */}
              <div className="absolute bottom-2 right-2 bg-black/70 text-white text-xs px-2 py-1 rounded">
                {video.duration}
              </div>

              {/* Favorite */}
              <button
                onClick={() => toggleFavorite(video.id)}
                className="absolute top-2 right-2 p-1.5 bg-black/50 rounded-full hover:bg-black/70 transition-colors"
              >
                {favoriteVideos.has(video.id) ? (
                  <HeartSolidIcon className="h-5 w-5 text-red-500" />
                ) : (
                  <HeartIcon className="h-5 w-5 text-white" />
                )}
              </button>
            </div>

            {/* Content */}
            <div className="p-4">
              <h3 className="text-lg font-semibold text-white mb-2 line-clamp-2">
                {video.title}
              </h3>
              
              <p className="text-white/70 text-sm mb-3 line-clamp-2">
                {video.description}
              </p>

              <div className="text-xs text-white/50 mb-3">
                By {video.author} • {formatDate(video.createdAt)}
              </div>

              {/* Tags */}
              <div className="flex flex-wrap gap-1 mb-3">
                {video.tags.slice(0, 3).map(tag => (
                  <span
                    key={tag}
                    className="px-2 py-1 bg-white/20 text-white/80 text-xs rounded-full"
                  >
                    #{tag}
                  </span>
                ))}
              </div>

              {/* Stats */}
              <div className="flex items-center justify-between text-xs text-white/60 mb-3">
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-1">
                    <EyeIcon className="h-4 w-4" />
                    <span>{formatViews(video.views)}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <HeartIcon className="h-4 w-4" />
                    <span>{video.likes}</span>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center space-x-2">
                <button className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-lg text-sm font-medium transition-colors">
                  Watch
                </button>
                <button className="p-2 bg-white/20 hover:bg-white/30 text-white rounded-lg transition-colors">
                  <ShareIcon className="h-4 w-4" />
                </button>
                <button className="p-2 bg-white/20 hover:bg-white/30 text-white rounded-lg transition-colors">
                  <PencilIcon className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {filteredAndSortedVideos.length === 0 && (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">🎬</div>
          <h3 className="text-xl font-semibold text-white/80 mb-2">No videos found</h3>
          <p className="text-white/60">
            {searchTerm || selectedCategory !== 'all' 
              ? 'Try adjusting your search or filter settings'
              : 'Create your first video to get started'
            }
          </p>
        </div>
      )}
    </div>
  );
};

export default VideoGallery;