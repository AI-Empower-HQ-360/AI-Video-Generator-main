"""
Spiritual Gurus API Module

This module provides RESTful API endpoints for interacting with AI-powered spiritual gurus.
Each guru specializes in different aspects of spiritual development and provides personalized
guidance using OpenAI's GPT models.

Key Features:
    - Multiple specialized spiritual gurus (spiritual, meditation, bhakti, karma, yoga, sloka)
    - Standard and streaming response modes
    - Workflow-based configuration management
    - Context-aware personalized responses
    - Error handling and fallback mechanisms

API Endpoints:
    - GET /gurus - List all available gurus
    - GET /gurus/{guru_type} - Get specific guru information
    - POST /gurus/ask - Ask a guru for guidance (standard response)
    - POST /gurus/ask/stream - Ask a guru for guidance (streaming response)
    - GET /gurus/workflows - Get available AI workflows
    - GET /gurus/workflow/{guru_type}/config - Get workflow configuration

Dependencies:
    - OpenAI API for AI response generation
    - Workflow manager for dynamic configuration
    - Asyncio for asynchronous operations

Author: AI-Empower-HQ-360
License: MIT
"""

from flask import Blueprint, request, jsonify, Response
import openai
import os
import asyncio
import json
from services.ai_service import AIService
from workflow_assignment import ChatGPTWorkflowManager

# Create Flask blueprint for organizing guru-related routes
# Blueprints allow modular organization of routes and can be registered with multiple URL prefixes
gurus_bp = Blueprint('gurus', __name__)

# Initialize AI Service and Workflow Manager with error handling
# These services may fail to initialize if API keys are missing or invalid
try:
    # AI Service handles OpenAI API communication and response generation
    ai_service = AIService()
    # Workflow Manager provides dynamic configuration for different guru types
    workflow_manager = ChatGPTWorkflowManager()
except ValueError as e:
    # Log initialization failure but allow the application to start
    # This enables graceful degradation when AI services are unavailable
    print(f"Warning: AI Service not initialized - {e}")
    ai_service = None
    workflow_manager = None

