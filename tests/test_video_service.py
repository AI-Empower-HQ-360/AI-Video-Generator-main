"""
Test cases for Advanced Video Processing Service
===============================================

Comprehensive tests for video processing capabilities including:
- Video upload and metadata extraction
- Video editing operations (trim, merge)
- AI enhancement features
- Text-to-speech integration
- Subtitle generation and translation
- Analytics and batch processing
"""

import pytest
import asyncio
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.video_service import VideoProcessingService, VoiceOption, VideoQuality, VideoMetadata


class TestVideoProcessingService:
    """Test cases for VideoProcessingService"""
    
    @pytest.fixture
    def video_service(self):
        """Create a video service instance for testing"""
        return VideoProcessingService()
    
    @pytest.fixture
    def temp_video_file(self):
        """Create a temporary video file for testing"""
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
            # Write some dummy content
            f.write(b'fake video content')
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_video_upload_processing(self, video_service, temp_video_file):
        """Test video upload and processing"""
        
        # Mock video metadata extraction
        with patch.object(video_service, '_extract_video_metadata') as mock_extract:
            mock_metadata = VideoMetadata(
                filename="test.mp4",
                duration=30.0,
                resolution=(1920, 1080),
                fps=30.0,
                size_mb=10.5,
                format=".mp4",
                created_at=None
            )
            mock_extract.return_value = mock_metadata
            
            result = await video_service.process_video_upload(
                temp_video_file, 
                {"description": "Test video"}
            )
            
            assert result["success"] is True
            assert "video_id" in result
            assert result["metadata"]["filename"] == "test.mp4"
            assert result["metadata"]["duration"] == 30.0
    
    @pytest.mark.asyncio
    async def test_video_trimming(self, video_service):
        """Test video trimming functionality"""
        
        video_id = "test_video_123"
        
        # Mock finding video file
        with patch.object(video_service, '_find_video_file') as mock_find:
            mock_find.return_value = Path("fake_video.mp4")
            
            # Mock MoviePy functionality
            with patch('services.video_service.MOVIEPY_AVAILABLE', True):
                with patch('services.video_service.VideoFileClip') as mock_clip:
                    mock_video = MagicMock()
                    mock_video.duration = 60.0
                    mock_video.subclip.return_value = mock_video
                    mock_clip.return_value.__enter__.return_value = mock_video
                    
                    result = await video_service.trim_video(video_id, 10.0, 30.0)
                    
                    assert result["success"] is True
                    assert result["original_duration"] == 60.0
                    assert result["trimmed_duration"] == 20.0
                    assert "output_file" in result
    
    @pytest.mark.asyncio
    async def test_video_trimming_invalid_range(self, video_service):
        """Test video trimming with invalid time range"""
        
        video_id = "test_video_123"
        
        with patch.object(video_service, '_find_video_file') as mock_find:
            mock_find.return_value = Path("fake_video.mp4")
            
            with patch('services.video_service.MOVIEPY_AVAILABLE', True):
                with patch('services.video_service.VideoFileClip') as mock_clip:
                    mock_video = MagicMock()
                    mock_video.duration = 60.0
                    mock_clip.return_value.__enter__.return_value = mock_video
                    
                    # Test invalid range (start > end)
                    result = await video_service.trim_video(video_id, 30.0, 10.0)
                    
                    assert result["success"] is False
                    assert "Invalid time range" in result["error"]
    
    @pytest.mark.asyncio
    async def test_video_merging(self, video_service):
        """Test video merging functionality"""
        
        video_ids = ["video1", "video2", "video3"]
        
        # Mock finding video files
        with patch.object(video_service, '_find_video_file') as mock_find:
            mock_find.return_value = Path("fake_video.mp4")
            
            # Mock MoviePy functionality
            with patch('services.video_service.MOVIEPY_AVAILABLE', True):
                with patch('services.video_service.VideoFileClip') as mock_clip:
                    with patch('services.video_service.concatenate_videoclips') as mock_concat:
                        mock_video = MagicMock()
                        mock_video.duration = 30.0
                        mock_clip.return_value = mock_video
                        
                        mock_final = MagicMock()
                        mock_concat.return_value = mock_final
                        
                        result = await video_service.merge_videos(video_ids)
                        
                        assert result["success"] is True
                        assert result["merged_videos"] == 3
                        assert result["total_duration"] == 90.0  # 3 * 30.0
                        assert "output_file" in result
    
    @pytest.mark.asyncio
    async def test_text_to_speech(self, video_service):
        """Test text-to-speech functionality"""
        
        text = "Welcome to our spiritual meditation session"
        voice = VoiceOption.SPIRITUAL_MALE
        
        result = await video_service.add_text_to_speech(text, voice)
        
        assert result["success"] is True
        assert result["voice_used"] == voice.value
        assert result["text_length"] == len(text)
        assert "output_file" in result
        assert "estimated_duration" in result
    
    @pytest.mark.asyncio
    async def test_video_enhancement(self, video_service):
        """Test video enhancement functionality"""
        
        video_id = "test_video_123"
        preset = "spiritual_ambient"
        
        # Mock finding video file
        with patch.object(video_service, '_find_video_file') as mock_find:
            mock_find.return_value = Path("fake_video.mp4")
            
            # Mock OpenCV functionality
            with patch('services.video_service.OPENCV_AVAILABLE', True):
                with patch('services.video_service.cv2') as mock_cv2:
                    # Mock video capture
                    mock_cap = MagicMock()
                    mock_cap.get.side_effect = [30.0, 1920.0, 1080.0]  # fps, width, height
                    mock_cap.read.side_effect = [(True, "frame1"), (True, "frame2"), (False, None)]
                    mock_cv2.VideoCapture.return_value = mock_cap
                    
                    # Mock video writer
                    mock_writer = MagicMock()
                    mock_cv2.VideoWriter.return_value = mock_writer
                    
                    # Mock enhancement filters
                    with patch.object(video_service, '_apply_enhancement_filters') as mock_enhance:
                        mock_enhance.return_value = "enhanced_frame"
                        
                        result = await video_service.enhance_video(video_id, preset)
                        
                        assert result["success"] is True
                        assert result["enhancement_preset"] == preset
                        assert result["frames_processed"] == 2
                        assert "output_file" in result
    
    @pytest.mark.asyncio
    async def test_subtitle_generation(self, video_service):
        """Test subtitle generation functionality"""
        
        video_id = "test_video_123"
        language = "en"
        
        # Mock finding video file
        with patch.object(video_service, '_find_video_file') as mock_find:
            mock_find.return_value = Path("fake_video.mp4")
            
            # Mock MoviePy audio extraction
            with patch('services.video_service.MOVIEPY_AVAILABLE', True):
                with patch('services.video_service.VideoFileClip') as mock_clip:
                    mock_video = MagicMock()
                    mock_audio = MagicMock()
                    mock_video.audio = mock_audio
                    mock_clip.return_value.__enter__.return_value = mock_video
                    
                    # Mock Whisper service
                    with patch('services.whisper_service.get_whisper_service') as mock_whisper:
                        mock_service = MagicMock()
                        mock_service.transcribe_audio = AsyncMock()
                        mock_service.transcribe_audio.return_value = {
                            "success": True,
                            "transcription": {
                                "segments": [
                                    {
                                        "start": 0.0,
                                        "end": 5.0,
                                        "text": "Welcome to our meditation session"
                                    },
                                    {
                                        "start": 5.0,
                                        "end": 10.0,
                                        "text": "Please find a comfortable position"
                                    }
                                ]
                            }
                        }
                        mock_whisper.return_value = mock_service
                        
                        result = await video_service.generate_subtitles(video_id, language)
                        
                        assert result["success"] is True
                        assert result["language"] == language
                        assert result["subtitle_count"] == 2
                        assert "subtitle_file" in result
    
    @pytest.mark.asyncio
    async def test_subtitle_translation(self, video_service):
        """Test subtitle translation functionality"""
        
        # Create a temporary subtitle file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.srt', delete=False) as f:
            subtitle_content = """1
00:00:00,000 --> 00:00:05,000
Welcome to our meditation session

2
00:00:05,000 --> 00:00:10,000
Please find a comfortable position
"""
            f.write(subtitle_content)
            temp_subtitle = f.name
        
        # Copy to processed directory
        subtitle_filename = "test_subtitles.srt"
        subtitle_path = video_service.processed_dir / subtitle_filename
        
        with open(subtitle_path, 'w') as f:
            f.write(subtitle_content)
        
        try:
            result = await video_service.translate_subtitles(subtitle_filename, "es")
            
            assert result["success"] is True
            assert result["target_language"] == "es"
            assert result["subtitle_count"] == 2
            assert "translated_file" in result
            
        finally:
            # Cleanup
            if os.path.exists(temp_subtitle):
                os.unlink(temp_subtitle)
            if subtitle_path.exists():
                subtitle_path.unlink()
    
    @pytest.mark.asyncio
    async def test_video_analytics(self, video_service):
        """Test video analytics functionality"""
        
        video_id = "test_video_123"
        
        # Setup analytics data
        video_service.video_analytics[video_id] = {
            "upload_time": "2024-01-01T00:00:00",
            "file_size": 10485760,  # 10MB
            "duration": 60.0,
            "view_count": 5,
            "engagement_score": 0.8,
            "processing_operations": [
                {
                    "operation": "trim",
                    "timestamp": "2024-01-01T01:00:00",
                    "parameters": {"start_time": 10, "end_time": 30}
                }
            ]
        }
        
        result = await video_service.get_video_analytics(video_id)
        
        assert result["success"] is True
        assert result["video_id"] == video_id
        assert "analytics" in result
        assert "engagement_metrics" in result["analytics"]
        assert result["analytics"]["engagement_metrics"]["total_processing_operations"] == 1
    
    @pytest.mark.asyncio
    async def test_batch_processing(self, video_service):
        """Test batch processing functionality"""
        
        operations = [
            {
                "type": "trim",
                "video_id": "video1",
                "parameters": {"start_time": 0, "end_time": 10}
            },
            {
                "type": "enhance",
                "video_id": "video2",
                "parameters": {"preset": "spiritual_ambient"}
            },
            {
                "type": "tts",
                "parameters": {"text": "Hello world", "voice": "male_calm"}
            }
        ]
        
        # Mock individual operations
        with patch.object(video_service, 'trim_video') as mock_trim:
            with patch.object(video_service, 'enhance_video') as mock_enhance:
                with patch.object(video_service, 'add_text_to_speech') as mock_tts:
                    
                    mock_trim.return_value = {"success": True, "output_file": "trimmed.mp4"}
                    mock_enhance.return_value = {"success": True, "output_file": "enhanced.mp4"}
                    mock_tts.return_value = {"success": True, "output_file": "speech.mp3"}
                    
                    result = await video_service.batch_process_videos(operations)
                    
                    assert result["success"] is True
                    assert result["total_operations"] == 3
                    assert result["successful_operations"] == 3
                    assert result["success_rate"] == 1.0
                    assert len(result["results"]) == 3
    
    def test_voice_options(self, video_service):
        """Test available voice options"""
        
        voices = video_service.tts_voices
        
        # Check that all voice options are configured
        for voice_option in VoiceOption:
            assert voice_option in voices
            voice_config = voices[voice_option]
            assert "name" in voice_config
            assert "description" in voice_config
            assert "language" in voice_config
            assert "speed" in voice_config
    
    def test_enhancement_presets(self, video_service):
        """Test video enhancement presets"""
        
        presets = video_service.enhancement_presets
        
        # Check that presets are available
        assert "spiritual_ambient" in presets
        assert "meditation_calm" in presets
        assert "teaching_clear" in presets
        
        # Check preset structure
        for preset_name, preset_config in presets.items():
            assert "brightness" in preset_config
            assert "contrast" in preset_config
            assert "saturation" in preset_config
    
    def test_supported_formats(self, video_service):
        """Test supported file formats"""
        
        video_formats = video_service.supported_video_formats
        audio_formats = video_service.supported_audio_formats
        
        # Check video formats
        assert '.mp4' in video_formats
        assert '.avi' in video_formats
        assert '.mov' in video_formats
        
        # Check audio formats
        assert '.mp3' in audio_formats
        assert '.wav' in audio_formats
        assert '.m4a' in audio_formats
    
    def test_srt_time_conversion(self, video_service):
        """Test SRT time format conversion"""
        
        # Test seconds to SRT time conversion
        assert video_service._seconds_to_srt_time(0) == "00:00:00,000"
        assert video_service._seconds_to_srt_time(65.5) == "00:01:05,500"
        assert video_service._seconds_to_srt_time(3661.123) == "01:01:01,123"
    
    def test_subtitle_text_extraction(self, video_service):
        """Test subtitle text extraction"""
        
        subtitle_content = """1
00:00:00,000 --> 00:00:05,000
Welcome to our meditation session

2
00:00:05,000 --> 00:00:10,000
Please find a comfortable position

3
00:00:10,000 --> 00:00:15,000
Close your eyes gently
"""
        
        texts = video_service._extract_subtitle_texts(subtitle_content)
        
        expected_texts = [
            "Welcome to our meditation session",
            "Please find a comfortable position", 
            "Close your eyes gently"
        ]
        
        assert texts == expected_texts


