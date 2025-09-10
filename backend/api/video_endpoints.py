"""
Video Processing API Endpoints
==============================

Flask API endpoints for advanced video processing capabilities including:
- Video upload and processing
- Video editing (trim, merge, effects)
- Text-to-speech integration
- Video enhancement and upscaling
- Subtitle generation and translation
- Video analytics and tracking
- Batch processing operations
"""

from flask import Blueprint, request, jsonify, current_app, send_file
from werkzeug.utils import secure_filename
import os
import asyncio
import json
from pathlib import Path
from services.video_service import get_video_service, VoiceOption, VideoQuality
import tempfile
import uuid
import logging

video_bp = Blueprint('video', __name__)

# Configuration
ALLOWED_VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv'}
ALLOWED_AUDIO_EXTENSIONS = {'.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac'}
MAX_VIDEO_SIZE = 500 * 1024 * 1024  # 500MB
MAX_AUDIO_SIZE = 50 * 1024 * 1024   # 50MB

def allowed_video_file(filename):
    """Check if video file extension is allowed"""
    return Path(filename).suffix.lower() in ALLOWED_VIDEO_EXTENSIONS

def allowed_audio_file(filename):
    """Check if audio file extension is allowed"""
    return Path(filename).suffix.lower() in ALLOWED_AUDIO_EXTENSIONS

@video_bp.route('/upload', methods=['POST'])
def upload_video():
    """
    Upload and process a video file
    
    Form data:
    - video_file: Video file to upload
    - metadata: Optional JSON metadata about the video
    """
    try:
        # Check if file is present
        if 'video_file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No video file provided'
            }), 400
        
        file = request.files['video_file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Validate file
        if not allowed_video_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'Unsupported video format. Allowed: {", ".join(ALLOWED_VIDEO_EXTENSIONS)}'
            }), 400
        
        # Get optional metadata
        metadata = {}
        if 'metadata' in request.form:
            try:
                metadata = json.loads(request.form['metadata'])
            except json.JSONDecodeError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid JSON metadata'
                }), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        video_id = str(uuid.uuid4())
        unique_filename = f"{video_id}_{filename}"
        
        video_service = get_video_service()
        upload_path = video_service.video_dir / unique_filename
        file.save(str(upload_path))
        
        try:
            # Check file size
            file_size = os.path.getsize(upload_path)
            if file_size > MAX_VIDEO_SIZE:
                upload_path.unlink()  # Delete the file
                return jsonify({
                    'success': False,
                    'error': f'Video file too large. Maximum size: {MAX_VIDEO_SIZE // (1024*1024)}MB'
                }), 400
            
            # Process video upload
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(
                video_service.process_video_upload(str(upload_path), metadata)
            )
            
            loop.close()
            
            # Add upload info to result
            if result.get('success'):
                result['upload_info'] = {
                    'original_filename': filename,
                    'stored_filename': unique_filename,
                    'upload_path': str(upload_path)
                }
            
            return jsonify(result)
            
        except Exception as e:
            # Clean up file on error
            if upload_path.exists():
                upload_path.unlink()
            raise e
    
    except Exception as e:
        current_app.logger.error(f"Error in video upload: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error during upload',
            'details': str(e)
        }), 500

