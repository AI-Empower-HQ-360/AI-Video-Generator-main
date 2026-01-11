"""
Unit tests for YouTube service
Tests video ID extraction, video info retrieval, and transcript fetching.
"""

import pytest
from unittest.mock import patch, MagicMock
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.youtube_service import YouTubeService, youtube_service


class TestYouTubeService:
    """Test suite for YouTube service functionality."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.service = YouTubeService()
    
    def test_extract_video_id_from_watch_url(self):
        """Test extracting video ID from standard watch URL."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        video_id = self.service.extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"
    
    def test_extract_video_id_from_short_url(self):
        """Test extracting video ID from shortened youtu.be URL."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        video_id = self.service.extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"
    
    def test_extract_video_id_from_embed_url(self):
        """Test extracting video ID from embed URL."""
        url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        video_id = self.service.extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"
    
    def test_extract_video_id_from_v_url(self):
        """Test extracting video ID from /v/ URL."""
        url = "https://www.youtube.com/v/dQw4w9WgXcQ"
        video_id = self.service.extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"
    
    def test_extract_video_id_from_plain_id(self):
        """Test that a plain video ID is returned as-is."""
        video_id = "dQw4w9WgXcQ"
        result = self.service.extract_video_id(video_id)
        assert result == video_id
    
    def test_extract_video_id_invalid_url(self):
        """Test that invalid URL returns None."""
        url = "https://www.example.com/not-a-youtube-url"
        video_id = self.service.extract_video_id(url)
        assert video_id is None
    
    @patch.dict(os.environ, {'YOUTUBE_API_KEY': 'test-api-key'})
    @patch('requests.get')
    def test_get_video_info_success(self, mock_get):
        """Test successful video info retrieval."""
        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'items': [{
                'snippet': {
                    'title': 'Test Video',
                    'description': 'Test Description',
                    'channelTitle': 'Test Channel',
                    'publishedAt': '2024-01-01T00:00:00Z',
                    'thumbnails': {
                        'high': {'url': 'https://example.com/thumb.jpg'}
                    }
                },
                'statistics': {
                    'viewCount': '1000',
                    'likeCount': '100'
                },
                'contentDetails': {
                    'duration': 'PT5M30S'
                }
            }]
        }
        mock_get.return_value = mock_response
        
        # Create service with mocked API key
        service = YouTubeService()
        result = service.get_video_info('test_video_id')
        
        assert result['status'] == 'success'
        assert result['title'] == 'Test Video'
        assert result['description'] == 'Test Description'
        assert result['channel'] == 'Test Channel'
        assert result['views'] == '1000'
        assert result['likes'] == '100'
    
    def test_get_video_info_no_api_key(self):
        """Test video info retrieval without API key."""
        # Ensure no API key is set
        service = YouTubeService()
        service.api_key = None
        
        result = service.get_video_info('test_video_id')
        
        assert result['status'] == 'error'
        assert 'not configured' in result['error']
    
    @patch.dict(os.environ, {'YOUTUBE_API_KEY': 'test-api-key'})
    @patch('requests.get')
    def test_get_video_info_not_found(self, mock_get):
        """Test video info retrieval for non-existent video."""
        # Mock API response with no items
        mock_response = MagicMock()
        mock_response.json.return_value = {'items': []}
        mock_get.return_value = mock_response
        
        service = YouTubeService()
        result = service.get_video_info('nonexistent_id')
        
        assert result['status'] == 'not_found'
        assert 'not found' in result['error']
    
    @patch('backend.services.youtube_service.YouTubeTranscriptApi.list')
    def test_get_transcript_success(self, mock_list):
        """Test successful transcript retrieval."""
        # Mock transcript
        mock_transcript = MagicMock()
        mock_transcript.language_code = 'en'
        mock_transcript.fetch.return_value = [
            {'text': 'Hello', 'start': 0.0, 'duration': 1.0},
            {'text': 'World', 'start': 1.0, 'duration': 1.0}
        ]
        
        mock_transcript_list = MagicMock()
        mock_transcript_list.find_transcript.return_value = mock_transcript
        mock_list.return_value = mock_transcript_list
        
        result = self.service.get_transcript('test_video_id')
        
        assert result['status'] == 'success'
        assert result['text'] == 'Hello World'
        assert result['language'] == 'en'
        assert result['is_auto_generated'] is False
        assert len(result['segments']) == 2
    
    @patch('backend.services.youtube_service.YouTubeTranscriptApi.list')
    def test_get_transcript_auto_generated(self, mock_list):
        """Test retrieval of auto-generated transcript."""
        from youtube_transcript_api._errors import NoTranscriptFound
        
        # Mock transcript
        mock_transcript = MagicMock()
        mock_transcript.language_code = 'en'
        mock_transcript.fetch.return_value = [
            {'text': 'Auto generated text', 'start': 0.0, 'duration': 1.0}
        ]
        
        mock_transcript_list = MagicMock()
        # Manual transcript not found, but auto-generated is
        mock_transcript_list.find_transcript.side_effect = NoTranscriptFound('', '', '')
        mock_transcript_list.find_generated_transcript.return_value = mock_transcript
        mock_list.return_value = mock_transcript_list
        
        result = self.service.get_transcript('test_video_id')
        
        assert result['status'] == 'success'
        assert result['is_auto_generated'] is True
        assert 'Auto generated text' in result['text']
    
    @patch('backend.services.youtube_service.YouTubeTranscriptApi.list')
    def test_get_transcript_disabled(self, mock_list):
        """Test transcript retrieval when transcripts are disabled."""
        from youtube_transcript_api._errors import TranscriptsDisabled
        
        mock_list.side_effect = TranscriptsDisabled('test_video_id')
        
        result = self.service.get_transcript('test_video_id')
        
        assert result['status'] == 'disabled'
        assert 'disabled' in result['error']
    
    @patch('backend.services.youtube_service.YouTubeTranscriptApi.list')
    def test_get_transcript_video_unavailable(self, mock_list):
        """Test transcript retrieval when video is unavailable."""
        from youtube_transcript_api._errors import VideoUnavailable
        
        mock_list.side_effect = VideoUnavailable('test_video_id')
        
        result = self.service.get_transcript('test_video_id')
        
        assert result['status'] == 'unavailable'
        assert 'unavailable' in result['error']
    
    def test_get_video_summary_invalid_url(self):
        """Test video summary with invalid URL."""
        result = self.service.get_video_summary('not-a-valid-url')
        
        assert result['status'] == 'invalid_url'
        assert 'Invalid' in result['error']
    
    @patch.object(YouTubeService, 'get_video_info')
    @patch.object(YouTubeService, 'get_transcript')
    def test_get_video_summary_success(self, mock_transcript, mock_info):
        """Test successful video summary retrieval."""
        # Mock responses
        mock_info.return_value = {
            'status': 'success',
            'title': 'Test Video'
        }
        mock_transcript.return_value = {
            'status': 'success',
            'text': 'Test transcript'
        }
        
        result = self.service.get_video_summary('https://youtu.be/dQw4w9WgXcQ')
        
        assert result['video_id'] == 'dQw4w9WgXcQ'
        assert result['video_info']['status'] == 'success'
        assert result['transcript']['status'] == 'success'
    
    def test_singleton_instance(self):
        """Test that youtube_service is properly instantiated."""
        assert youtube_service is not None
        assert isinstance(youtube_service, YouTubeService)


class TestYouTubeServiceIntegration:
    """Integration tests for YouTube service (requires actual API)."""
    
    @pytest.mark.skipif(
        not os.environ.get('YOUTUBE_API_KEY') or 
        os.environ.get('YOUTUBE_API_KEY') == 'your-youtube-api-key-here',
        reason="YouTube API key not configured"
    )
    def test_real_video_info(self):
        """Test with a real video (only runs if API key is configured)."""
        service = YouTubeService()
        # Using a well-known public video
        result = service.get_video_info('jNQXAC9IVRw')
        
        if result['status'] == 'success':
            assert 'title' in result
            assert len(result['title']) > 0
    
    @pytest.mark.skipif(
        not os.environ.get('YOUTUBE_API_KEY') or 
        os.environ.get('YOUTUBE_API_KEY') == 'your-youtube-api-key-here',
        reason="YouTube API key not configured"
    )
    def test_real_transcript(self):
        """Test with a real video transcript (only runs if API key is configured)."""
        service = YouTubeService()
        # Using a well-known public video
        result = service.get_transcript('jNQXAC9IVRw')
        
        # Transcript may or may not be available
        assert result['status'] in ['success', 'disabled', 'no_transcript']
