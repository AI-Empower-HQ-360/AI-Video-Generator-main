try:
    from flask_sqlalchemy import SQLAlchemy
except ImportError:
    raise ImportError(
        "The 'flask_sqlalchemy' package is required. "
        "Install it with 'pip install flask_sqlalchemy'."
    )

from datetime import datetime
import uuid

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=True, index=True)
    name = db.Column(db.String(100), nullable=True)
    spiritual_level = db.Column(db.String(50), default='beginner', index=True)
    preferred_gurus = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    last_active = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    sessions = db.relationship('SpiritualSession', backref='user', lazy='dynamic')
    user_sessions = db.relationship('UserSession', backref='user', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'spiritual_level': self.spiritual_level,
            'preferred_gurus': self.preferred_gurus,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SpiritualSession(db.Model):
    __tablename__ = 'spiritual_sessions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True, index=True)
    guru_type = db.Column(db.String(50), nullable=False, index=True)
    question = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    satisfaction_rating = db.Column(db.Integer)
    session_duration = db.Column(db.Integer)  # in seconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Composite indexes for common queries
    __table_args__ = (
        db.Index('idx_user_guru_created', 'user_id', 'guru_type', 'created_at'),
        db.Index('idx_guru_created', 'guru_type', 'created_at'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'guru_type': self.guru_type,
            'question': self.question,
            'response': self.response,
            'satisfaction_rating': self.satisfaction_rating,
            'created_at': self.created_at.isoformat()
        }

class DailyWisdom(db.Model):
    __tablename__ = 'daily_wisdom'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    date = db.Column(db.Date, unique=True, nullable=False)
    sloka_sanskrit = db.Column(db.Text)
    sloka_translation = db.Column(db.Text)
    wisdom_message = db.Column(db.Text)
    guru_type = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'sloka_sanskrit': self.sloka_sanskrit,
            'sloka_translation': self.sloka_translation,
            'wisdom_message': self.wisdom_message,
            'guru_type': self.guru_type
        }

class UserSession(db.Model):
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    session_type = db.Column(db.String(50), nullable=False, default='meditation', index=True)
    status = db.Column(db.String(20), nullable=False, default='active', index=True)  # active, completed, cancelled
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    end_time = db.Column(db.DateTime)
    duration = db.Column(db.Integer)  # in seconds
    notes = db.Column(db.Text)
    reflection = db.Column(db.Text)
    real_life_application = db.Column(db.Text)
    
    # Composite indexes for common queries
    __table_args__ = (
        db.Index('idx_user_status_start', 'user_id', 'status', 'start_time'),
        db.Index('idx_session_type_start', 'session_type', 'start_time'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_type': self.session_type,
            'status': self.status,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': self.duration,
            'notes': self.notes,
            'reflection': self.reflection,
            'real_life_application': self.real_life_application
        }


class Video(db.Model):
    __tablename__ = 'videos'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.BigInteger)  # in bytes
    duration = db.Column(db.Integer)  # in seconds
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    
    # Streaming metadata
    hls_playlist_url = db.Column(db.String(512))  # HLS master playlist URL
    dash_manifest_url = db.Column(db.String(512))  # DASH manifest URL
    thumbnail_url = db.Column(db.String(512))
    
    # Processing status
    processing_status = db.Column(db.String(50), default='pending', index=True)  # pending, processing, completed, failed
    processing_progress = db.Column(db.Integer, default=0)  # 0-100
    
    # Categorization
    category = db.Column(db.String(100), index=True)  # meditation, teaching, music, etc.
    tags = db.Column(db.JSON)  # Array of tags for searching
    guru_type = db.Column(db.String(50), index=True)  # Associated guru if applicable
    
    # Access control
    is_public = db.Column(db.Boolean, default=True, index=True)
    required_level = db.Column(db.String(50))  # beginner, intermediate, advanced
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    uploaded_by = db.Column(db.String(36), db.ForeignKey('users.id'), index=True)
    
    # Analytics
    view_count = db.Column(db.Integer, default=0, index=True)
    like_count = db.Column(db.Integer, default=0)
    
    # Relationships
    video_qualities = db.relationship('VideoQuality', backref='video', lazy='dynamic', cascade='all, delete-orphan')
    video_views = db.relationship('VideoView', backref='video', lazy='dynamic', cascade='all, delete-orphan')
    
    # Composite indexes for common queries
    __table_args__ = (
        db.Index('idx_category_public_created', 'category', 'is_public', 'created_at'),
        db.Index('idx_guru_public_created', 'guru_type', 'is_public', 'created_at'),
        db.Index('idx_status_created', 'processing_status', 'created_at'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'duration': self.duration,
            'width': self.width,
            'height': self.height,
            'hls_playlist_url': self.hls_playlist_url,
            'dash_manifest_url': self.dash_manifest_url,
            'thumbnail_url': self.thumbnail_url,
            'processing_status': self.processing_status,
            'processing_progress': self.processing_progress,
            'category': self.category,
            'tags': self.tags,
            'guru_type': self.guru_type,
            'is_public': self.is_public,
            'required_level': self.required_level,
            'created_at': self.created_at.isoformat(),
            'view_count': self.view_count,
            'like_count': self.like_count
        }


class VideoQuality(db.Model):
    __tablename__ = 'video_qualities'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    video_id = db.Column(db.String(36), db.ForeignKey('videos.id'), nullable=False, index=True)
    quality = db.Column(db.String(20), nullable=False)  # 240p, 360p, 480p, 720p, 1080p
    bitrate = db.Column(db.Integer, nullable=False)  # in kbps
    width = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    file_size = db.Column(db.BigInteger)  # in bytes
    cdn_url = db.Column(db.String(512))  # CDN URL for this quality
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Composite index for video quality lookup
    __table_args__ = (
        db.Index('idx_video_quality', 'video_id', 'quality'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'quality': self.quality,
            'bitrate': self.bitrate,
            'width': self.width,
            'height': self.height,
            'cdn_url': self.cdn_url,
            'file_size': self.file_size
        }


class VideoView(db.Model):
    __tablename__ = 'video_views'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    video_id = db.Column(db.String(36), db.ForeignKey('videos.id'), nullable=False, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True, index=True)
    session_id = db.Column(db.String(100))  # For anonymous users
    ip_address = db.Column(db.String(45))  # IPv4/IPv6
    user_agent = db.Column(db.String(512))
    
    # View metadata
    watch_duration = db.Column(db.Integer, default=0)  # seconds watched
    completion_percentage = db.Column(db.Float, default=0.0)  # 0.0 to 100.0
    quality_watched = db.Column(db.String(20))  # Quality level watched
    
    # Timestamps
    started_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    last_position = db.Column(db.Integer, default=0)  # Last playback position in seconds
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Composite indexes for analytics
    __table_args__ = (
        db.Index('idx_video_user_started', 'video_id', 'user_id', 'started_at'),
        db.Index('idx_video_started', 'video_id', 'started_at'),
        db.Index('idx_user_started', 'user_id', 'started_at'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'video_id': self.video_id,
            'user_id': self.user_id,
            'watch_duration': self.watch_duration,
            'completion_percentage': self.completion_percentage,
            'quality_watched': self.quality_watched,
            'started_at': self.started_at.isoformat(),
            'last_position': self.last_position
        }
