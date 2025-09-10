"""
Video streaming service with CDN integration and adaptive bitrate support
"""

import os
import subprocess
import json
from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin
from flask import current_app
from models.database import db, Video, VideoQuality
from services.cache_service import cache, cached
import uuid


class VideoService:
    """Service for video processing, streaming, and CDN integration"""
    
    SUPPORTED_FORMATS = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
    QUALITY_PRESETS = {
        '240p': {'width': 426, 'height': 240, 'bitrate': 400},
        '360p': {'width': 640, 'height': 360, 'bitrate': 800},
        '480p': {'width': 854, 'height': 480, 'bitrate': 1200},
        '720p': {'width': 1280, 'height': 720, 'bitrate': 2500},
        '1080p': {'width': 1920, 'height': 1080, 'bitrate': 5000}
    }
    
    def __init__(self):
        self.storage_path = None
        self.cdn_domain = None
        self.video_cdn_domain = None
    
    def init_app(self, app):
        """Initialize video service with Flask app"""
        self.storage_path = app.config.get('VIDEO_STORAGE_PATH', 'uploads/videos')
        self.cdn_domain = app.config.get('CDN_DOMAIN', '')
        self.video_cdn_domain = app.config.get('VIDEO_CDN_DOMAIN', '')
        
        # Ensure storage directory exists
        os.makedirs(self.storage_path, exist_ok=True)
        os.makedirs(os.path.join(self.storage_path, 'hls'), exist_ok=True)
        os.makedirs(os.path.join(self.storage_path, 'thumbnails'), exist_ok=True)
    
    def upload_video(self, file, title: str, description: str = '', 
                    category: str = '', guru_type: str = '', 
                    uploaded_by: str = None) -> Video:
        """Upload and process a video file"""
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(self.storage_path, unique_filename)
        
        # Save uploaded file
        file.save(file_path)
        file_size = os.path.getsize(file_path)
        
        # Get video metadata
        metadata = self._get_video_metadata(file_path)
        
        # Create video record
        video = Video(
            title=title,
            description=description,
            filename=unique_filename,
            original_filename=file.filename,
            file_size=file_size,
            duration=metadata.get('duration', 0),
            width=metadata.get('width', 0),
            height=metadata.get('height', 0),
            category=category,
            guru_type=guru_type,
            uploaded_by=uploaded_by,
            processing_status='pending'
        )
        
        db.session.add(video)
        db.session.commit()
        
        # Start async processing
        self._process_video_async(video.id)
        
        return video
    
    def _get_video_metadata(self, file_path: str) -> Dict:
        """Extract video metadata using ffprobe"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_streams', '-show_format', file_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return {}
            
            data = json.loads(result.stdout)
            video_stream = next(
                (s for s in data['streams'] if s['codec_type'] == 'video'), 
                {}
            )
            
            return {
                'duration': int(float(data.get('format', {}).get('duration', 0))),
                'width': int(video_stream.get('width', 0)),
                'height': int(video_stream.get('height', 0)),
                'bitrate': int(video_stream.get('bit_rate', 0))
            }
        except Exception as e:
            current_app.logger.error(f"Error extracting video metadata: {e}")
            return {}
    
    def _process_video_async(self, video_id: str):
        """Process video for adaptive streaming (should be run in background)"""
        try:
            video = Video.query.get(video_id)
            if not video:
                return
            
            video.processing_status = 'processing'
            db.session.commit()
            
            file_path = os.path.join(self.storage_path, video.filename)
            
            # Generate thumbnail
            thumbnail_path = self._generate_thumbnail(file_path, video_id)
            if thumbnail_path:
                video.thumbnail_url = self._get_cdn_url(thumbnail_path)
            
            # Generate multiple quality versions
            qualities_generated = []
            
            for quality, preset in self.QUALITY_PRESETS.items():
                if preset['height'] <= video.height:  # Don't upscale
                    quality_file = self._transcode_video(
                        file_path, video_id, quality, preset
                    )
                    if quality_file:
                        video_quality = VideoQuality(
                            video_id=video_id,
                            quality=quality,
                            bitrate=preset['bitrate'],
                            width=preset['width'],
                            height=preset['height'],
                            file_path=quality_file,
                            file_size=os.path.getsize(quality_file),
                            cdn_url=self._get_cdn_url(quality_file)
                        )
                        db.session.add(video_quality)
                        qualities_generated.append(quality)
            
            # Generate HLS playlist
            hls_playlist = self._generate_hls_playlist(video_id, qualities_generated)
            if hls_playlist:
                video.hls_playlist_url = self._get_cdn_url(hls_playlist)
            
            video.processing_status = 'completed'
            video.processing_progress = 100
            db.session.commit()
            
            # Clear relevant caches
            self._invalidate_video_cache(video_id)
            
        except Exception as e:
            current_app.logger.error(f"Error processing video {video_id}: {e}")
            video = Video.query.get(video_id)
            if video:
                video.processing_status = 'failed'
                db.session.commit()
    
    def _generate_thumbnail(self, video_path: str, video_id: str) -> Optional[str]:
        """Generate video thumbnail"""
        try:
            thumbnail_filename = f"{video_id}_thumb.jpg"
            thumbnail_path = os.path.join(self.storage_path, 'thumbnails', thumbnail_filename)
            
            cmd = [
                'ffmpeg', '-i', video_path, '-ss', '00:00:01.000',
                '-vframes', '1', '-y', thumbnail_path
            ]
            result = subprocess.run(cmd, capture_output=True)
            
            return thumbnail_path if result.returncode == 0 else None
        except Exception as e:
            current_app.logger.error(f"Error generating thumbnail: {e}")
            return None
    
    def _transcode_video(self, input_path: str, video_id: str, 
                        quality: str, preset: Dict) -> Optional[str]:
        """Transcode video to specific quality"""
        try:
            output_filename = f"{video_id}_{quality}.mp4"
            output_path = os.path.join(self.storage_path, output_filename)
            
            cmd = [
                'ffmpeg', '-i', input_path,
                '-c:v', 'libx264', '-c:a', 'aac',
                '-b:v', f"{preset['bitrate']}k",
                '-vf', f"scale={preset['width']}:{preset['height']}",
                '-preset', 'medium', '-crf', '23',
                '-y', output_path
            ]
            result = subprocess.run(cmd, capture_output=True)
            
            return output_path if result.returncode == 0 else None
        except Exception as e:
            current_app.logger.error(f"Error transcoding video: {e}")
            return None
    
    def _generate_hls_playlist(self, video_id: str, qualities: List[str]) -> Optional[str]:
        """Generate HLS master playlist"""
        try:
            hls_dir = os.path.join(self.storage_path, 'hls', video_id)
            os.makedirs(hls_dir, exist_ok=True)
            
            master_playlist_path = os.path.join(hls_dir, 'master.m3u8')
            
            with open(master_playlist_path, 'w') as f:
                f.write('#EXTM3U\n')
                f.write('#EXT-X-VERSION:3\n\n')
                
                for quality in qualities:
                    preset = self.QUALITY_PRESETS[quality]
                    playlist_filename = f"{quality}.m3u8"
                    
                    # Generate individual quality playlist
                    self._generate_quality_hls_playlist(
                        video_id, quality, preset, 
                        os.path.join(hls_dir, playlist_filename)
                    )
                    
                    f.write(f'#EXT-X-STREAM-INF:BANDWIDTH={preset["bitrate"]*1000},'
                           f'RESOLUTION={preset["width"]}x{preset["height"]}\n')
                    f.write(f'{playlist_filename}\n')
            
            return master_playlist_path
        except Exception as e:
            current_app.logger.error(f"Error generating HLS playlist: {e}")
            return None
    
    def _generate_quality_hls_playlist(self, video_id: str, quality: str, 
                                     preset: Dict, playlist_path: str):
        """Generate HLS playlist for specific quality"""
        try:
            video_path = os.path.join(self.storage_path, f"{video_id}_{quality}.mp4")
            segment_dir = os.path.dirname(playlist_path)
            segment_pattern = os.path.join(segment_dir, f"{quality}_%03d.ts")
            
            cmd = [
                'ffmpeg', '-i', video_path,
                '-c', 'copy', '-hls_time', '10', '-hls_list_size', '0',
                '-hls_segment_filename', segment_pattern,
                '-y', playlist_path
            ]
            subprocess.run(cmd, capture_output=True)
        except Exception as e:
            current_app.logger.error(f"Error generating quality HLS playlist: {e}")
    
    def _get_cdn_url(self, file_path: str) -> str:
        """Get CDN URL for file"""
        if self.video_cdn_domain:
            relative_path = os.path.relpath(file_path, self.storage_path)
            return urljoin(self.video_cdn_domain, relative_path)
        return file_path
    
    def _invalidate_video_cache(self, video_id: str):
        """Invalidate cache for video-related data"""
        cache.delete(f"video:{video_id}")
        cache.delete(f"video_qualities:{video_id}")
    
    @cached(timeout=3600, key_prefix='video')
    def get_video_with_qualities(self, video_id: str) -> Optional[Dict]:
        """Get video with all quality options"""
        video = Video.query.get(video_id)
        if not video:
            return None
        
        qualities = VideoQuality.query.filter_by(video_id=video_id).all()
        
        video_data = video.to_dict()
        video_data['qualities'] = [q.to_dict() for q in qualities]
        
        return video_data
    
    @cached(timeout=1800, key_prefix='videos')
    def get_videos_by_category(self, category: str, page: int = 1, 
                              per_page: int = 20) -> Dict:
        """Get paginated videos by category"""
        query = Video.query.filter_by(
            category=category, 
            is_public=True, 
            processing_status='completed'
        ).order_by(Video.created_at.desc())
        
        paginated = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return {
            'videos': [video.to_dict() for video in paginated.items],
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': page,
            'per_page': per_page
        }
    
    def record_view(self, video_id: str, user_id: str = None, 
                   session_id: str = None, ip_address: str = None,
                   user_agent: str = None) -> bool:
        """Record video view for analytics"""
        try:
            from models.database import VideoView
            
            # Check if this user/session already has a recent view
            recent_view = VideoView.query.filter_by(
                video_id=video_id,
                user_id=user_id if user_id else session_id
            ).filter(
                VideoView.started_at > db.func.now() - db.text("INTERVAL 1 HOUR")
            ).first()
            
            if recent_view:
                return False  # Don't count duplicate views within 1 hour
            
            video_view = VideoView(
                video_id=video_id,
                user_id=user_id,
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            db.session.add(video_view)
            
            # Increment view count
            video = Video.query.get(video_id)
            if video:
                video.view_count += 1
            
            db.session.commit()
            
            # Invalidate cache
            self._invalidate_video_cache(video_id)
            
            return True
        except Exception as e:
            current_app.logger.error(f"Error recording video view: {e}")
            db.session.rollback()
            return False


# Global video service instance
video_service = VideoService()