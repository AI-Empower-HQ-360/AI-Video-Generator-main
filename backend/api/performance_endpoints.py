"""
Performance monitoring API endpoints
"""

from flask import Blueprint, jsonify, request, current_app
from services.performance_monitor import performance_monitor
from services.cache_service import cache_response, cache
from datetime import datetime, timedelta
from models.database import db


performance_bp = Blueprint('performance', __name__)


@performance_bp.route('/dashboard', methods=['GET'])
@cache_response(timeout=30, key_prefix='performance_dashboard')
def get_performance_dashboard():
    """Get performance dashboard data"""
    try:
        dashboard_data = performance_monitor.get_dashboard_data()
        return jsonify(dashboard_data), 200
    except Exception as e:
        current_app.logger.error(f"Error getting performance dashboard: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@performance_bp.route('/metrics/<metric_name>', methods=['GET'])
@cache_response(timeout=60, key_prefix='performance_metric')
def get_metric_history(metric_name):
    """Get metric history"""
    try:
        # Get time range
        hours = request.args.get('hours', 1, type=int)
        since = datetime.utcnow() - timedelta(hours=hours)
        
        metrics = performance_monitor.metrics.get_metrics(metric_name, since)
        
        return jsonify({
            'metric': metric_name,
            'data_points': [
                {
                    'timestamp': m.timestamp.isoformat(),
                    'value': m.value,
                    'tags': m.tags
                }
                for m in metrics
            ],
            'summary': performance_monitor.metrics.get_metric_summary(metric_name, hours * 60)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting metric history: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@performance_bp.route('/health', methods=['GET'])
def health_check():
    """Application health check endpoint"""
    try:
        # Check database connectivity
        db_healthy = True
        try:
            db.session.execute('SELECT 1')
        except Exception:
            db_healthy = False
        
        # Check cache connectivity
        cache_healthy = True
        try:
            cache.set('health_check', 'ok', timeout=10)
            cache_healthy = cache.get('health_check') == 'ok'
        except Exception:
            cache_healthy = False
        
        # Get current performance metrics
        dashboard_data = performance_monitor.get_dashboard_data()
        
        # Determine overall health
        healthy = (
            db_healthy and 
            cache_healthy and
            dashboard_data['cpu_usage']['latest'] < 90 and
            dashboard_data['memory_usage']['latest'] < 95
        )
        
        status_code = 200 if healthy else 503
        
        return jsonify({
            'status': 'healthy' if healthy else 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'checks': {
                'database': 'ok' if db_healthy else 'failed',
                'cache': 'ok' if cache_healthy else 'failed',
                'cpu_usage': dashboard_data['cpu_usage']['latest'],
                'memory_usage': dashboard_data['memory_usage']['latest']
            },
            'metrics': dashboard_data
        }), status_code
        
    except Exception as e:
        current_app.logger.error(f"Error in health check: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': 'Health check failed'
        }), 503


@performance_bp.route('/cache/stats', methods=['GET'])
def get_cache_stats():
    """Get cache statistics"""
    try:
        # Get cache hit/miss stats from recent metrics
        cache_stats = performance_monitor.metrics.get_metric_summary('cache_hit_rate_percent')
        
        stats = {
            'hit_rate': cache_stats,
            'redis_connected': cache.redis_client is not None,
            'cache_type': 'redis' if cache.redis_client else 'memory'
        }
        
        # Try to get Redis-specific stats if available
        if cache.redis_client:
            try:
                redis_info = cache.redis_client.info()
                stats['redis_info'] = {
                    'connected_clients': redis_info.get('connected_clients', 0),
                    'used_memory': redis_info.get('used_memory_human', '0B'),
                    'hits': redis_info.get('keyspace_hits', 0),
                    'misses': redis_info.get('keyspace_misses', 0),
                    'uptime': redis_info.get('uptime_in_seconds', 0)
                }
            except Exception as e:
                stats['redis_error'] = str(e)
        
        return jsonify(stats), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting cache stats: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@performance_bp.route('/cache/clear', methods=['POST'])
def clear_cache():
    """Clear application cache"""
    try:
        # Get cache pattern to clear (if specified)
        pattern = request.json.get('pattern', '*') if request.json else '*'
        
        if pattern == '*':
            success = cache.clear()
        else:
            from services.cache_service import invalidate_cache_pattern
            cleared_count = invalidate_cache_pattern(pattern)
            success = cleared_count > 0
        
        return jsonify({
            'message': 'Cache cleared successfully' if success else 'Cache clear failed',
            'success': success
        }), 200 if success else 500
        
    except Exception as e:
        current_app.logger.error(f"Error clearing cache: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@performance_bp.route('/database/stats', methods=['GET'])
@cache_response(timeout=300, key_prefix='db_stats')
def get_database_stats():
    """Get database performance statistics"""
    try:
        from models.database import User, SpiritualSession, Video, VideoView
        
        # Get basic counts
        stats = {
            'tables': {
                'users': User.query.count(),
                'spiritual_sessions': SpiritualSession.query.count(),
                'videos': Video.query.count(),
                'video_views': VideoView.query.count()
            },
            'query_performance': performance_monitor.metrics.get_metric_summary(
                'database_query_duration_seconds'
            )
        }
        
        # Get recent activity
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        stats['recent_activity'] = {
            'new_users': User.query.filter(User.created_at >= recent_cutoff).count(),
            'new_sessions': SpiritualSession.query.filter(
                SpiritualSession.created_at >= recent_cutoff
            ).count(),
            'new_videos': Video.query.filter(Video.created_at >= recent_cutoff).count(),
            'video_views': VideoView.query.filter(
                VideoView.started_at >= recent_cutoff
            ).count()
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting database stats: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@performance_bp.route('/alerts', methods=['GET'])
def get_alerts():
    """Get current alert status"""
    try:
        alerts_status = []
        
        for alert_name, alert in performance_monitor.metrics.alerts.items():
            alert_state = performance_monitor.metrics.alert_states[alert_name]
            
            alerts_status.append({
                'name': alert.name,
                'metric': alert.metric,
                'threshold': alert.threshold,
                'condition': alert.condition,
                'duration': alert.duration,
                'enabled': alert.enabled,
                'triggered': alert_state['triggered'],
                'first_trigger': alert_state['first_trigger'].isoformat() 
                              if alert_state['first_trigger'] else None
            })
        
        return jsonify({'alerts': alerts_status}), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting alerts: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@performance_bp.route('/alerts/<alert_name>/toggle', methods=['POST'])
def toggle_alert(alert_name):
    """Enable or disable an alert"""
    try:
        if alert_name not in performance_monitor.metrics.alerts:
            return jsonify({'error': 'Alert not found'}), 404
        
        alert = performance_monitor.metrics.alerts[alert_name]
        alert.enabled = not alert.enabled
        
        return jsonify({
            'message': f'Alert {alert_name} {"enabled" if alert.enabled else "disabled"}',
            'enabled': alert.enabled
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error toggling alert: {e}")
        return jsonify({'error': 'Internal server error'}), 500