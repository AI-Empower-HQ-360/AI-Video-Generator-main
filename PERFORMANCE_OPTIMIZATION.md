# Performance Optimization Features

This document describes the performance optimization features implemented in the AI Heart Development Platform.

## Overview

The platform now includes comprehensive performance optimizations across six key areas:

1. **CDN Integration** for global video delivery
2. **Video Streaming** with adaptive bitrate
3. **Progressive Loading** and lazy loading
4. **Database Optimization** and indexing
5. **Caching Strategies** for API responses
6. **Performance Monitoring** and alerting

## Features

### 1. CDN Integration

The platform supports CDN integration for video delivery with configurable endpoints:

```bash
# Environment Variables
CDN_DOMAIN=https://cdn.empowerhub360.org
VIDEO_CDN_DOMAIN=https://video-cdn.empowerhub360.org
```

### 2. Video Streaming

#### Upload Videos
```bash
# API Endpoint
POST /api/videos/upload

# Example with curl
curl -X POST \
  -F "video=@path/to/video.mp4" \
  -F "title=Meditation Session" \
  -F "description=Guided meditation" \
  -F "category=meditation" \
  -F "guru_type=meditation" \
  http://localhost:5000/api/videos/upload
```

#### Get Video with Qualities
```bash
GET /api/videos/{video_id}
```

Response includes all available quality options and HLS playlist URLs.

#### React Video Player Usage
```jsx
import VideoPlayer from './components/VideoPlayer';

function App() {
  return (
    <VideoPlayer
      videoId="video-123"
      autoplay={false}
      controls={true}
      lazy={true}
      preload="metadata"
      onViewRecord={(videoId) => console.log('View recorded')}
    />
  );
}
```

### 3. Progressive Loading

#### Video Gallery with Lazy Loading
```jsx
import VideoGallery from './components/VideoGallery';

function VideoPage() {
  return (
    <VideoGallery
      category="meditation"
      guruType="spiritual"
      showUploadButton={true}
      onVideoUpload={() => setShowUploadModal(true)}
    />
  );
}
```

### 4. Database Optimization

#### Indexes Added
- User: `email`, `spiritual_level`, `created_at`, `last_active`
- SpiritualSession: Composite indexes on `(user_id, guru_type, created_at)`
- UserSession: Composite indexes on `(user_id, status, start_time)`
- Video: Composite indexes on `(category, is_public, created_at)`

#### Connection Pooling
```python
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 20,
    'pool_timeout': 20,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
    'max_overflow': 10
}
```

### 5. Caching

#### API Response Caching
```python
from services.cache_service import cache_response

@cache_response(timeout=3600, key_prefix='videos')
def get_videos():
    # This response will be cached for 1 hour
    return jsonify(videos)
```

#### Function Result Caching
```python
from services.cache_service import cached

@cached(timeout=1800, key_prefix='user_data')
def get_user_preferences(user_id):
    # Function result cached for 30 minutes
    return expensive_calculation(user_id)
```

#### Redis Configuration
```bash
# Environment Variables
REDIS_URL=redis://localhost:6379/0
CACHE_DEFAULT_TIMEOUT=300
```

### 6. Performance Monitoring

#### Performance Dashboard
```jsx
import PerformanceDashboard from './components/PerformanceDashboard';

function AdminPage() {
  return <PerformanceDashboard className="w-full" />;
}
```

#### Health Check
```bash
GET /api/performance/health
```

Returns system health status including database, cache, and resource usage.

#### Metrics API
```bash
# Get performance dashboard
GET /api/performance/dashboard

# Get specific metric history
GET /api/performance/metrics/cpu_usage?hours=24

# Get cache statistics
GET /api/performance/cache/stats

# Clear cache
POST /api/performance/cache/clear
```

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/dbname

# Redis Cache
REDIS_URL=redis://localhost:6379/0

# CDN
CDN_DOMAIN=https://cdn.example.com
VIDEO_CDN_DOMAIN=https://video-cdn.example.com

# Video Processing
VIDEO_STORAGE_PATH=uploads/videos

# Performance Monitoring
APM_SERVICE_NAME=ai-heart-platform
APM_SERVER_URL=http://apm-server:8200
```

### Docker Compose (Development)

```yaml
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: ai_heart_db
      POSTGRES_USER: ai_heart_user
      POSTGRES_PASSWORD: secure_password
    ports:
      - "5432:5432"
```

## Usage Examples

### Video Upload and Processing

1. Upload video through API
2. Video automatically processed into multiple qualities
3. HLS playlist generated for adaptive streaming
4. CDN URLs created for global delivery

### Performance Monitoring

1. Access performance dashboard at `/admin/performance`
2. Monitor real-time metrics
3. Set up alerts for critical thresholds
4. Track video analytics and user engagement

### Caching

1. API responses automatically cached based on decorators
2. Cache invalidation on data updates
3. Redis fallback to memory cache
4. Cache hit rate monitoring

## Best Practices

### Video Optimization
- Use H.264 codec for best compatibility
- Recommended resolutions: 720p, 1080p for source material
- Keep file sizes under 500MB for upload
- Use meaningful titles and descriptions for SEO

### Performance Monitoring
- Set up alerts for CPU > 80%, Memory > 85%, Disk > 90%
- Monitor cache hit rates (target > 70%)
- Track response times (target < 2 seconds)
- Regular database maintenance and index optimization

### Caching Strategy
- Cache static content for longer periods (1+ hours)
- Cache user-specific data for shorter periods (5-30 minutes)
- Implement cache warming for critical data
- Monitor cache memory usage and eviction policies

## Troubleshooting

### Common Issues

1. **Video Processing Failed**
   - Check ffmpeg installation
   - Verify file format compatibility
   - Check disk space for processing

2. **Cache Not Working**
   - Verify Redis connection
   - Check Redis memory limits
   - Validate cache key patterns

3. **Performance Issues**
   - Check database connection pool
   - Monitor slow query logs
   - Verify index usage
   - Check Redis memory usage

### Debug Commands

```bash
# Check Redis connection
redis-cli ping

# Monitor Redis commands
redis-cli monitor

# Check database indexes
# Connect to PostgreSQL and run:
\d+ table_name

# View cache statistics
curl http://localhost:5000/api/performance/cache/stats
```

For more detailed information, check the API documentation and service implementation files.