@video_bp.route('/trim', methods=['POST'])
def trim_video():
    """
    Trim a video to specified time range
    
    JSON payload:
    - video_id: Video ID to trim
    - start_time: Start time in seconds
    - end_time: End time in seconds
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        required_fields = ['video_id', 'start_time', 'end_time']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        video_id = data['video_id']
        start_time = float(data['start_time'])
        end_time = float(data['end_time'])
        
        # Validate time range
        if start_time < 0 or end_time <= start_time:
            return jsonify({
                'success': False,
                'error': 'Invalid time range. start_time must be >= 0 and end_time > start_time'
            }), 400
        
        video_service = get_video_service()
        
        # Run trimming operation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            video_service.trim_video(video_id, start_time, end_time)
        )
        
        loop.close()
        
        return jsonify(result)
    
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid numeric value: {e}'
        }), 400
    except Exception as e:
        current_app.logger.error(f"Error in video trimming: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error during trimming',
            'details': str(e)
        }), 500

@video_bp.route('/merge', methods=['POST'])
def merge_videos():
    """
    Merge multiple videos into a single video
    
    JSON payload:
    - video_ids: Array of video IDs to merge
    - output_name: Optional custom output filename
    """
    try:
        data = request.get_json()
        
        if not data or 'video_ids' not in data:
            return jsonify({
                'success': False,
                'error': 'video_ids array is required'
            }), 400
        
        video_ids = data['video_ids']
        output_name = data.get('output_name')
        
        if not isinstance(video_ids, list) or len(video_ids) < 2:
            return jsonify({
                'success': False,
                'error': 'At least 2 video IDs are required for merging'
            }), 400
        
        video_service = get_video_service()
        
        # Run merging operation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            video_service.merge_videos(video_ids, output_name)
        )
        
        loop.close()
        
        return jsonify(result)
    
    except Exception as e:
        current_app.logger.error(f"Error in video merging: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error during merging',
            'details': str(e)
        }), 500

@video_bp.route('/enhance', methods=['POST'])
def enhance_video():
    """
    Apply AI-powered video enhancement
    
    JSON payload:
    - video_id: Video ID to enhance
    - enhancement_preset: Enhancement preset to apply
    """
    try:
        data = request.get_json()
        
        if not data or 'video_id' not in data:
            return jsonify({
                'success': False,
                'error': 'video_id is required'
            }), 400
        
        video_id = data['video_id']
        enhancement_preset = data.get('enhancement_preset', 'spiritual_ambient')
        
        video_service = get_video_service()
        
        # Validate enhancement preset
        valid_presets = ['spiritual_ambient', 'meditation_calm', 'teaching_clear']
        if enhancement_preset not in valid_presets:
            return jsonify({
                'success': False,
                'error': f'Invalid enhancement preset. Valid options: {", ".join(valid_presets)}'
            }), 400
        
        # Run enhancement operation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            video_service.enhance_video(video_id, enhancement_preset)
        )
        
        loop.close()
        
        return jsonify(result)
    
    except Exception as e:
        current_app.logger.error(f"Error in video enhancement: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error during enhancement',
            'details': str(e)
        }), 500

@video_bp.route('/text-to-speech', methods=['POST'])
def generate_speech():
    """
    Generate speech audio from text
    
    JSON payload:
    - text: Text to convert to speech
    - voice: Voice option to use
    - output_name: Optional custom output filename
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': 'text is required'
            }), 400
        
        text = data['text']
        voice_name = data.get('voice', 'male_calm')
        output_name = data.get('output_name')
        
        # Validate voice option
        try:
            voice = VoiceOption(voice_name)
        except ValueError:
            valid_voices = [v.value for v in VoiceOption]
            return jsonify({
                'success': False,
                'error': f'Invalid voice option. Valid options: {", ".join(valid_voices)}'
            }), 400
        
        # Validate text length
        if len(text) > 5000:
            return jsonify({
                'success': False,
                'error': 'Text too long. Maximum 5000 characters allowed.'
            }), 400
        
        video_service = get_video_service()
        
        # Generate speech
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            video_service.add_text_to_speech(text, voice, output_name)
        )
        
        loop.close()
        
        return jsonify(result)
    
    except Exception as e:
        current_app.logger.error(f"Error in text-to-speech: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error during speech generation',
            'details': str(e)
        }), 500

@video_bp.route('/subtitles/generate', methods=['POST'])
def generate_subtitles():
    """
    Generate subtitles for a video
    
    JSON payload:
    - video_id: Video ID to generate subtitles for
    - language: Language code for subtitles (default: 'en')
    """
    try:
        data = request.get_json()
        
        if not data or 'video_id' not in data:
            return jsonify({
                'success': False,
                'error': 'video_id is required'
            }), 400
        
        video_id = data['video_id']
        language = data.get('language', 'en')
        
        video_service = get_video_service()
        
        # Generate subtitles
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            video_service.generate_subtitles(video_id, language)
        )
        
        loop.close()
        
        return jsonify(result)
    
    except Exception as e:
        current_app.logger.error(f"Error in subtitle generation: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error during subtitle generation',
            'details': str(e)
        }), 500

@video_bp.route('/subtitles/translate', methods=['POST'])
def translate_subtitles():
    """
    Translate existing subtitles to target language
    
    JSON payload:
    - subtitle_file: Name of existing subtitle file
    - target_language: Target language code
    """
    try:
        data = request.get_json()
        
        if not data or 'subtitle_file' not in data or 'target_language' not in data:
            return jsonify({
                'success': False,
                'error': 'subtitle_file and target_language are required'
            }), 400
        
        subtitle_file = data['subtitle_file']
        target_language = data['target_language']
        
        video_service = get_video_service()
        
        # Translate subtitles
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            video_service.translate_subtitles(subtitle_file, target_language)
        )
        
        loop.close()
        
        return jsonify(result)
    
    except Exception as e:
        current_app.logger.error(f"Error in subtitle translation: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error during subtitle translation',
            'details': str(e)
        }), 500

@video_bp.route('/analytics/<video_id>', methods=['GET'])
def get_video_analytics(video_id):
    """
    Get analytics data for a specific video
    
    Parameters:
    - video_id: Video ID to get analytics for
    """
    try:
        video_service = get_video_service()
        
        # Get analytics
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            video_service.get_video_analytics(video_id)
        )
        
        loop.close()
        
        return jsonify(result)
    
    except Exception as e:
        current_app.logger.error(f"Error getting video analytics: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error during analytics retrieval',
            'details': str(e)
        }), 500

