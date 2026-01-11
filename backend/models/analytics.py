"""
Analytics data models for video engagement tracking and insights.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()

class VideoEngagement(Base):
    """Model for tracking video engagement metrics."""
    __tablename__ = 'video_engagement'
    
    id = Column(Integer, primary_key=True)
    video_id = Column(String(255), nullable=False, index=True)
    user_id = Column(String(255), nullable=True, index=True)
    session_id = Column(String(255), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Engagement metrics
    watch_time_seconds = Column(Float, default=0.0)
    total_duration_seconds = Column(Float, nullable=False)
    completion_rate = Column(Float, default=0.0)  # Percentage watched
    
    # Interaction points
    interactions = Column(JSON)  # Store click/hover/pause events with timestamps
    drop_off_point = Column(Float, nullable=True)  # Time when user stopped watching
    
    # Device and context
    device_type = Column(String(50), nullable=True)
    browser = Column(String(100), nullable=True)
    resolution = Column(String(20), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class HeatmapData(Base):
    """Model for storing video heatmap engagement data."""
    __tablename__ = 'heatmap_data'
    
    id = Column(Integer, primary_key=True)
    video_id = Column(String(255), nullable=False, index=True)
    time_segment = Column(Float, nullable=False)  # Time in seconds
    engagement_intensity = Column(Float, default=0.0)  # 0-1 scale
    interaction_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    
    # Aggregate data for the time segment
    avg_attention_score = Column(Float, default=0.0)
    drop_off_count = Column(Integer, default=0)
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ConversionMetrics(Base):
    """Model for tracking conversion and ROI analytics."""
    __tablename__ = 'conversion_metrics'
    
    id = Column(Integer, primary_key=True)
    video_id = Column(String(255), nullable=False, index=True)
    user_id = Column(String(255), nullable=True, index=True)
    session_id = Column(String(255), nullable=False, index=True)
    
    # Conversion tracking
    conversion_type = Column(String(100), nullable=False)  # signup, purchase, download, etc.
    conversion_value = Column(Float, default=0.0)  # Monetary value
    time_to_conversion = Column(Float, nullable=True)  # Seconds from video start
    
    # Attribution
    attribution_source = Column(String(100), nullable=True)
    campaign_id = Column(String(255), nullable=True)
    
    converted_at = Column(DateTime, default=datetime.utcnow)

class ViewerBehavior(Base):
    """Model for detailed viewer behavior analysis."""
    __tablename__ = 'viewer_behavior'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), nullable=True, index=True)
    session_id = Column(String(255), nullable=False, index=True)
    video_id = Column(String(255), nullable=False, index=True)
    
    # Behavior patterns
    pause_events = Column(JSON)  # List of pause timestamps and durations
    rewind_events = Column(JSON)  # List of rewind events
    fast_forward_events = Column(JSON)  # List of fast forward events
    volume_changes = Column(JSON)  # Volume adjustment events
    
    # Engagement metrics
    engagement_score = Column(Float, default=0.0)  # Calculated engagement score
    attention_spans = Column(JSON)  # Periods of continuous viewing
    
    # Predictive indicators
    likelihood_to_complete = Column(Float, default=0.5)  # 0-1 prediction
    predicted_drop_off_time = Column(Float, nullable=True)
    
    analyzed_at = Column(DateTime, default=datetime.utcnow)

class ContentPerformance(Base):
    """Model for content performance analytics and predictions."""
    __tablename__ = 'content_performance'
    
    id = Column(Integer, primary_key=True)
    video_id = Column(String(255), nullable=False, unique=True, index=True)
    
    # Performance metrics
    total_views = Column(Integer, default=0)
    unique_viewers = Column(Integer, default=0)
    avg_watch_time = Column(Float, default=0.0)
    avg_completion_rate = Column(Float, default=0.0)
    engagement_rate = Column(Float, default=0.0)
    
    # Conversion metrics
    total_conversions = Column(Integer, default=0)
    conversion_rate = Column(Float, default=0.0)
    total_revenue = Column(Float, default=0.0)
    roi = Column(Float, default=0.0)
    
    # Predictive modeling
    predicted_performance_score = Column(Float, default=0.0)  # 0-100 scale
    trending_score = Column(Float, default=0.0)  # Momentum indicator
    
    # Content attributes for analysis
    content_category = Column(String(100), nullable=True)
    content_tags = Column(JSON)  # List of tags
    duration_seconds = Column(Float, nullable=True)
    
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CompetitorData(Base):
    """Model for competitor analysis and benchmarking."""
    __tablename__ = 'competitor_data'
    
    id = Column(Integer, primary_key=True)
    competitor_name = Column(String(255), nullable=False, index=True)
    content_type = Column(String(100), nullable=False)
    
    # Benchmarking metrics
    avg_engagement_rate = Column(Float, default=0.0)
    avg_completion_rate = Column(Float, default=0.0)
    avg_conversion_rate = Column(Float, default=0.0)
    
    # Content strategy insights
    posting_frequency = Column(Float, default=0.0)  # Posts per week
    optimal_duration = Column(Float, default=0.0)  # Seconds
    top_performing_tags = Column(JSON)  # List of effective tags
    
    # Market position
    market_share = Column(Float, default=0.0)  # Percentage
    growth_rate = Column(Float, default=0.0)  # Monthly growth
    
    last_analyzed = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DashboardWidget(Base):
    """Model for custom dashboard widget configurations."""
    __tablename__ = 'dashboard_widgets'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), nullable=False, index=True)
    widget_type = Column(String(100), nullable=False)  # heatmap, roi_chart, behavior_flow, etc.
    
    # Widget configuration
    title = Column(String(255), nullable=False)
    configuration = Column(JSON)  # Widget-specific settings
    position_x = Column(Integer, default=0)
    position_y = Column(Integer, default=0)
    width = Column(Integer, default=4)
    height = Column(Integer, default=3)
    
    # Visibility and sharing
    is_active = Column(Boolean, default=True)
    is_shared = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)