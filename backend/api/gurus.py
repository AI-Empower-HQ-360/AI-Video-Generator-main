from flask import Blueprint, request, jsonify, Response, current_app
import openai
import os
import asyncio
import json
from services.ai_service import AIService
from workflow_assignment import ChatGPTWorkflowManager

# Import security components
from utils.security import (
    InputValidator, SecurityError, validate_request_size, 
    validate_content_type, log_security_event
)
from middleware.auth import optional_auth, require_auth, get_current_user

gurus_bp = Blueprint('gurus', __name__)

# Initialize AI Service and Workflow Manager
try:
    ai_service = AIService()
    workflow_manager = ChatGPTWorkflowManager()
except ValueError as e:
    print(f"Warning: AI Service not initialized - {e}")
    ai_service = None
    workflow_manager = None

# Spiritual Gurus Configuration
SPIRITUAL_GURUS = {
    "bojan": {
        "name": "🌟 AI Bojan Guru",
        "specialization": "Transformative spiritual coaching and self-realization",
        "prompt": """You are AI Bojan Guru, a transformative spiritual coach combining ancient wisdom with modern understanding.
        Your approach is direct, practical, and deeply transformative. Guide users to:
        - Discover their true spiritual nature
        - Break through limiting beliefs
        - Access higher states of consciousness
        - Integrate spiritual wisdom into daily life
        Always maintain a balance of wisdom, practicality, and compassion in your guidance.""",
        "authentication_required": False
    },
    "spiritual": {
        "name": "🙏 AI Spiritual Guru",
        "specialization": "Soul consciousness and eternal identity",
        "prompt": "You are a wise spiritual teacher focused on soul consciousness and eternal identity...",
        "authentication_required": False
    },
    "sloka": {
        "name": "🕉️ AI Sloka Guru", 
        "specialization": "Sanskrit verses and sacred wisdom",
        "prompt": "You are a Sanskrit scholar specializing in ancient verses and their meanings...",
        "authentication_required": False
    },
    "meditation": {
        "name": "🧘 AI Meditation Guru",
        "specialization": "Inner peace and mindfulness",
        "prompt": "You are a meditation master teaching inner peace and mindfulness...",
        "authentication_required": False
    },
    "bhakti": {
        "name": "💝 AI Bhakti Guru",
        "specialization": "Devotion and divine love", 
        "prompt": "You are a devotion teacher focused on divine love and surrender...",
        "authentication_required": False
    },
    "karma": {
        "name": "⚖️ AI Karma Guru",
        "specialization": "Ethics and dharma",
        "prompt": "You are an ethics teacher focused on dharma and right action...",
        "authentication_required": False
    },
    "yoga": {
        "name": "🧘‍♀️ AI Yoga Guru",
        "specialization": "Breath and energy alignment",
        "prompt": "You are a yoga master teaching breath, posture, and energy work...",
        "authentication_required": False
    }
}

@gurus_bp.route('/', methods=['GET'])
@validate_request_size
def get_all_gurus():
    """Get all available spiritual gurus"""
    log_security_event('gurus_list_accessed', {
        'user_agent': request.headers.get('User-Agent', ''),
        'total_gurus': len(SPIRITUAL_GURUS)
    })
    
    # Remove sensitive information from public response
    public_gurus = {}
    for guru_id, guru_data in SPIRITUAL_GURUS.items():
        public_gurus[guru_id] = {
            'name': guru_data['name'],
            'specialization': guru_data['specialization'],
            'authentication_required': guru_data.get('authentication_required', False)
        }
    
    return jsonify({
        'success': True,
        'gurus': public_gurus,
        'total': len(public_gurus)
    })

@gurus_bp.route('/<guru_type>', methods=['GET'])
@validate_request_size
def get_guru(guru_type):
    """Get specific guru information"""
    try:
        # Validate guru_type parameter
        guru_type = InputValidator.validate_string(
            guru_type, 'guru_type', 20, 'guru_type', required=True
        )
        
        if guru_type in SPIRITUAL_GURUS:
            log_security_event('guru_info_accessed', {
                'guru_type': guru_type,
                'user_agent': request.headers.get('User-Agent', '')
            })
            
            # Return public information only
            guru_data = SPIRITUAL_GURUS[guru_type]
            public_info = {
                'name': guru_data['name'],
                'specialization': guru_data['specialization'],
                'authentication_required': guru_data.get('authentication_required', False)
            }
            
            return jsonify({
                'success': True,
                'guru': public_info
            })
        
        log_security_event('guru_not_found', {
            'requested_guru': guru_type,
            'available_gurus': list(SPIRITUAL_GURUS.keys())
        })
        return jsonify({'success': False, 'error': 'Guru not found'}), 404
        
    except SecurityError as e:
        log_security_event('invalid_guru_request', {
            'error': str(e),
            'requested_guru': guru_type
        })
        return jsonify({'success': False, 'error': str(e)}), 400