@video_bp.route('/batch-process', methods=['POST'])
def batch_process_videos():
    """
    Process multiple videos with batch operations
    
    JSON payload:
    - operations: Array of operations to perform
    Each operation should have:
      - type: Operation type (trim, enhance, subtitles, tts)
      - video_id: Video ID (for video operations)
      - parameters: Operation-specific parameters
    """
    try:
        data = request.get_json()
        
        if not data or 'operations' not in data:
            return jsonify({
                'success': False,
                'error': 'operations array is required'
            }), 400
        
        operations = data['operations']
        
        if not isinstance(operations, list) or len(operations) == 0:
            return jsonify({
                'success': False,
                'error': 'At least one operation is required'
            }), 400
        
        # Validate operations
        valid_operation_types = ['trim', 'enhance', 'subtitles', 'tts', 'merge']
        for i, operation in enumerate(operations):
            if not isinstance(operation, dict):
                return jsonify({
                    'success': False,
                    'error': f'Operation {i+1} must be a JSON object'
                }), 400
            
            if 'type' not in operation:
                return jsonify({
                    'success': False,
                    'error': f'Operation {i+1} missing required field: type'
                }), 400
            
            if operation['type'] not in valid_operation_types:
                return jsonify({
                    'success': False,
                    'error': f'Operation {i+1} has invalid type. Valid types: {", ".join(valid_operation_types)}'
                }), 400
        
        video_service = get_video_service()
        
        # Run batch processing
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            video_service.batch_process_videos(operations)
        )
        
        loop.close()
        
        return jsonify(result)
    
    except Exception as e:
        current_app.logger.error(f"Error in batch processing: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error during batch processing',
            'details': str(e)
        }), 500

@video_bp.route('/voices', methods=['GET'])
def get_available_voices():
    """Get available voice options for text-to-speech"""
    
    video_service = get_video_service()
    
    voices = {}
    for voice_option in VoiceOption:
        voice_config = video_service.tts_voices[voice_option]
        voices[voice_option.value] = {
            'name': voice_config['name'],
            'description': voice_config['description'],
            'language': voice_config['language'],
            'recommended_for': voice_option.value.replace('_', ' ').title()
        }
    
    return jsonify({
        'success': True,
        'voices': voices,
        'total_voices': len(voices)
    })

@video_bp.route('/enhancement-presets', methods=['GET'])
def get_enhancement_presets():
    """Get available video enhancement presets"""
    
    video_service = get_video_service()
    
    presets = {}
    for preset_name, preset_config in video_service.enhancement_presets.items():
        presets[preset_name] = {
            'name': preset_name.replace('_', ' ').title(),
            'description': f"Enhancement preset optimized for {preset_name.replace('_', ' ')} content",
            'settings': preset_config
        }
    
    return jsonify({
        'success': True,
        'presets': presets,
        'total_presets': len(presets)
    })

@video_bp.route('/supported-formats', methods=['GET'])
def get_supported_formats():
    """Get supported video and audio formats"""
    
    video_formats = {}
    for ext in ALLOWED_VIDEO_EXTENSIONS:
        video_formats[ext] = {
            'extension': ext,
            'type': 'video',
            'recommended': ext in ['.mp4', '.mov']
        }
    
    audio_formats = {}
    for ext in ALLOWED_AUDIO_EXTENSIONS:
        audio_formats[ext] = {
            'extension': ext,
            'type': 'audio',
            'recommended': ext in ['.mp3', '.wav']
        }
    
    return jsonify({
        'success': True,
        'video_formats': video_formats,
        'audio_formats': audio_formats,
        'max_video_size_mb': MAX_VIDEO_SIZE // (1024*1024),
        'max_audio_size_mb': MAX_AUDIO_SIZE // (1024*1024),
        'recommendations': [
            'Use MP4 format for best compatibility',
            'Ensure good lighting and clear audio for best processing results',
            'Keep file sizes reasonable for faster processing'
        ]
    })

@video_bp.route('/download/<filename>', methods=['GET'])
def download_processed_file(filename):
    """
    Download a processed video, audio, or subtitle file
    
    Parameters:
    - filename: Name of the file to download
    """
    try:
        video_service = get_video_service()
        file_path = video_service.processed_dir / secure_filename(filename)
        
        if not file_path.exists():
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404
        
        return send_file(
            str(file_path),
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        current_app.logger.error(f"Error downloading file: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error during file download',
            'details': str(e)
        }), 500

@video_bp.route('/health', methods=['GET'])
def video_health_check():
    """Health check for video processing service"""
    
    try:
        video_service = get_video_service()
        
        # Check dependencies
        dependencies = {
            'opencv_available': video_service.__class__.__module__.find('cv2') != -1,
            'moviepy_available': video_service.__class__.__module__.find('moviepy') != -1,
        }
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'service': 'video_processing',
            'dependencies': dependencies,
            'supported_video_formats': list(ALLOWED_VIDEO_EXTENSIONS),
            'supported_audio_formats': list(ALLOWED_AUDIO_EXTENSIONS),
            'max_video_size_mb': MAX_VIDEO_SIZE // (1024*1024),
            'features': {
                'video_editing': dependencies['moviepy_available'],
                'video_enhancement': dependencies['opencv_available'],
                'text_to_speech': True,
                'subtitle_generation': True,
                'batch_processing': True,
                'analytics': True
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e)
        }), 500