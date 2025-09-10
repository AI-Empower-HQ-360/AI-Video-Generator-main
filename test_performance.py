"""
Test file for performance optimization features
Run with: python -m pytest test_performance.py -v
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from backend.services.cache_service import CacheService
from backend.services.performance_monitor import MetricsCollector, Alert
from backend.models.database import Video, VideoQuality


class TestCacheService:
    """Test cache service functionality"""
    
    def test_memory_cache_fallback(self):
        """Test that cache service works without Redis"""
        cache = CacheService()
        
        # Test set and get
        assert cache.set('test_key', 'test_value')
        assert cache.get('test_key') == 'test_value'
        
        # Test delete
        assert cache.delete('test_key')
        assert cache.get('test_key') is None
        
        # Test exists
        cache.set('exists_key', 'value')
        assert cache.exists('exists_key')
        assert not cache.exists('nonexistent_key')
    
    def test_cache_decorators(self):
        """Test cache decorators"""
        from backend.services.cache_service import cached
        
        call_count = 0
        
        @cached(timeout=60, key_prefix='test')
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call should execute function
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count == 1
        
        # Second call should use cache
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # Should not increment


class TestPerformanceMonitor:
    """Test performance monitoring functionality"""
    
    def test_metrics_collector(self):
        """Test metrics collection"""
        collector = MetricsCollector()
        
        # Record some metrics
        collector.record_metric('test_metric', 10.5)
        collector.record_metric('test_metric', 15.2)
        collector.record_metric('test_metric', 8.7)
        
        # Get metrics
        metrics = collector.get_metrics('test_metric')
        assert len(metrics) == 3
        assert metrics[0].value == 10.5
        
        # Get summary
        summary = collector.get_metric_summary('test_metric')
        assert summary['count'] == 3
        assert summary['avg'] == pytest.approx(11.47, rel=1e-2)
        assert summary['min'] == 8.7
        assert summary['max'] == 15.2
    
    def test_alert_system(self):
        """Test alert configuration and triggering"""
        collector = MetricsCollector()
        
        # Add alert
        alert = Alert(
            name='high_cpu',
            metric='cpu_usage',
            threshold=80.0,
            condition='greater',
            duration=0  # Immediate alert for testing
        )
        collector.add_alert(alert)
        
        # Should not trigger alert
        collector.record_metric('cpu_usage', 75.0)
        assert not collector.alert_states['high_cpu']['triggered']
        
        # Should trigger alert
        collector.record_metric('cpu_usage', 85.0)
        assert collector.alert_states['high_cpu']['triggered']


class TestVideoModels:
    """Test video-related database models"""
    
    def test_video_model_creation(self):
        """Test video model attributes"""
        video = Video(
            title="Test Video",
            description="Test Description",
            filename="test.mp4",
            original_filename="original_test.mp4",
            category="meditation",
            guru_type="spiritual"
        )
        
        assert video.title == "Test Video"
        assert video.category == "meditation"
        assert video.processing_status == "pending"
        assert video.view_count == 0
        
        # Test to_dict method
        video_dict = video.to_dict()
        assert video_dict['title'] == "Test Video"
        assert video_dict['category'] == "meditation"
    
    def test_video_quality_model(self):
        """Test video quality model"""
        quality = VideoQuality(
            video_id="test-video-id",
            quality="720p",
            bitrate=2500,
            width=1280,
            height=720,
            file_path="/path/to/video.mp4"
        )
        
        assert quality.quality == "720p"
        assert quality.bitrate == 2500
        
        quality_dict = quality.to_dict()
        assert quality_dict['quality'] == "720p"
        assert quality_dict['width'] == 1280


class TestVideoService:
    """Test video service functionality"""
    
    @patch('subprocess.run')
    def test_video_metadata_extraction(self, mock_subprocess):
        """Test video metadata extraction"""
        from backend.services.video_service import VideoService
        
        # Mock ffprobe output
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = '''
        {
            "streams": [
                {
                    "codec_type": "video",
                    "width": 1920,
                    "height": 1080,
                    "bit_rate": "5000000"
                }
            ],
            "format": {
                "duration": "120.5"
            }
        }
        '''
        
        service = VideoService()
        metadata = service._get_video_metadata("/fake/path/video.mp4")
        
        assert metadata['width'] == 1920
        assert metadata['height'] == 1080
        assert metadata['duration'] == 120
    
    def test_cdn_url_generation(self):
        """Test CDN URL generation"""
        from backend.services.video_service import VideoService
        
        service = VideoService()
        service.video_cdn_domain = "https://cdn.example.com"
        service.storage_path = "/uploads"
        
        url = service._get_cdn_url("/uploads/videos/test.mp4")
        assert url == "https://cdn.example.com/videos/test.mp4"
    
    def test_quality_presets(self):
        """Test video quality presets"""
        from backend.services.video_service import VideoService
        
        assert '720p' in VideoService.QUALITY_PRESETS
        assert VideoService.QUALITY_PRESETS['720p']['width'] == 1280
        assert VideoService.QUALITY_PRESETS['720p']['height'] == 720


class TestAPIEndpoints:
    """Test API endpoint functionality (mock tests)"""
    
    def test_video_upload_validation(self):
        """Test video upload validation logic"""
        from backend.services.video_service import VideoService
        
        service = VideoService()
        
        # Test supported formats
        assert '.mp4' in service.SUPPORTED_FORMATS
        assert '.avi' in service.SUPPORTED_FORMATS
        assert '.txt' not in service.SUPPORTED_FORMATS
    
    @patch('backend.services.cache_service.cache.get')
    @patch('backend.services.cache_service.cache.set')
    def test_cache_response_decorator(self, mock_set, mock_get):
        """Test cache response decorator"""
        from backend.services.cache_service import cache_response
        from flask import Flask, jsonify
        
        app = Flask(__name__)
        
        # Mock cache miss
        mock_get.return_value = None
        
        @cache_response(timeout=300, key_prefix='test')
        def test_endpoint():
            return jsonify({'data': 'test'})
        
        with app.test_request_context('/test'):
            response = test_endpoint()
            
            # Should have cache miss header
            assert response.headers.get('X-Cache') == 'MISS'


def test_integration_imports():
    """Test that all modules can be imported without errors"""
    try:
        from backend.services.cache_service import CacheService, cache_response, cached
        from backend.services.video_service import VideoService
        from backend.services.performance_monitor import PerformanceMonitor
        from backend.models.database import Video, VideoQuality, VideoView
        
        # Test basic instantiation
        cache_service = CacheService()
        video_service = VideoService()
        perf_monitor = PerformanceMonitor()
        
        assert cache_service is not None
        assert video_service is not None
        assert perf_monitor is not None
        
    except ImportError as e:
        pytest.fail(f"Import error: {e}")


if __name__ == "__main__":
    # Run basic tests
    print("Running performance optimization tests...")
    
    # Test cache service
    print("✓ Testing cache service...")
    test_cache = TestCacheService()
    test_cache.test_memory_cache_fallback()
    
    # Test performance monitor
    print("✓ Testing performance monitor...")
    test_perf = TestPerformanceMonitor()
    test_perf.test_metrics_collector()
    test_perf.test_alert_system()
    
    # Test video models
    print("✓ Testing video models...")
    test_video = TestVideoModels()
    test_video.test_video_model_creation()
    test_video.test_video_quality_model()
    
    # Test video service
    print("✓ Testing video service...")
    test_video_service = TestVideoService()
    test_video_service.test_quality_presets()
    test_video_service.test_cdn_url_generation()
    
    # Test imports
    print("✓ Testing imports...")
    test_integration_imports()
    
    print("\n🎉 All tests passed! Performance optimization features are working correctly.")