# Spiritual Gurus Configuration
# This dictionary defines the available AI spiritual gurus, their specializations,
# and the system prompts that shape their personalities and response styles.
# Each guru represents a different aspect of spiritual development and wisdom.
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
        Always maintain a balance of wisdom, practicality, and compassion in your guidance."""
    },
    "spiritual": {
        "name": "🙏 AI Spiritual Guru",
        "specialization": "Soul consciousness and eternal identity",
        "prompt": "You are a wise spiritual teacher focused on soul consciousness and eternal identity..."
    },
    "sloka": {
        "name": "🕉️ AI Sloka Guru", 
        "specialization": "Sanskrit verses and sacred wisdom",
        "prompt": "You are a Sanskrit scholar specializing in ancient verses and their meanings..."
    },
    "meditation": {
        "name": "🧘 AI Meditation Guru",
        "specialization": "Inner peace and mindfulness",
        "prompt": "You are a meditation master teaching inner peace and mindfulness..."
    },
    "bhakti": {
        "name": "💝 AI Bhakti Guru",
        "specialization": "Devotion and divine love", 
        "prompt": "You are a devotion teacher focused on divine love and surrender..."
    },
    "karma": {
        "name": "⚖️ AI Karma Guru",
        "specialization": "Ethics and dharma",
        "prompt": "You are an ethics teacher focused on dharma and right action..."
    },
    "yoga": {
        "name": "🧘‍♀️ AI Yoga Guru",
        "specialization": "Breath and energy alignment",
        "prompt": "You are a yoga master teaching breath, posture, and energy work..."
    }
}

@gurus_bp.route('/', methods=['GET'])
def get_all_gurus():
    """
    Get all available spiritual gurus and their information.
    
    This endpoint provides a complete list of available AI spiritual gurus,
    including their names, specializations, and unique identifiers.
    Used by the frontend to populate guru selection interfaces.
    
    Returns:
        JSON response containing:
        - success: Boolean indicating request success
        - gurus: Dictionary of all available gurus with their details
        - total: Total number of available gurus
        
    Example Response:
        {
            "success": true,
            "gurus": {
                "spiritual": {
                    "name": "🙏 AI Spiritual Guru",
                    "specialization": "Soul consciousness and eternal identity"
                },
                ...
            },
            "total": 7
        }
    """
    return jsonify({
        'success': True,
        'gurus': SPIRITUAL_GURUS,
        'total': len(SPIRITUAL_GURUS)
    })

@gurus_bp.route('/<guru_type>', methods=['GET'])
def get_guru(guru_type):
    """
    Get information about a specific spiritual guru.
    
    Retrieves detailed information about a single guru based on the guru type.
    Used for displaying guru-specific information and validation.
    
    Args:
        guru_type (str): The type/identifier of the guru to retrieve
        
    Returns:
        JSON response with guru information or error if not found
        
    HTTP Status Codes:
        200: Success - guru found and returned
        404: Not Found - guru type doesn't exist
        
    Example:
        GET /api/gurus/spiritual
        Response: {
            "success": true,
            "guru": {
                "name": "🙏 AI Spiritual Guru",
                "specialization": "Soul consciousness and eternal identity"
            }
        }
    """
    if guru_type in SPIRITUAL_GURUS:
        return jsonify({
            'success': True,
            'guru': SPIRITUAL_GURUS[guru_type]
        })
    return jsonify({'success': False, 'error': 'Guru not found'}), 404

@gurus_bp.route('/ask', methods=['POST'])
def ask_guru():
    data = request.get_json()
    guru_type = data.get('guru_type')
    question = data.get('question')
    user_context = data.get('user_context')
    
    if not guru_type or not question:
        return jsonify({'success': False, 'error': 'Missing guru_type or question'}), 400
    
    if guru_type not in SPIRITUAL_GURUS:
        return jsonify({'success': False, 'error': 'Invalid guru type'}), 400
    
    if not ai_service:
        return jsonify({'success': False, 'error': 'AI service not available'}), 503
    
    try:
        # Get AI response using the AI service
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response_data = loop.run_until_complete(
            ai_service.get_spiritual_guidance(guru_type, question, user_context)
        )
        loop.close()
        
        if response_data.get('success'):
            return jsonify({
                'success': True,
                'guru_name': SPIRITUAL_GURUS[guru_type]['name'],
                'guru_type': guru_type,
                'question': question,
                'response': response_data['response'],
                'specialization': SPIRITUAL_GURUS[guru_type]['specialization'],
                'tokens_used': response_data.get('tokens_used'),
                'model': response_data.get('model')
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to get AI response'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@gurus_bp.route('/ask/stream', methods=['POST'])
def ask_guru_stream():
    data = request.get_json()
    guru_type = data.get('guru_type')
    question = data.get('question')
    user_context = data.get('user_context')
    
    if not guru_type or not question:
        return jsonify({'success': False, 'error': 'Missing guru_type or question'}), 400
    
    if guru_type not in SPIRITUAL_GURUS:
        return jsonify({'success': False, 'error': 'Invalid guru type'}), 400
    
    if not ai_service:
        return jsonify({'success': False, 'error': 'AI service not available'}), 503
    
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
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/plain')

# Add new endpoint for spiritual guidance (matching frontend expectations)
@gurus_bp.route('/spiritual/guidance', methods=['POST'])
def spiritual_guidance():
    return ask_guru()

@gurus_bp.route('/spiritual/guidance/stream', methods=['POST'])
def spiritual_guidance_stream():
    return ask_guru_stream()

@gurus_bp.route('/workflows', methods=['GET'])
def get_available_workflows():
    """Get all available AI Guru workflows and their ChatGPT configurations"""
    if not workflow_manager:
        return jsonify({'success': False, 'error': 'Workflow manager not available'}), 503
    
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
def get_workflow_config(guru_type):
    """Get detailed workflow configuration for a specific guru"""
    if not workflow_manager:
        return jsonify({'success': False, 'error': 'Workflow manager not available'}), 503
    
    try:
        config = workflow_manager.assign_chatgpt_to_workflow(guru_type)
        return jsonify({
            'success': True,
            'workflow_config': config
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
