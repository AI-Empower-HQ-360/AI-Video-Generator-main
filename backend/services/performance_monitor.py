"""
Performance monitoring and alerting service
"""

import time
import psutil
import threading
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from flask import current_app, request, g
from functools import wraps
import logging
from collections import defaultdict, deque


@dataclass
class MetricPoint:
    """Single metric data point"""
    timestamp: datetime
    value: float
    tags: Dict[str, str] = None


@dataclass
class Alert:
    """Alert definition"""
    name: str
    metric: str
    threshold: float
    condition: str  # 'greater', 'less', 'equal'
    duration: int  # seconds
    enabled: bool = True


class MetricsCollector:
    """Collects and stores application metrics"""
    
    def __init__(self):
        self.metrics = defaultdict(lambda: deque(maxlen=1000))  # Store last 1000 points
        self.alerts = {}
        self.alert_states = defaultdict(lambda: {'triggered': False, 'first_trigger': None})
        self._lock = threading.Lock()
    
    def record_metric(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record a metric value"""
        with self._lock:
            metric_point = MetricPoint(
                timestamp=datetime.utcnow(),
                value=value,
                tags=tags or {}
            )
            self.metrics[name].append(metric_point)
        
        # Check alerts
        self._check_alerts(name, value)
    
    def get_metrics(self, name: str, since: datetime = None) -> List[MetricPoint]:
        """Get metric history"""
        with self._lock:
            metrics = list(self.metrics[name])
            if since:
                metrics = [m for m in metrics if m.timestamp >= since]
            return metrics
    
    def get_metric_summary(self, name: str, duration_minutes: int = 5) -> Dict:
        """Get metric summary for the last N minutes"""
        since = datetime.utcnow() - timedelta(minutes=duration_minutes)
        metrics = self.get_metrics(name, since)
        
        if not metrics:
            return {'count': 0, 'avg': 0, 'min': 0, 'max': 0}
        
        values = [m.value for m in metrics]
        return {
            'count': len(values),
            'avg': sum(values) / len(values),
            'min': min(values),
            'max': max(values),
            'latest': values[-1] if values else 0
        }
    
    def add_alert(self, alert: Alert):
        """Add an alert rule"""
        self.alerts[alert.name] = alert
    
    def _check_alerts(self, metric_name: str, value: float):
        """Check if any alerts should be triggered"""
        for alert_name, alert in self.alerts.items():
            if alert.metric != metric_name or not alert.enabled:
                continue
            
            triggered = False
            if alert.condition == 'greater' and value > alert.threshold:
                triggered = True
            elif alert.condition == 'less' and value < alert.threshold:
                triggered = True
            elif alert.condition == 'equal' and value == alert.threshold:
                triggered = True
            
            alert_state = self.alert_states[alert_name]
            
            if triggered:
                if not alert_state['triggered']:
                    alert_state['first_trigger'] = datetime.utcnow()
                    alert_state['triggered'] = True
                
                # Check if alert duration has been exceeded
                if (datetime.utcnow() - alert_state['first_trigger']).seconds >= alert.duration:
                    self._fire_alert(alert, value)
            else:
                alert_state['triggered'] = False
                alert_state['first_trigger'] = None
    
    def _fire_alert(self, alert: Alert, value: float):
        """Fire an alert"""
        current_app.logger.warning(
            f"ALERT: {alert.name} - {alert.metric} = {value} "
            f"({alert.condition} {alert.threshold})"
        )
        # Here you could integrate with external alerting systems


class PerformanceMonitor:
    """Application performance monitoring"""
    
    def __init__(self, app=None):
        self.metrics = MetricsCollector()
        self.request_metrics = defaultdict(list)
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize performance monitoring with Flask app"""
        app.before_request(self._before_request)
        app.after_request(self._after_request)
        
        # Set up default alerts
        self._setup_default_alerts()
        
        # Start system metrics collection
        self._start_system_metrics_collection()
        
        app.logger.info("Performance monitoring initialized")
    
    def _before_request(self):
        """Record request start time"""
        g.start_time = time.time()
    
    def _after_request(self, response):
        """Record request metrics"""
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            
            # Record response time
            self.metrics.record_metric(
                'http_request_duration_seconds',
                duration,
                tags={
                    'method': request.method,
                    'endpoint': request.endpoint or 'unknown',
                    'status_code': str(response.status_code)
                }
            )
            
            # Record request count
            self.metrics.record_metric(
                'http_requests_total',
                1,
                tags={
                    'method': request.method,
                    'endpoint': request.endpoint or 'unknown',
                    'status_code': str(response.status_code)
                }
            )
            
            # Add performance headers
            response.headers['X-Response-Time'] = f"{duration:.3f}s"
        
        return response
    
    def _setup_default_alerts(self):
        """Set up default performance alerts"""
        alerts = [
            Alert(
                name='high_response_time',
                metric='http_request_duration_seconds',
                threshold=2.0,
                condition='greater',
                duration=60  # Alert if response time > 2s for 1 minute
            ),
            Alert(
                name='high_cpu_usage',
                metric='system_cpu_percent',
                threshold=80.0,
                condition='greater',
                duration=300  # Alert if CPU > 80% for 5 minutes
            ),
            Alert(
                name='high_memory_usage',
                metric='system_memory_percent',
                threshold=85.0,
                condition='greater',
                duration=300  # Alert if memory > 85% for 5 minutes
            ),
            Alert(
                name='low_disk_space',
                metric='system_disk_percent',
                threshold=90.0,
                condition='greater',
                duration=60  # Alert if disk > 90% for 1 minute
            )
        ]
        
        for alert in alerts:
            self.metrics.add_alert(alert)
    
    def _start_system_metrics_collection(self):
        """Start collecting system metrics in background"""
        def collect_system_metrics():
            while True:
                try:
                    # CPU usage
                    cpu_percent = psutil.cpu_percent(interval=1)
                    self.metrics.record_metric('system_cpu_percent', cpu_percent)
                    
                    # Memory usage
                    memory = psutil.virtual_memory()
                    self.metrics.record_metric('system_memory_percent', memory.percent)
                    self.metrics.record_metric('system_memory_available_bytes', memory.available)
                    
                    # Disk usage
                    disk = psutil.disk_usage('/')
                    disk_percent = (disk.used / disk.total) * 100
                    self.metrics.record_metric('system_disk_percent', disk_percent)
                    self.metrics.record_metric('system_disk_free_bytes', disk.free)
                    
                    # Network I/O
                    net_io = psutil.net_io_counters()
                    self.metrics.record_metric('system_network_bytes_sent', net_io.bytes_sent)
                    self.metrics.record_metric('system_network_bytes_recv', net_io.bytes_recv)
                    
                except Exception as e:
                    current_app.logger.error(f"Error collecting system metrics: {e}")
                
                time.sleep(30)  # Collect every 30 seconds
        
        thread = threading.Thread(target=collect_system_metrics, daemon=True)
        thread.start()
    
    def record_custom_metric(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record a custom application metric"""
        self.metrics.record_metric(name, value, tags)
    
    def record_database_query_time(self, query_type: str, duration: float):
        """Record database query performance"""
        self.metrics.record_metric(
            'database_query_duration_seconds',
            duration,
            tags={'query_type': query_type}
        )
    
    def record_cache_hit_rate(self, cache_type: str, hits: int, total: int):
        """Record cache hit rate"""
        hit_rate = (hits / total) * 100 if total > 0 else 0
        self.metrics.record_metric(
            'cache_hit_rate_percent',
            hit_rate,
            tags={'cache_type': cache_type}
        )
    
    def get_dashboard_data(self) -> Dict:
        """Get performance dashboard data"""
        now = datetime.utcnow()
        
        return {
            'response_time': self.metrics.get_metric_summary('http_request_duration_seconds'),
            'request_rate': self.metrics.get_metric_summary('http_requests_total'),
            'cpu_usage': self.metrics.get_metric_summary('system_cpu_percent'),
            'memory_usage': self.metrics.get_metric_summary('system_memory_percent'),
            'disk_usage': self.metrics.get_metric_summary('system_disk_percent'),
            'cache_hit_rate': self.metrics.get_metric_summary('cache_hit_rate_percent'),
            'database_query_time': self.metrics.get_metric_summary('database_query_duration_seconds'),
            'timestamp': now.isoformat()
        }


def monitor_database_query(query_type: str):
    """Decorator to monitor database query performance"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = f(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                if hasattr(current_app, 'performance_monitor'):
                    current_app.performance_monitor.record_database_query_time(
                        query_type, duration
                    )
        return wrapper
    return decorator


def monitor_function_performance(metric_name: str):
    """Decorator to monitor function performance"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = f(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                if hasattr(current_app, 'performance_monitor'):
                    current_app.performance_monitor.record_custom_metric(
                        f'{metric_name}_duration_seconds', duration
                    )
        return wrapper
    return decorator


# Global performance monitor instance
performance_monitor = PerformanceMonitor()