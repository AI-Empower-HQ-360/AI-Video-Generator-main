"""
Video Processing API Endpoints
Provides REST API for video processing operations with edge computing support
"""
import os
import tempfile
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
from dataclasses import asdict

from services.video_processor import video_processor
from services.distributed_processor import DistributedProcessor
from api.edge_computing import edge_manager
from config.edge_config import edge_config

video_bp = Blueprint('video', __name__)

# Initialize distributed processor
distributed_processor = DistributedProcessor(edge_manager)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm', 'm4v', 'flv', '3gp'}
UPLOAD_FOLDER = tempfile.gettempdir()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@video_bp.route('/upload', methods=['POST'])
def upload_video():
    """Upload video file for processing"""
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No file provided'
        }), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({
            'success': False,
            'error': 'No file selected'
        }), 400
    
    if not allowed_file(file.filename):
        return jsonify({
            'success': False,
            'error': f'File type not allowed. Supported: {", ".join(ALLOWED_EXTENSIONS)}'
        }), 400
    
    try:
        # Generate unique filename
        file_id = str(uuid.uuid4())
        original_filename = secure_filename(file.filename)
        file_extension = original_filename.rsplit('.', 1)[1].lower()
        filename = f"{file_id}.{file_extension}"
        
        # Save file
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Get file info
        file_size = os.path.getsize(file_path)
        
        return jsonify({
            'success': True,
            'file_id': file_id,
            'filename': filename,
            'original_filename': original_filename,
            'file_path': file_path,
            'file_size': file_size,
            'upload_time': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Upload failed: {str(e)}'
        }), 500


