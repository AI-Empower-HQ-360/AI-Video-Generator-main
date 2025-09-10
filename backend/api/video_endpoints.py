"""
Video streaming API endpoints with CDN integration and adaptive bitrate
"""

from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from models.database import db, Video, VideoView
from services.video_service import video_service
from services.cache_service import cache_response, cached
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

video_bp = Blueprint('video', __name__)

# Rate limiting
limiter = Limiter(
    app=current_app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)


@video_bp.route('/upload', methods=['POST'])
@limiter.limit("5 per minute")
def upload_video():
    """Upload and process a video file"""
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        file = request.files['video']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get form data
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', 'general').strip()
        guru_type = request.form.get('guru_type', '').strip()
        uploaded_by = request.form.get('uploaded_by')  # User ID
        
        if not title:
            return jsonify({'error': 'Title is required'}), 400
        
        # Check file size (limit to 500MB)
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > 500 * 1024 * 1024:  # 500MB
            return jsonify({'error': 'File size too large (max 500MB)'}), 400
        
        # Upload and process video
        video = video_service.upload_video(
            file=file,
            title=title,
            description=description,
            category=category,
            guru_type=guru_type,
            uploaded_by=uploaded_by
        )
        
        return jsonify({
            'message': 'Video uploaded successfully',
            'video': video.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error uploading video: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@video_bp.route('/<video_id>', methods=['GET'])
@cache_response(timeout=3600, key_prefix='video_detail')
def get_video(video_id):
    """Get video details with all quality options"""
    try:
        video_data = video_service.get_video_with_qualities(video_id)
        
        if not video_data:
            return jsonify({'error': 'Video not found'}), 404
        
        # Check if video is accessible
        if not video_data['is_public']:
            # Add access control logic here
            pass
        
        return jsonify({'video': video_data}), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting video {video_id}: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@video_bp.route('/category/<category>', methods=['GET'])
@cache_response(timeout=1800, key_prefix='videos_category')
def get_videos_by_category(category):
    """Get videos by category with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 50)
        
        videos_data = video_service.get_videos_by_category(
            category=category,
            page=page,
            per_page=per_page
        )
        
        return jsonify(videos_data), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting videos for category {category}: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@video_bp.route('/search', methods=['GET'])
@cache_response(timeout=900, key_prefix='video_search')
def search_videos():
    """Search videos by title, description, or tags"""
    try:
        query = request.args.get('q', '').strip()
        category = request.args.get('category')
        guru_type = request.args.get('guru_type')
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 50)
        
        if not query and not category and not guru_type:
            return jsonify({'error': 'Search query, category, or guru_type required'}), 400
        
        # Build query
        video_query = Video.query.filter(
            Video.is_public == True,
            Video.processing_status == 'completed'
        )
        
        if query:
            video_query = video_query.filter(
                db.or_(
                    Video.title.ilike(f'%{query}%'),
                    Video.description.ilike(f'%{query}%')
                )
            )
        
        if category:
            video_query = video_query.filter(Video.category == category)
        
        if guru_type:
            video_query = video_query.filter(Video.guru_type == guru_type)
        
        # Order by relevance and recency
        video_query = video_query.order_by(
            Video.view_count.desc(),
            Video.created_at.desc()
        )
        
        paginated = video_query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'videos': [video.to_dict() for video in paginated.items],
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': page,
            'per_page': per_page,
            'query': query
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error searching videos: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@video_bp.route('/<video_id>/view', methods=['POST'])
@limiter.limit("100 per hour")
def record_video_view(video_id):
    """Record a video view for analytics"""
    try:
        data = request.get_json() or {}
        
        user_id = data.get('user_id')
        session_id = data.get('session_id')
        watch_duration = data.get('watch_duration', 0)
        completion_percentage = data.get('completion_percentage', 0.0)
        quality_watched = data.get('quality', 'auto')
        
        # Get client info
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', 
                                       request.environ.get('REMOTE_ADDR'))
        user_agent = request.headers.get('User-Agent', '')
        
        # Record the view
        success = video_service.record_view(
            video_id=video_id,
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Update view details if provided
        if watch_duration > 0 or completion_percentage > 0:
            video_view = VideoView.query.filter_by(
                video_id=video_id,
                user_id=user_id if user_id else session_id
            ).order_by(VideoView.started_at.desc()).first()
            
            if video_view:
                video_view.watch_duration = max(video_view.watch_duration, watch_duration)
                video_view.completion_percentage = max(
                    video_view.completion_percentage, completion_percentage
                )
                video_view.quality_watched = quality_watched
                video_view.last_position = data.get('last_position', 0)
                db.session.commit()
        
        return jsonify({
            'message': 'View recorded successfully',
            'counted': success
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error recording video view: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@video_bp.route('/<video_id>/analytics', methods=['GET'])
@cache_response(timeout=3600, key_prefix='video_analytics')
def get_video_analytics(video_id):
    """Get video analytics data"""
    try:
        video = Video.query.get(video_id)
        if not video:
            return jsonify({'error': 'Video not found'}), 404
        
        # Get view statistics
        total_views = VideoView.query.filter_by(video_id=video_id).count()
        unique_viewers = VideoView.query.filter_by(video_id=video_id).distinct(VideoView.user_id).count()
        
        # Average watch time
        avg_watch_time = db.session.query(
            db.func.avg(VideoView.watch_duration)
        ).filter_by(video_id=video_id).scalar() or 0
        
        # Completion rate
        completion_rate = db.session.query(
            db.func.avg(VideoView.completion_percentage)
        ).filter_by(video_id=video_id).scalar() or 0
        
        # Quality distribution
        quality_stats = db.session.query(
            VideoView.quality_watched,
            db.func.count(VideoView.id)
        ).filter_by(video_id=video_id).group_by(VideoView.quality_watched).all()
        
        return jsonify({
            'video_id': video_id,
            'total_views': total_views,
            'unique_viewers': unique_viewers,
            'average_watch_time': round(float(avg_watch_time), 2),
            'completion_rate': round(float(completion_rate), 2),
            'quality_distribution': {
                quality: count for quality, count in quality_stats
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting video analytics: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@video_bp.route('/trending', methods=['GET'])
@cache_response(timeout=1800, key_prefix='trending_videos')
def get_trending_videos():
    """Get trending videos based on recent views and engagement"""
    try:
        limit = min(request.args.get('limit', 20, type=int), 50)
        category = request.args.get('category')
        
        # Query for trending videos (high view count in recent period)
        query = Video.query.filter(
            Video.is_public == True,
            Video.processing_status == 'completed'
        )
        
        if category:
            query = query.filter(Video.category == category)
        
        # Order by recent popularity
        videos = query.order_by(
            Video.view_count.desc(),
            Video.created_at.desc()
        ).limit(limit).all()
        
        return jsonify({
            'videos': [video.to_dict() for video in videos],
            'category': category
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting trending videos: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@video_bp.route('/<video_id>/processing-status', methods=['GET'])
def get_processing_status(video_id):
    """Get video processing status"""
    try:
        video = Video.query.get(video_id)
        if not video:
            return jsonify({'error': 'Video not found'}), 404
        
        return jsonify({
            'video_id': video_id,
            'status': video.processing_status,
            'progress': video.processing_progress,
            'message': {
                'pending': 'Video is queued for processing',
                'processing': f'Processing video... {video.processing_progress}%',
                'completed': 'Video processing completed',
                'failed': 'Video processing failed'
            }.get(video.processing_status, 'Unknown status')
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting processing status: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# Error handlers
@video_bp.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large'}), 413


@video_bp.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'error': 'Rate limit exceeded', 'retry_after': e.retry_after}), 429