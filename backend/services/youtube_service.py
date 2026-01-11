"""
YouTube API Integration Service
Handles YouTube video operations including transcript fetching and video information retrieval.
"""

import os
import re
import logging
from typing import Dict, List, Optional, Any
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable
)

logger = logging.getLogger(__name__)


class YouTubeService:
    """Service for interacting with YouTube API and transcripts."""
    
    def __init__(self):
        """Initialize YouTube service with API key from environment."""
        self.api_key = os.environ.get('YOUTUBE_API_KEY')
        self.base_url = "https://www.googleapis.com/youtube/v3"
        
        if not self.api_key or self.api_key == 'your-youtube-api-key-here':
            logger.warning("YouTube API key not configured properly")
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """
        Extract video ID from YouTube URL.
        
        Args:
            url: YouTube video URL
            
        Returns:
            Video ID if found, None otherwise
        """
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)',
            r'youtube\.com\/embed\/([^&\n?#]+)',
            r'youtube\.com\/v\/([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # If no pattern matches, assume the input is already a video ID
        if len(url) == 11 and not '/' in url:
            return url
            
        return None
    
    def get_video_info(self, video_id: str) -> Dict[str, Any]:
        """
        Get video information from YouTube API.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Dictionary with video information
        """
        if not self.api_key or self.api_key == 'your-youtube-api-key-here':
            return {
                'error': 'YouTube API key not configured',
                'status': 'error'
            }
        
        try:
            url = f"{self.base_url}/videos"
            params = {
                'part': 'snippet,contentDetails,statistics',
                'id': video_id,
                'key': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('items'):
                return {
                    'error': 'Video not found',
                    'status': 'not_found'
                }
            
            video = data['items'][0]
            snippet = video.get('snippet', {})
            statistics = video.get('statistics', {})
            
            return {
                'status': 'success',
                'title': snippet.get('title', ''),
                'description': snippet.get('description', ''),
                'channel': snippet.get('channelTitle', ''),
                'published_at': snippet.get('publishedAt', ''),
                'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                'views': statistics.get('viewCount', '0'),
                'likes': statistics.get('likeCount', '0'),
                'duration': video.get('contentDetails', {}).get('duration', '')
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching video info: {e}")
            return {
                'error': str(e),
                'status': 'error'
            }
    
    def get_transcript(self, video_id: str, languages: List[str] = None) -> Dict[str, Any]:
        """
        Get transcript for a YouTube video.
        
        Args:
            video_id: YouTube video ID
            languages: List of preferred language codes (e.g., ['en', 'hi'])
            
        Returns:
            Dictionary with transcript text and metadata
        """
        if languages is None:
            languages = ['en', 'en-US', 'en-GB']
        
        try:
            # Try to fetch transcript
            transcript_list = YouTubeTranscriptApi.list(video_id)
            
            # Try manual transcripts first
            try:
                transcript = transcript_list.find_transcript(languages)
                is_auto_generated = False
            except NoTranscriptFound:
                # Fallback to auto-generated
                try:
                    transcript = transcript_list.find_generated_transcript(languages)
                    is_auto_generated = True
                except NoTranscriptFound:
                    return {
                        'error': 'No transcript available in requested languages',
                        'status': 'no_transcript',
                        'available_languages': [t.language_code for t in transcript_list]
                    }
            
            # Fetch the transcript
            transcript_data = transcript.fetch()
            
            # Combine all text segments
            full_text = ' '.join([entry['text'] for entry in transcript_data])
            
            return {
                'status': 'success',
                'text': full_text,
                'language': transcript.language_code,
                'is_auto_generated': is_auto_generated,
                'segments': transcript_data
            }
            
        except TranscriptsDisabled:
            return {
                'error': 'Transcripts are disabled for this video',
                'status': 'disabled'
            }
        except VideoUnavailable:
            return {
                'error': 'Video is unavailable',
                'status': 'unavailable'
            }
        except Exception as e:
            logger.error(f"Error fetching transcript: {e}")
            return {
                'error': str(e),
                'status': 'error'
            }
    
    def get_video_summary(self, video_url: str) -> Dict[str, Any]:
        """
        Get complete video information including transcript.
        
        Args:
            video_url: YouTube video URL or ID
            
        Returns:
            Dictionary with video info and transcript
        """
        video_id = self.extract_video_id(video_url)
        
        if not video_id:
            return {
                'error': 'Invalid YouTube URL or video ID',
                'status': 'invalid_url'
            }
        
        # Get video info
        video_info = self.get_video_info(video_id)
        
        # Get transcript
        transcript_info = self.get_transcript(video_id)
        
        # Combine results
        result = {
            'video_id': video_id,
            'video_info': video_info,
            'transcript': transcript_info
        }
        
        return result


# Create singleton instance
youtube_service = YouTubeService()
