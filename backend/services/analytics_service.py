"""
Analytics services for real-time data processing and insights generation.
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque
import threading

class RealTimeAnalytics:
    """Service for real-time analytics processing."""
    
    def __init__(self):
        self.active_sessions = {}  # session_id -> session_data
        self.video_metrics = defaultdict(lambda: {
            'viewers': 0,
            'total_watch_time': 0,
            'interactions': [],
            'heatmap': defaultdict(int)
        })
        self.engagement_events = deque(maxlen=10000)  # Recent events buffer
        self._lock = threading.Lock()
    
    def track_viewer_session(self, session_id: str, video_id: str, user_id: str = None):
        """Start tracking a viewer session."""
        with self._lock:
            self.active_sessions[session_id] = {
                'video_id': video_id,
                'user_id': user_id,
                'start_time': datetime.utcnow(),
                'last_activity': datetime.utcnow(),
                'watch_time': 0,
                'current_position': 0,
                'interactions': [],
                'is_active': True
            }
            
            # Update video metrics
            self.video_metrics[video_id]['viewers'] += 1
    
    def track_engagement_event(self, session_id: str, event_type: str, 
                             video_time: float, metadata: Dict = None):
        """Track an engagement event."""
        timestamp = datetime.utcnow()
        
        with self._lock:
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                session['last_activity'] = timestamp
                session['current_position'] = video_time
                
                event = {
                    'session_id': session_id,
                    'video_id': session['video_id'],
                    'event_type': event_type,
                    'video_time': video_time,
                    'timestamp': timestamp,
                    'metadata': metadata or {}
                }
                
                session['interactions'].append(event)
                self.engagement_events.append(event)
                
                # Update heatmap data
                video_id = session['video_id']
                time_bucket = int(video_time // 10) * 10  # 10-second buckets
                self.video_metrics[video_id]['heatmap'][time_bucket] += 1
                
                return True
        return False
    
    def update_watch_time(self, session_id: str, watch_time: float):
        """Update watch time for a session."""
        with self._lock:
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                session['watch_time'] = watch_time
                session['last_activity'] = datetime.utcnow()
                
                # Update video total watch time
                video_id = session['video_id']
                self.video_metrics[video_id]['total_watch_time'] += watch_time
    
    def end_session(self, session_id: str):
        """End a viewer session."""
        with self._lock:
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                session['is_active'] = False
                session['end_time'] = datetime.utcnow()
                
                # Update video metrics
                video_id = session['video_id']
                if self.video_metrics[video_id]['viewers'] > 0:
                    self.video_metrics[video_id]['viewers'] -= 1
    
    def get_real_time_heatmap(self, video_id: str, duration: float = 300) -> List[Dict]:
        """Get real-time heatmap data for a video."""
        with self._lock:
            heatmap_data = []
            video_data = self.video_metrics.get(video_id, {})
            heatmap = video_data.get('heatmap', {})
            
            for time_bucket in range(0, int(duration), 10):
                intensity = heatmap.get(time_bucket, 0)
                # Normalize intensity (could be based on total viewers)
                normalized_intensity = min(intensity / 10.0, 1.0) if intensity > 0 else 0
                
                heatmap_data.append({
                    'time': time_bucket,
                    'intensity': normalized_intensity,
                    'raw_interactions': intensity
                })
            
            return heatmap_data
    
    def get_active_viewers(self, video_id: str) -> int:
        """Get current number of active viewers for a video."""
        with self._lock:
            return self.video_metrics.get(video_id, {}).get('viewers', 0)
    
    def get_recent_events(self, video_id: str = None, limit: int = 100) -> List[Dict]:
        """Get recent engagement events."""
        with self._lock:
            events = list(self.engagement_events)
            
            if video_id:
                events = [e for e in events if e.get('video_id') == video_id]
            
            # Convert datetime objects to ISO strings for JSON serialization
            for event in events:
                if isinstance(event.get('timestamp'), datetime):
                    event['timestamp'] = event['timestamp'].isoformat()
            
            return events[-limit:]

class PredictiveAnalytics:
    """Service for predictive modeling and insights."""
    
    def __init__(self):
        self.model_cache = {}
        self.performance_history = defaultdict(list)
    
    def calculate_engagement_score(self, session_data: Dict) -> float:
        """Calculate engagement score for a session."""
        if not session_data.get('interactions'):
            return 0.0
        
        # Factors for engagement scoring
        interaction_count = len(session_data['interactions'])
        watch_time = session_data.get('watch_time', 0)
        session_duration = (
            session_data.get('end_time', datetime.utcnow()) - 
            session_data.get('start_time', datetime.utcnow())
        ).total_seconds()
        
        # Calculate score (0-100)
        interaction_score = min(interaction_count * 5, 40)  # Max 40 points
        time_score = min((watch_time / max(session_duration, 1)) * 60, 60)  # Max 60 points
        
        return interaction_score + time_score
    
    def predict_drop_off_probability(self, current_position: float, 
                                   session_data: Dict) -> float:
        """Predict probability of viewer dropping off."""
        # Simple heuristic-based prediction
        # In real implementation, this would use ML models
        
        watch_time = session_data.get('watch_time', 0)
        interactions = len(session_data.get('interactions', []))
        
        # Base probability increases with time
        base_prob = min(current_position / 300, 0.7)  # Max 70% at 5 minutes
        
        # Adjust based on engagement
        engagement_factor = max(0.1, 1 - (interactions / 10))  # More interactions = less likely to drop
        
        return min(base_prob * engagement_factor, 0.95)
    
    def predict_completion_likelihood(self, session_data: Dict) -> float:
        """Predict likelihood of session completion."""
        current_pos = session_data.get('current_position', 0)
        interactions = len(session_data.get('interactions', []))
        watch_time = session_data.get('watch_time', 0)
        
        # Simple scoring algorithm
        position_score = current_pos / 300  # Normalize to 5-minute video
        interaction_score = min(interactions / 5, 1)  # Max at 5 interactions
        engagement_score = min(watch_time / current_pos if current_pos > 0 else 0, 1)
        
        return (position_score * 0.4 + interaction_score * 0.3 + engagement_score * 0.3)
    
    def generate_content_recommendations(self, video_data: Dict) -> List[str]:
        """Generate recommendations for content optimization."""
        recommendations = []
        
        # Analyze performance patterns
        avg_completion = video_data.get('avg_completion_rate', 0)
        drop_off_points = video_data.get('drop_off_points', [])
        
        if avg_completion < 0.5:
            recommendations.append("Consider shortening content or improving hook in first 30 seconds")
        
        if drop_off_points:
            major_drop_off = max(drop_off_points, key=lambda x: x.get('percentage', 0))
            if major_drop_off.get('percentage', 0) > 0.2:
                recommendations.append(f"Review content at {major_drop_off['time']}s - major drop-off point")
        
        engagement_rate = video_data.get('engagement_rate', 0)
        if engagement_rate < 0.05:
            recommendations.append("Add more interactive elements or call-to-actions")
        
        return recommendations

class ConversionAnalytics:
    """Service for conversion tracking and ROI analytics."""
    
    def __init__(self):
        self.conversion_events = []
        self.funnel_stages = defaultdict(lambda: defaultdict(int))
    
    def track_conversion(self, video_id: str, user_id: str, conversion_type: str,
                        value: float = 0, metadata: Dict = None):
        """Track a conversion event."""
        conversion = {
            'video_id': video_id,
            'user_id': user_id,
            'conversion_type': conversion_type,
            'value': value,
            'timestamp': datetime.utcnow(),
            'metadata': metadata or {}
        }
        
        self.conversion_events.append(conversion)
        return conversion
    
    def calculate_roi(self, video_id: str, cost: float, time_period: int = 7) -> Dict:
        """Calculate ROI for a video over a time period."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=time_period)
        
        # Filter conversions for this video and time period
        relevant_conversions = [
            c for c in self.conversion_events
            if c['video_id'] == video_id and start_date <= c['timestamp'] <= end_date
        ]
        
        total_revenue = sum(c['value'] for c in relevant_conversions)
        conversion_count = len(relevant_conversions)
        
        roi = (total_revenue - cost) / cost if cost > 0 else 0
        
        return {
            'revenue': total_revenue,
            'cost': cost,
            'roi': roi,
            'conversion_count': conversion_count,
            'cost_per_conversion': cost / conversion_count if conversion_count > 0 else 0,
            'time_period_days': time_period
        }
    
    def analyze_conversion_funnel(self, video_id: str) -> Dict:
        """Analyze conversion funnel for a video."""
        # Mock funnel analysis
        total_views = 1000  # Would be retrieved from actual data
        
        funnel = {
            'views': total_views,
            'engaged_viewers': int(total_views * 0.6),  # 60% engagement
            'clicks': int(total_views * 0.15),  # 15% click-through
            'conversions': len([c for c in self.conversion_events if c['video_id'] == video_id])
        }
        
        # Calculate conversion rates
        funnel['engagement_rate'] = funnel['engaged_viewers'] / funnel['views']
        funnel['click_rate'] = funnel['clicks'] / funnel['views']
        funnel['conversion_rate'] = funnel['conversions'] / funnel['views'] if funnel['views'] > 0 else 0
        
        return funnel

# Global instances
real_time_analytics = RealTimeAnalytics()
predictive_analytics = PredictiveAnalytics()
conversion_analytics = ConversionAnalytics()