@video_bp.route('/process', methods=['POST'])
def start_video_processing():
    """Start video processing task"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['operation', 'input_file']
    if not all(field in data for field in required_fields):
        return jsonify({
            'success': False,
            'error': f'Missing required fields: {required_fields}'
        }), 400
    
    operation = data['operation']
    input_file = data['input_file']
    parameters = data.get('parameters', {})
    distributed = data.get('distributed', False)
    
    # Validate operation
    valid_operations = ['transcode', 'enhance', 'edit', 'render', 'analyze']
    if operation not in valid_operations:
        return jsonify({
            'success': False,
            'error': f'Invalid operation. Must be one of: {valid_operations}'
        }), 400
    
    # Check if input file exists
    if not os.path.exists(input_file):
        return jsonify({
            'success': False,
            'error': 'Input file not found'
        }), 404
    
    try:
        # Generate output file path
        file_id = str(uuid.uuid4())
        input_filename = os.path.basename(input_file)
        name, ext = os.path.splitext(input_filename)
        output_file = os.path.join(UPLOAD_FOLDER, f"{name}_processed_{file_id}{ext}")
        
        if distributed:
            # Use distributed processing
            import asyncio
            
            async def create_distributed_task():
                if not distributed_processor.session:
                    await distributed_processor.initialize()
                
                task = await distributed_processor.create_distributed_task(
                    operation, input_file, output_file, parameters
                )
                
                # Start processing in background
                asyncio.create_task(distributed_processor.process_distributed_task(task))
                
                return task
            
            # Run async function
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            task = loop.run_until_complete(create_distributed_task())
            loop.close()
            
            return jsonify({
                'success': True,
                'task_id': task.task_id,
                'task_type': 'distributed',
                'operation': operation,
                'status': task.status,
                'input_file': input_file,
                'output_file': output_file,
                'created_at': task.created_at
            })
        else:
            # Use single-node processing
            import asyncio
            
            async def create_single_task():
                task = await video_processor.create_task(
                    operation, input_file, output_file, parameters
                )
                
                # Start processing in background
                asyncio.create_task(video_processor.process_video(task))
                
                return task
            
            # Run async function
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            task = loop.run_until_complete(create_single_task())
            loop.close()
            
            return jsonify({
                'success': True,
                'task_id': task.task_id,
                'task_type': 'single',
                'operation': operation,
                'status': task.status,
                'input_file': input_file,
                'output_file': output_file,
                'created_at': task.created_at,
                'gpu_accelerated': task.gpu_accelerated
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to start processing: {str(e)}'
        }), 500


@video_bp.route('/tasks/<task_id>/status', methods=['GET'])
def get_task_status(task_id):
    """Get status of video processing task"""
    try:
        # Check distributed tasks first
        status = distributed_processor.get_task_status(task_id)
        
        if not status:
            # Check single-node tasks
            status = video_processor.get_task_status(task_id)
        
        if status:
            return jsonify({
                'success': True,
                'task': status
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Task not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get task status: {str(e)}'
        }), 500


@video_bp.route('/tasks/<task_id>/cancel', methods=['POST'])
def cancel_task(task_id):
    """Cancel video processing task"""
    try:
        # Try canceling distributed task first
        cancelled = distributed_processor.cancel_task(task_id)
        
        if not cancelled:
            # Try canceling single-node task
            cancelled = video_processor.cancel_task(task_id)
        
        if cancelled:
            return jsonify({
                'success': True,
                'message': f'Task {task_id} cancelled successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Task not found or cannot be cancelled'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to cancel task: {str(e)}'
        }), 500


@video_bp.route('/tasks', methods=['GET'])
def list_tasks():
    """List all active video processing tasks"""
    try:
        tasks = []
        
        # Get distributed tasks
        for task_id, task in distributed_processor.active_tasks.items():
            task_data = asdict(task)
            task_data['task_type'] = 'distributed'
            tasks.append(task_data)
        
        # Get single-node tasks
        for task_id, task in video_processor.active_tasks.items():
            task_data = asdict(task)
            task_data['task_type'] = 'single'
            tasks.append(task_data)
        
        # Sort by creation time
        tasks.sort(key=lambda t: t['created_at'], reverse=True)
        
        return jsonify({
            'success': True,
            'tasks': tasks,
            'total': len(tasks)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to list tasks: {str(e)}'
        }), 500


@video_bp.route('/download/<task_id>', methods=['GET'])
def download_result(task_id):
    """Download processed video file"""
    try:
        # Get task status
        status = distributed_processor.get_task_status(task_id)
        if not status:
            status = video_processor.get_task_status(task_id)
        
        if not status:
            return jsonify({
                'success': False,
                'error': 'Task not found'
            }), 404
        
        if status['status'] != 'completed':
            return jsonify({
                'success': False,
                'error': f'Task not completed. Current status: {status["status"]}'
            }), 400
        
        output_file = status['output_file']
        
        if not os.path.exists(output_file):
            return jsonify({
                'success': False,
                'error': 'Output file not found'
            }), 404
        
        return send_file(
            output_file,
            as_attachment=True,
            download_name=f"processed_{task_id}.mp4"
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Download failed: {str(e)}'
        }), 500


@video_bp.route('/presets', methods=['GET'])
def get_processing_presets():
    """Get available processing presets"""
    presets = {
        'transcode': {
            'web_optimized': {
                'description': 'Optimized for web streaming',
                'parameters': {
                    'codec': 'h264',
                    'quality': 'medium',
                    'resolution': '1920x1080',
                    'fps': 30
                }
            },
            'mobile_optimized': {
                'description': 'Optimized for mobile devices',
                'parameters': {
                    'codec': 'h264',
                    'quality': 'low',
                    'resolution': '1280x720',
                    'fps': 24
                }
            },
            'high_quality': {
                'description': 'High quality output',
                'parameters': {
                    'codec': 'h265',
                    'quality': 'high',
                    'resolution': '3840x2160',
                    'fps': 60
                }
            }
        },
        'enhance': {
            'basic_enhancement': {
                'description': 'Basic video enhancement',
                'parameters': {
                    'denoise': True,
                    'sharpen': True,
                    'brightness': 0.1,
                    'contrast': 1.1
                }
            },
            'color_correction': {
                'description': 'Color correction and saturation',
                'parameters': {
                    'brightness': 0.0,
                    'contrast': 1.2,
                    'saturation': 1.1
                }
            }
        },
        'edit': {
            'trim_start': {
                'description': 'Remove first 10 seconds',
                'parameters': {
                    'trim': {
                        'start': 10
                    }
                }
            },
            'trim_duration': {
                'description': 'Keep only first 60 seconds',
                'parameters': {
                    'trim': {
                        'start': 0,
                        'duration': 60
                    }
                }
            }
        }
    }
    
    return jsonify({
        'success': True,
        'presets': presets
    })


@video_bp.route('/formats', methods=['GET'])
def get_supported_formats():
    """Get supported video formats and codecs"""
    config = edge_config.get_video_processing_config()
    
    formats_info = {
        'input_formats': list(ALLOWED_EXTENSIONS),
        'output_formats': config['supported_formats'],
        'codecs': ['h264', 'h265', 'vp8', 'vp9'],
        'max_resolution': config['max_resolution'],
        'max_duration': config['max_duration'],
        'gpu_acceleration_available': config['gpu_acceleration'],
        'processing_qualities': list(config['processing_quality'].keys())
    }
    
    return jsonify({
        'success': True,
        'formats': formats_info
    })


@video_bp.route('/gpu/status', methods=['GET'])
def get_gpu_status():
    """Get GPU acceleration status"""
    gpu_info = {
        'gpu_available': video_processor.gpu_accelerator.gpu_available,
        'gpu_devices': video_processor.gpu_accelerator.gpu_devices,
        'acceleration_enabled': edge_config.enable_gpu_acceleration
    }
    
    return jsonify({
        'success': True,
        'gpu_status': gpu_info
    })


@video_bp.route('/cleanup', methods=['POST'])
def cleanup_completed_tasks():
    """Clean up completed tasks and temporary files"""
    try:
        # Clean up video processor tasks
        video_processor.cleanup_completed_tasks()
        
        # Clean up distributed processor tasks
        max_age_hours = request.json.get('max_age_hours', 24) if request.json else 24
        
        # Simple cleanup for distributed tasks
        import time
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        to_remove = []
        for task_id, task in distributed_processor.active_tasks.items():
            if task.status in ['completed', 'failed', 'cancelled']:
                if task.completed_at and (current_time - task.completed_at) > max_age_seconds:
                    to_remove.append(task_id)
        
        for task_id in to_remove:
            del distributed_processor.active_tasks[task_id]
        
        return jsonify({
            'success': True,
            'message': f'Cleaned up {len(to_remove)} old tasks',
            'tasks_removed': len(to_remove)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Cleanup failed: {str(e)}'
        }), 500