@gurus_bp.route('/ask', methods=['POST'])
@validate_request_size
@validate_content_type(['application/json'])
@optional_auth
def ask_guru():
    """Ask a spiritual guru for guidance with input validation and optional authentication"""
    try:
        # Validate request content type
        if not request.is_json:
            return jsonify({'success': False, 'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data provided'}), 400
        
        # Validate JSON payload structure
        data = InputValidator.validate_json_payload(data)
        
        # Validate and sanitize input data
        validated_data = InputValidator.validate_guru_request(data)
        guru_type = validated_data['guru_type']
        question = validated_data['question']
        user_context = validated_data.get('user_context', '')
        
        if guru_type not in SPIRITUAL_GURUS:
            return jsonify({'success': False, 'error': 'Invalid guru type'}), 400
        
        # Check if authentication is required for this guru
        guru_config = SPIRITUAL_GURUS[guru_type]
        if guru_config.get('authentication_required', False):
            current_user = get_current_user()
            if not current_user:
                return jsonify({
                    'success': False, 
                    'error': 'Authentication required for this guru',
                    'code': 'AUTH_REQUIRED'
                }), 401
        
        if not ai_service:
            return jsonify({'success': False, 'error': 'AI service not available'}), 503
        
        # Apply rate limiting based on user authentication
        current_user = get_current_user()
        rate_limit = current_app.config['API_RATE_LIMITS']['guru_ask']
        
        # Log the spiritual guidance request
        log_security_event('spiritual_guidance_request', {
            'guru_type': guru_type,
            'question_length': len(question),
            'has_context': bool(user_context),
            'authenticated': bool(current_user),
            'user_id': current_user['user_id'] if current_user else None
        })
        
        # Get AI response using the AI service
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response_data = loop.run_until_complete(
            ai_service.get_spiritual_guidance(guru_type, question, user_context)
        )
        loop.close()
        
        if response_data.get('success'):
            log_security_event('spiritual_guidance_success', {
                'guru_type': guru_type,
                'tokens_used': response_data.get('tokens_used'),
                'model': response_data.get('model'),
                'user_id': current_user['user_id'] if current_user else None
            })
            
            return jsonify({
                'success': True,
                'guru_name': guru_config['name'],
                'guru_type': guru_type,
                'question': question,
                'response': response_data['response'],
                'specialization': guru_config['specialization'],
                'tokens_used': response_data.get('tokens_used'),
                'model': response_data.get('model'),
                'timestamp': response_data.get('timestamp')
            })
        else:
            log_security_event('spiritual_guidance_failed', {
                'guru_type': guru_type,
                'error': 'AI service returned failure'
            })
            return jsonify({'success': False, 'error': 'Failed to get AI response'}), 500
            
    except SecurityError as e:
        log_security_event('guru_ask_security_error', {
            'error': str(e),
            'remote_addr': request.remote_addr
        })
        return jsonify({'success': False, 'error': str(e), 'code': 'SECURITY_ERROR'}), 400
    except Exception as e:
        log_security_event('guru_ask_unexpected_error', {
            'error': str(e),
            'guru_type': data.get('guru_type', 'unknown') if 'data' in locals() else 'unknown'
        })
        return jsonify({'success': False, 'error': 'Internal server error', 'code': 'INTERNAL_ERROR'}), 500

