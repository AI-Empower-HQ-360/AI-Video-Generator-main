"""
Advanced Automation API Integration
Central API endpoints for all automation services
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from flask import Flask, request, jsonify, Blueprint

# Import automation services
from services.video_quality_service import VideoQualityAssessment, assess_single_video, assess_video_batch
from services.content_moderation_service import SpiritualContentModerator, moderate_text_content
from services.thumbnail_generation_service import VideoThumbnailGenerator, generate_video_thumbnail
from services.workflow_automation_service import WorkflowEngine, schedule_video_processing
from services.disaster_recovery_service import DisasterRecoveryManager, create_emergency_backup
from services.performance_testing_service import PerformanceTestingService, run_load_test

# Create automation blueprint
automation_bp = Blueprint('automation', __name__, url_prefix='/api/automation')

# Initialize services
video_quality_service = VideoQualityAssessment()
content_moderation_service = SpiritualContentModerator()
thumbnail_generation_service = VideoThumbnailGenerator()
workflow_engine = WorkflowEngine()
disaster_recovery_manager = DisasterRecoveryManager()
performance_testing_service = PerformanceTestingService()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@automation_bp.route('/health', methods=['GET'])
def automation_health():
    """Health check for automation services"""
    try:
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'services': {
                'video_quality': 'healthy',
                'content_moderation': 'healthy',
                'thumbnail_generation': 'healthy',
                'workflow_automation': 'healthy',
                'disaster_recovery': 'healthy',
                'performance_testing': 'healthy'
            },
            'system_info': {
                'workflow_engine_running': workflow_engine.is_running if hasattr(workflow_engine, 'is_running') else False,
                'dr_monitoring_active': disaster_recovery_manager.is_monitoring if hasattr(disaster_recovery_manager, 'is_monitoring') else False,
                'performance_monitoring_active': performance_testing_service.monitoring_active if hasattr(performance_testing_service, 'monitoring_active') else False
            }
        }
        
        return jsonify(health_status), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Video Quality Assessment Endpoints
@automation_bp.route('/video/quality/assess', methods=['POST'])
def assess_video_quality():
    """Assess quality of a single video"""
    try:
        data = request.get_json()
        
        if not data or 'video_path' not in data:
            return jsonify({'error': 'video_path is required'}), 400
        
        video_path = data['video_path']
        content_type = data.get('content_type', 'spiritual')
        
        if not os.path.exists(video_path):
            return jsonify({'error': 'Video file not found'}), 404
        
        result = video_quality_service.assess_video_quality(video_path, content_type)
        
        return jsonify({
            'success': True,
            'result': result,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Video quality assessment failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@automation_bp.route('/video/quality/batch', methods=['POST'])
def assess_video_batch_quality():
    """Assess quality of multiple videos"""
    try:
        data = request.get_json()
        
        if not data or 'video_directory' not in data:
            return jsonify({'error': 'video_directory is required'}), 400
        
        video_directory = data['video_directory']
        content_type = data.get('content_type', 'spiritual')
        
        if not os.path.isdir(video_directory):
            return jsonify({'error': 'Video directory not found'}), 404
        
        result = video_quality_service.batch_assess_videos(video_directory, content_type)
        
        return jsonify({
            'success': True,
            'result': result,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Batch video quality assessment failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Content Moderation Endpoints
@automation_bp.route('/content/moderate', methods=['POST'])
def moderate_content():
    """Moderate content for spiritual appropriateness"""
    try:
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({'error': 'content is required'}), 400
        
        content = data['content']
        content_type = data.get('content_type', 'text')
        metadata = data.get('metadata', {})
        
        result = content_moderation_service.moderate_content(content, content_type, metadata)
        
        return jsonify({
            'success': True,
            'result': result,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Content moderation failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@automation_bp.route('/content/moderate/batch', methods=['POST'])
def moderate_content_batch():
    """Moderate multiple pieces of content"""
    try:
        data = request.get_json()
        
        if not data or 'content_list' not in data:
            return jsonify({'error': 'content_list is required'}), 400
        
        content_list = data['content_list']
        
        if not isinstance(content_list, list):
            return jsonify({'error': 'content_list must be an array'}), 400
        
        result = content_moderation_service.moderate_batch_content(content_list)
        
        return jsonify({
            'success': True,
            'result': result,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Batch content moderation failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Thumbnail Generation Endpoints
@automation_bp.route('/video/thumbnail/generate', methods=['POST'])
def generate_thumbnail():
    """Generate thumbnail for a video"""
    try:
        data = request.get_json()
        
        if not data or 'video_path' not in data:
            return jsonify({'error': 'video_path is required'}), 400
        
        video_path = data['video_path']
        content_type = data.get('content_type', 'spiritual')
        platform = data.get('platform', 'standard')
        custom_settings = data.get('custom_settings')
        
        if not os.path.exists(video_path):
            return jsonify({'error': 'Video file not found'}), 404
        
        result = thumbnail_generation_service.generate_thumbnail(
            video_path, content_type, platform, custom_settings
        )
        
        return jsonify({
            'success': True,
            'result': result,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Thumbnail generation failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@automation_bp.route('/video/thumbnail/batch', methods=['POST'])
def generate_thumbnails_batch():
    """Generate thumbnails for multiple videos"""
    try:
        data = request.get_json()
        
        if not data or 'video_list' not in data:
            return jsonify({'error': 'video_list is required'}), 400
        
        video_list = data['video_list']
        default_platform = data.get('default_platform', 'standard')
        
        if not isinstance(video_list, list):
            return jsonify({'error': 'video_list must be an array'}), 400
        
        result = thumbnail_generation_service.generate_batch_thumbnails(video_list, default_platform)
        
        return jsonify({
            'success': True,
            'result': result,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Batch thumbnail generation failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Workflow Automation Endpoints
@automation_bp.route('/workflow/create', methods=['POST'])
def create_workflow():
    """Create a new automation workflow"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Workflow configuration is required'}), 400
        
        workflow_id = workflow_engine.create_workflow(data)
        
        return jsonify({
            'success': True,
            'workflow_id': workflow_id,
            'timestamp': datetime.now().isoformat()
        }), 201
        
    except Exception as e:
        logger.error(f"Workflow creation failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@automation_bp.route('/workflow/schedule', methods=['POST'])
def schedule_workflow():
    """Schedule a workflow for execution"""
    try:
        data = request.get_json()
        
        if not data or 'workflow_id' not in data:
            return jsonify({'error': 'workflow_id is required'}), 400
        
        workflow_id = data['workflow_id']
        schedule_time = data.get('schedule_time')
        input_data = data.get('input_data', {})
        
        # Convert schedule_time string to datetime if provided
        if schedule_time:
            schedule_time = datetime.fromisoformat(schedule_time.replace('Z', '+00:00'))
        
        job_id = workflow_engine.schedule_workflow(workflow_id, schedule_time, input_data)
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'timestamp': datetime.now().isoformat()
        }), 201
        
    except Exception as e:
        logger.error(f"Workflow scheduling failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@automation_bp.route('/workflow/status/<workflow_id>', methods=['GET'])
def get_workflow_status(workflow_id):
    """Get status of a workflow"""
    try:
        status = workflow_engine.get_workflow_status(workflow_id)
        
        return jsonify({
            'success': True,
            'status': status,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get workflow status: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@automation_bp.route('/workflow/templates', methods=['GET'])
def get_workflow_templates():
    """Get available workflow templates"""
    try:
        templates = workflow_engine.get_available_templates()
        
        return jsonify({
            'success': True,
            'templates': templates,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get workflow templates: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@automation_bp.route('/workflow/process-video', methods=['POST'])
def process_video_complete():
    """Schedule complete video processing workflow"""
    try:
        data = request.get_json()
        
        if not data or 'video_path' not in data:
            return jsonify({'error': 'video_path is required'}), 400
        
        video_path = data['video_path']
        content_type = data.get('content_type', 'spiritual')
        
        if not os.path.exists(video_path):
            return jsonify({'error': 'Video file not found'}), 404
        
        job_id = schedule_video_processing(video_path, content_type)
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': 'Video processing workflow scheduled',
            'timestamp': datetime.now().isoformat()
        }), 201
        
    except Exception as e:
        logger.error(f"Video processing workflow failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Disaster Recovery Endpoints
@automation_bp.route('/disaster-recovery/backup', methods=['POST'])
def create_backup():
    """Create system backup"""
    try:
        data = request.get_json() or {}
        
        backup_type = data.get('backup_type', 'incremental')
        data_type = data.get('data_type', 'full')
        
        result = disaster_recovery_manager.create_backup(backup_type, data_type)
        
        return jsonify({
            'success': True,
            'result': result,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Backup creation failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@automation_bp.route('/disaster-recovery/restore', methods=['POST'])
def restore_backup():
    """Restore from backup"""
    try:
        data = request.get_json()
        
        if not data or 'backup_id' not in data:
            return jsonify({'error': 'backup_id is required'}), 400
        
        backup_id = data['backup_id']
        restore_type = data.get('restore_type', 'full')
        
        result = disaster_recovery_manager.restore_from_backup(backup_id, restore_type)
        
        return jsonify({
            'success': True,
            'result': result,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Backup restore failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@automation_bp.route('/disaster-recovery/status', methods=['GET'])
def get_system_status():
    """Get comprehensive system status"""
    try:
        status = disaster_recovery_manager.get_system_status()
        
        return jsonify({
            'success': True,
            'status': status,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get system status: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Performance Testing Endpoints
@automation_bp.route('/performance/test', methods=['POST'])
def run_performance_test():
    """Run performance test"""
    try:
        data = request.get_json() or {}
        
        test_type = data.get('test_type', 'load')
        target_endpoint = data.get('target_endpoint')
        custom_config = data.get('custom_config')
        
        result = performance_testing_service.run_performance_test(
            test_type, target_endpoint, custom_config
        )
        
        return jsonify({
            'success': True,
            'result': result,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Performance test failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@automation_bp.route('/performance/baseline', methods=['POST'])
def establish_baseline():
    """Establish performance baseline"""
    try:
        data = request.get_json() or {}
        
        endpoints = data.get('endpoints')
        
        result = performance_testing_service.establish_baseline(endpoints)
        
        return jsonify({
            'success': True,
            'result': result,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Baseline establishment failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@automation_bp.route('/performance/report', methods=['GET'])
def get_performance_report():
    """Get performance report"""
    try:
        days = request.args.get('days', 7, type=int)
        
        result = performance_testing_service.get_performance_report(days)
        
        return jsonify({
            'success': True,
            'result': result,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get performance report: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# System Management Endpoints
@automation_bp.route('/system/start-monitoring', methods=['POST'])
def start_system_monitoring():
    """Start all automation monitoring services"""
    try:
        # Start workflow engine
        if hasattr(workflow_engine, 'start_engine') and not workflow_engine.is_running:
            workflow_engine.start_engine()
        
        # Start disaster recovery monitoring
        if hasattr(disaster_recovery_manager, 'start_monitoring') and not disaster_recovery_manager.is_monitoring:
            disaster_recovery_manager.start_monitoring()
        
        # Start performance monitoring
        if hasattr(performance_testing_service, 'start_continuous_monitoring') and not performance_testing_service.monitoring_active:
            performance_testing_service.start_continuous_monitoring()
        
        return jsonify({
            'success': True,
            'message': 'All monitoring services started',
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to start monitoring: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@automation_bp.route('/system/stop-monitoring', methods=['POST'])
def stop_system_monitoring():
    """Stop all automation monitoring services"""
    try:
        # Stop workflow engine
        if hasattr(workflow_engine, 'stop_engine') and workflow_engine.is_running:
            workflow_engine.stop_engine()
        
        # Stop disaster recovery monitoring
        if hasattr(disaster_recovery_manager, 'stop_monitoring') and disaster_recovery_manager.is_monitoring:
            disaster_recovery_manager.stop_monitoring()
        
        # Stop performance monitoring
        if hasattr(performance_testing_service, 'stop_continuous_monitoring') and performance_testing_service.monitoring_active:
            performance_testing_service.stop_continuous_monitoring()
        
        return jsonify({
            'success': True,
            'message': 'All monitoring services stopped',
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to stop monitoring: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@automation_bp.route('/system/metrics', methods=['GET'])
def get_system_metrics():
    """Get comprehensive system metrics"""
    try:
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'workflow_engine': {},
            'disaster_recovery': {},
            'performance_testing': {}
        }
        
        # Get workflow engine metrics
        if hasattr(workflow_engine, 'get_system_metrics'):
            metrics['workflow_engine'] = workflow_engine.get_system_metrics()
        
        # Get disaster recovery metrics
        if hasattr(disaster_recovery_manager, 'get_system_status'):
            dr_status = disaster_recovery_manager.get_system_status()
            metrics['disaster_recovery'] = {
                'overall_health': dr_status.get('overall_health', 'unknown'),
                'monitoring_active': dr_status.get('monitoring_active', False),
                'backup_status': dr_status.get('backup_status', {}),
                'recent_alerts_count': len(dr_status.get('recent_alerts', []))
            }
        
        # Get performance testing metrics
        if hasattr(performance_testing_service, 'current_metrics'):
            metrics['performance_testing'] = performance_testing_service.current_metrics
        
        return jsonify({
            'success': True,
            'metrics': metrics,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get system metrics: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Error handlers
@automation_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'timestamp': datetime.now().isoformat()
    }), 404

@automation_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 'Method not allowed',
        'timestamp': datetime.now().isoformat()
    }), 405

@automation_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'timestamp': datetime.now().isoformat()
    }), 500

# Initialize automation services when module is loaded
def initialize_automation_services():
    """Initialize all automation services"""
    try:
        logger.info("Initializing automation services...")
        
        # Start workflow engine
        if hasattr(workflow_engine, 'start_engine'):
            workflow_engine.start_engine()
            logger.info("Workflow engine started")
        
        # Start disaster recovery monitoring
        if hasattr(disaster_recovery_manager, 'start_monitoring'):
            disaster_recovery_manager.start_monitoring()
            logger.info("Disaster recovery monitoring started")
        
        logger.info("Automation services initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize automation services: {str(e)}")

# Shutdown handler
def shutdown_automation_services():
    """Shutdown all automation services"""
    try:
        logger.info("Shutting down automation services...")
        
        # Stop workflow engine
        if hasattr(workflow_engine, 'stop_engine'):
            workflow_engine.stop_engine()
        
        # Stop disaster recovery monitoring
        if hasattr(disaster_recovery_manager, 'stop_monitoring'):
            disaster_recovery_manager.stop_monitoring()
        
        # Stop performance monitoring
        if hasattr(performance_testing_service, 'stop_continuous_monitoring'):
            performance_testing_service.stop_continuous_monitoring()
        
        logger.info("Automation services shut down successfully")
        
    except Exception as e:
        logger.error(f"Error shutting down automation services: {str(e)}")

# Register shutdown handler
import atexit
atexit.register(shutdown_automation_services)

# Auto-initialize services
initialize_automation_services()

def create_automation_app():
    """Create Flask app with automation blueprint"""
    app = Flask(__name__)
    app.register_blueprint(automation_bp)
    
    return app

if __name__ == '__main__':
    app = create_automation_app()
    app.run(host='0.0.0.0', port=5001, debug=False)