class TestVideoServiceIntegration:
    """Integration tests for video service with Flask app"""
    
    @pytest.fixture
    def app(self):
        """Create Flask app for testing"""
        from app import app
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    def test_video_health_endpoint(self, client):
        """Test video service health check endpoint"""
        
        response = client.get('/api/video/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['status'] == 'healthy'
        assert 'features' in data
    
    def test_voices_endpoint(self, client):
        """Test voices endpoint"""
        
        response = client.get('/api/video/voices')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'voices' in data
        assert len(data['voices']) > 0
    
    def test_enhancement_presets_endpoint(self, client):
        """Test enhancement presets endpoint"""
        
        response = client.get('/api/video/enhancement-presets')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'presets' in data
        assert len(data['presets']) > 0
    
    def test_supported_formats_endpoint(self, client):
        """Test supported formats endpoint"""
        
        response = client.get('/api/video/supported-formats')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'video_formats' in data
        assert 'audio_formats' in data
        assert 'max_video_size_mb' in data
    
    def test_video_upload_no_file(self, client):
        """Test video upload without file"""
        
        response = client.post('/api/video/upload')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'No video file provided' in data['error']
    
    def test_trim_video_invalid_data(self, client):
        """Test video trimming with invalid data"""
        
        response = client.post('/api/video/trim',
                              json={'video_id': 'test123'})  # Missing start_time, end_time
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Missing required field' in data['error']
    
    def test_text_to_speech_invalid_voice(self, client):
        """Test text-to-speech with invalid voice"""
        
        response = client.post('/api/video/text-to-speech',
                              json={
                                  'text': 'Hello world',
                                  'voice': 'invalid_voice'
                              })
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Invalid voice option' in data['error']
    
    def test_batch_processing_invalid_operations(self, client):
        """Test batch processing with invalid operations"""
        
        response = client.post('/api/video/batch-process',
                              json={'operations': []})  # Empty operations
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'At least one operation is required' in data['error']


if __name__ == '__main__':
    # Run the tests
    pytest.main([__file__, '-v'])