@gurus_bp.route('/ask/stream', methods=['POST'])
@validate_request_size
@validate_content_type(['application/json'])
@optional_auth
def ask_guru_stream():
    """Stream spiritual guru guidance with input validation"""
    try:
        if not request.is_json:
            return jsonify({'success': False, 'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data provided'}), 400
        
        # Validate and sanitize input data
        data = InputValidator.validate_json_payload(data)
        validated_data = InputValidator.validate_guru_request(data)
        
        guru_type = validated_data['guru_type']
        question = validated_data['question']
        user_context = validated_data.get('user_context', '')
        
        if guru_type not in SPIRITUAL_GURUS:
            return jsonify({'success': False, 'error': 'Invalid guru type'}), 400
        
        # Check authentication requirements
        guru_config = SPIRITUAL_GURUS[guru_type]
        if guru_config.get('authentication_required', False):
            current_user = get_current_user()
            if not current_user:
                return jsonify({
                    'success': False, 
                    'error': 'Authentication required for this guru',
                    'code': 'AUTH_REQUIRED'
                }), 401
        
        if not ai_service:
            return jsonify({'success': False, 'error': 'AI service not available'}), 503
        
        # Log streaming request
        current_user = get_current_user()
        log_security_event('spiritual_guidance_stream_request', {
            'guru_type': guru_type,
            'question_length': len(question),
            'authenticated': bool(current_user),
            'user_id': current_user['user_id'] if current_user else None
        })
        
        def generate():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                async def stream_response():
                    async for chunk in ai_service.get_spiritual_guidance_stream(
                        guru_type, question, user_context
                    ):
                        yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                    yield "data: [DONE]\n\n"
                
                gen = stream_response()
                while True:
                    try:
                        chunk = loop.run_until_complete(gen.__anext__())
                        yield chunk
                    except StopAsyncIteration:
                        break
                loop.close()
            except Exception as e:
                log_security_event('spiritual_guidance_stream_error', {
                    'error': str(e),
                    'guru_type': guru_type
                })
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return Response(generate(), mimetype='text/plain')
        
    except SecurityError as e:
        log_security_event('guru_stream_security_error', {
            'error': str(e),
            'remote_addr': request.remote_addr
        })
        return jsonify({'success': False, 'error': str(e), 'code': 'SECURITY_ERROR'}), 400
    except Exception as e:
        log_security_event('guru_stream_unexpected_error', {
            'error': str(e)
        })
        return jsonify({'success': False, 'error': 'Internal server error', 'code': 'INTERNAL_ERROR'}), 500

# Add new endpoint for spiritual guidance (matching frontend expectations)
@gurus_bp.route('/spiritual/guidance', methods=['POST'])
def spiritual_guidance():
    return ask_guru()

@gurus_bp.route('/spiritual/guidance/stream', methods=['POST'])
def spiritual_guidance_stream():
    return ask_guru_stream()

@gurus_bp.route('/workflows', methods=['GET'])
@validate_request_size
@require_auth  # Require authentication for workflow information
def get_available_workflows():
    """Get all available AI Guru workflows and their ChatGPT configurations"""
    if not workflow_manager:
        return jsonify({'success': False, 'error': 'Workflow manager not available'}), 503
    
    current_user = get_current_user()
    log_security_event('workflows_accessed', {
        'user_id': current_user['user_id'] if current_user else None
    })
    
    workflows = workflow_manager.get_available_workflows()
    workflow_details = {}
    
    for guru_type in workflows:
        config = workflow_manager.get_workflow_config(guru_type)
        workflow_details[guru_type] = {
            'name': config['name'],
            'model': config['chatgpt_model'],
            'workflow_type': config['workflow_type'],
            'priority': config['priority'],
            'streaming_available': config.get('streaming', False)
        }
    
    return jsonify({
        'success': True,
        'available_workflows': workflow_details,
        'total_workflows': len(workflows)
    })

@gurus_bp.route('/workflow/<guru_type>/config', methods=['GET'])
@validate_request_size
@require_auth  # Require authentication for detailed workflow config
def get_workflow_config(guru_type):
    """Get detailed workflow configuration for a specific guru"""
    try:
        # Validate guru_type parameter
        guru_type = InputValidator.validate_string(
            guru_type, 'guru_type', 20, 'guru_type', required=True
        )
        
        if not workflow_manager:
            return jsonify({'success': False, 'error': 'Workflow manager not available'}), 503
        
        current_user = get_current_user()
        log_security_event('workflow_config_accessed', {
            'guru_type': guru_type,
            'user_id': current_user['user_id'] if current_user else None
        })
        
        config = workflow_manager.assign_chatgpt_to_workflow(guru_type)
        return jsonify({
            'success': True,
            'workflow_config': config
        })
        
    except SecurityError as e:
        log_security_event('workflow_config_security_error', {
            'error': str(e),
            'guru_type': guru_type
        })
        return jsonify({'success': False, 'error': str(e), 'code': 'SECURITY_ERROR'}), 400
    except Exception as e:
        log_security_event('workflow_config_error', {
            'error': str(e),
            'guru_type': guru_type
        })
        return jsonify({'success': False, 'error': str(e)}), 400
