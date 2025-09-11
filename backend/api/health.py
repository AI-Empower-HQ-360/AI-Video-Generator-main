from flask import Blueprint, jsonify, current_app
import time
import psutil
import os
from datetime import datetime
import requests

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Basic health check endpoint"""
    try:
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'region': os.environ.get('AWS_REGION', 'unknown'),
            'environment': os.environ.get('ENVIRONMENT', 'development')
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@health_bp.route('/health/database', methods=['GET'])
def database_health():
    """Database connectivity health check"""
    try:
        from sqlalchemy import text
        from backend.models import db
        
        # Simple database query to check connectivity
        result = db.session.execute(text('SELECT 1'))
        db.session.commit()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        current_app.logger.error(f"Database health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@health_bp.route('/health/external', methods=['GET'])
def external_services_health():
    """External services health check"""
    services_status = {}
    overall_status = 'healthy'
    
    # Check OpenAI API connectivity
    try:
        openai_key = os.environ.get('OPENAI_API_KEY')
        if openai_key:
            # Simple test to validate API key format
            services_status['openai'] = {
                'status': 'configured',
                'message': 'API key is present'
            }
        else:
            services_status['openai'] = {
                'status': 'warning',
                'message': 'API key not configured'
            }
    except Exception as e:
        services_status['openai'] = {
            'status': 'error',
            'message': str(e)
        }
        overall_status = 'degraded'
    
    # Check Redis connectivity (if configured)
    try:
        redis_url = os.environ.get('REDIS_URL')
        if redis_url and 'memory://' not in redis_url:
            # For production Redis instances
            services_status['redis'] = {
                'status': 'configured',
                'message': 'Redis URL configured'
            }
        else:
            services_status['redis'] = {
                'status': 'memory',
                'message': 'Using in-memory storage'
            }
    except Exception as e:
        services_status['redis'] = {
            'status': 'error', 
            'message': str(e)
        }
        overall_status = 'degraded'
    
    status_code = 200 if overall_status == 'healthy' else 207
    
    return jsonify({
        'status': overall_status,
        'services': services_status,
        'timestamp': datetime.utcnow().isoformat()
    }), status_code

@health_bp.route('/health/detailed', methods=['GET'])
def detailed_health():
    """Detailed health check with system metrics"""
    try:
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Get load averages (Unix only)
        load_avg = None
        try:
            load_avg = os.getloadavg()
        except (OSError, AttributeError):
            # Windows doesn't support getloadavg
            pass
        
        return jsonify({
            'status': 'healthy',
            'system': {
                'cpu_percent': cpu_percent,
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent
                },
                'disk': {
                    'total': disk.total,
                    'free': disk.free,
                    'percent': (disk.used / disk.total) * 100
                },
                'load_average': load_avg
            },
            'application': {
                'uptime': time.time() - psutil.Process().create_time(),
                'region': os.environ.get('AWS_REGION', 'unknown'),
                'environment': os.environ.get('ENVIRONMENT', 'development'),
                'version': '1.0.0'
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        current_app.logger.error(f"Detailed health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@health_bp.route('/health/readiness', methods=['GET'])
def readiness_check():
    """Kubernetes readiness probe endpoint"""
    try:
        # Check if all critical services are ready
        checks = {
            'database': False,
            'configuration': False
        }
        
        # Database readiness
        try:
            from sqlalchemy import text
            from backend.models import db
            db.session.execute(text('SELECT 1'))
            db.session.commit()
            checks['database'] = True
        except:
            pass
        
        # Configuration readiness
        checks['configuration'] = bool(os.environ.get('SECRET_KEY'))
        
        all_ready = all(checks.values())
        
        return jsonify({
            'ready': all_ready,
            'checks': checks,
            'timestamp': datetime.utcnow().isoformat()
        }), 200 if all_ready else 503
    except Exception as e:
        return jsonify({
            'ready': False,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503

@health_bp.route('/health/liveness', methods=['GET'])
def liveness_check():
    """Kubernetes liveness probe endpoint"""
    try:
        # Simple liveness check - if we can respond, we're alive
        return jsonify({
            'alive': True,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'alive': False,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500