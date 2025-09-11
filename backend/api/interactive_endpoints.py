"""
Interactive Video API Endpoints
Handles backend functionality for interactive video features
"""

from flask import Blueprint, request, jsonify, session
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
import json
import uuid
from datetime import datetime, timedelta
import os

# Create Blueprint for interactive video endpoints
interactive_bp = Blueprint('interactive', __name__)

# In-memory storage (in production, use a database)
user_progress = {}
achievements_data = {}
live_sessions = {}
chat_messages = {}
branching_data = {}
hotspot_data = {}
leaderboards = {}

# Initialize SocketIO (will be bound to app in main.py)
socketio = None

def init_socketio(app):
    global socketio
    socketio = SocketIO(app, cors_allowed_origins="*")
    setup_socketio_events()

def setup_socketio_events():
    """Setup Socket.IO event handlers for real-time features"""
    
    @socketio.on('connect')
    def handle_connect():
        print(f'Client connected: {request.sid}')
        emit('connection_status', {'status': 'connected'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        print(f'Client disconnected: {request.sid}')
        # Remove from any live sessions
        for session_id, session_data in live_sessions.items():
            if request.sid in session_data.get('viewers', []):
                session_data['viewers'].remove(request.sid)
                emit('viewer_count_update', len(session_data['viewers']), room=session_id)
    
    @socketio.on('join_stream')
    def handle_join_stream(data):
        session_id = data.get('session_id', 'default')
        user_id = data.get('userId', str(uuid.uuid4()))
        
        join_room(session_id)
        
        if session_id not in live_sessions:
            live_sessions[session_id] = {
                'viewers': [],
                'is_live': False,
                'stream_url': None,
                'created_at': datetime.utcnow()
            }
        
        if request.sid not in live_sessions[session_id]['viewers']:
            live_sessions[session_id]['viewers'].append(request.sid)
        
        # Send viewer count update to all in room
        viewer_count = len(live_sessions[session_id]['viewers'])
        emit('viewer_count_update', viewer_count, room=session_id)
        
        # Send current stream status
        emit('stream_status', {
            'isLive': live_sessions[session_id]['is_live'],
            'streamUrl': live_sessions[session_id]['stream_url']
        })
    
    @socketio.on('chat_message')
    def handle_chat_message(data):
        session_id = data.get('session_id', 'default')
        message = {
            'id': data.get('id', str(uuid.uuid4())),
            'userId': data.get('userId'),
            'username': data.get('username'),
            'message': data.get('message'),
            'timestamp': datetime.utcnow().isoformat(),
            'type': data.get('type', 'user')
        }
        
        # Store message
        if session_id not in chat_messages:
            chat_messages[session_id] = []
        chat_messages[session_id].append(message)
        
        # Limit message history
        if len(chat_messages[session_id]) > 100:
            chat_messages[session_id] = chat_messages[session_id][-100:]
        
        # Broadcast to all in room
        emit('chat_message', message, room=session_id)
    
    @socketio.on('interactive_event')
    def handle_interactive_event(data):
        session_id = data.get('session_id', 'default')
        event_type = data.get('type')
        event_data = data.get('data')
        
        # Broadcast interactive event to all viewers
        emit('interactive_event', {
            'type': event_type,
            'data': event_data
        }, room=session_id)
    
    @socketio.on('poll_vote')
    def handle_poll_vote(data):
        poll_id = data.get('pollId')
        option_index = data.get('optionIndex')
        user_id = data.get('userId')
        
        # Store poll vote (implement poll result tracking)
        emit('poll_result_update', {
            'pollId': poll_id,
            'optionIndex': option_index
        }, broadcast=True)

# User Progress and Achievements API
@interactive_bp.route('/api/interactive/progress/<user_id>', methods=['GET'])
def get_user_progress(user_id):
    """Get user's progress and achievements"""
    try:
        progress = user_progress.get(user_id, {
            'achievements': [],
            'decisions': [],
            'completedScenes': [],
            'interactions': [],
            'totalWatchTime': 0,
            'level': 1,
            'experience': 0
        })
        return jsonify({'success': True, 'progress': progress})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@interactive_bp.route('/api/interactive/progress/<user_id>', methods=['POST'])
def update_user_progress(user_id):
    """Update user's progress"""
    try:
        data = request.get_json()
        
        if user_id not in user_progress:
            user_progress[user_id] = {
                'achievements': [],
                'decisions': [],
                'completedScenes': [],
                'interactions': [],
                'totalWatchTime': 0,
                'level': 1,
                'experience': 0
            }
        
        # Update progress data
        progress = user_progress[user_id]
        progress.update(data)
        
        # Check for new achievements
        new_achievements = check_achievements(user_id, progress)
        
        return jsonify({
            'success': True, 
            'progress': progress,
            'newAchievements': new_achievements
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@interactive_bp.route('/api/interactive/achievements', methods=['GET'])
def get_all_achievements():
    """Get all available achievements"""
    achievements = [
        {
            'id': 'first_interaction',
            'name': 'First Steps',
            'description': 'Made your first interaction',
            'icon': '🌟',
            'points': 10
        },
        {
            'id': 'decision_maker',
            'name': 'Decision Maker',
            'description': 'Made 5 decisions',
            'icon': '🎯',
            'points': 25
        },
        {
            'id': 'explorer',
            'name': 'Explorer',
            'description': 'Found all hotspots in a scene',
            'icon': '🔍',
            'points': 50
        },
        {
            'id': 'wisdom_seeker',
            'name': 'Wisdom Seeker',
            'description': 'Completed spiritual journey',
            'icon': '🧘',
            'points': 100
        },
        {
            'id': 'meditation_master',
            'name': 'Meditation Master',
            'description': 'Completed 10 meditation sessions',
            'icon': '🕉️',
            'points': 75
        },
        {
            'id': 'social_butterfly',
            'name': 'Social Butterfly',
            'description': 'Participated in live chat 20 times',
            'icon': '💬',
            'points': 30
        },
        {
            'id': 'vr_pioneer',
            'name': 'VR Pioneer',
            'description': 'Used VR mode for the first time',
            'icon': '🥽',
            'points': 40
        },
        {
            'id': 'voice_commander',
            'name': 'Voice Commander',
            'description': 'Used voice commands 15 times',
            'icon': '🎤',
            'points': 35
        }
    ]
    return jsonify({'success': True, 'achievements': achievements})

def check_achievements(user_id, progress):
    """Check and award new achievements"""
    new_achievements = []
    
    # Achievement logic
    achievements_logic = {
        'first_interaction': lambda p: len(p.get('interactions', [])) >= 1,
        'decision_maker': lambda p: len(p.get('decisions', [])) >= 5,
        'explorer': lambda p: count_hotspot_interactions(p) >= 3,
        'wisdom_seeker': lambda p: len(p.get('completedScenes', [])) >= 5,
        'meditation_master': lambda p: count_meditation_sessions(p) >= 10,
        'social_butterfly': lambda p: count_chat_messages(user_id) >= 20,
        'vr_pioneer': lambda p: has_used_vr(p),
        'voice_commander': lambda p: count_voice_commands(p) >= 15
    }
    
    current_achievements = set(progress.get('achievements', []))
    
    for achievement_id, check_func in achievements_logic.items():
        if achievement_id not in current_achievements and check_func(progress):
            progress['achievements'].append(achievement_id)
            new_achievements.append(achievement_id)
            
            # Award experience points
            progress['experience'] += get_achievement_points(achievement_id)
            
            # Level up logic
            new_level = calculate_level(progress['experience'])
            if new_level > progress.get('level', 1):
                progress['level'] = new_level
    
    return new_achievements

def count_hotspot_interactions(progress):
    """Count hotspot interactions"""
    interactions = progress.get('interactions', [])
    return len([i for i in interactions if i.get('type') == 'hotspot_click'])

def count_meditation_sessions(progress):
    """Count meditation sessions"""
    interactions = progress.get('interactions', [])
    return len([i for i in interactions if i.get('type') == 'meditation_started'])

def count_chat_messages(user_id):
    """Count chat messages for user"""
    total = 0
    for session_messages in chat_messages.values():
        total += len([m for m in session_messages if m.get('userId') == user_id])
    return total

def has_used_vr(progress):
    """Check if user has used VR"""
    interactions = progress.get('interactions', [])
    return any(i.get('type') == 'vr_mode_entered' for i in interactions)

def count_voice_commands(progress):
    """Count voice commands used"""
    interactions = progress.get('interactions', [])
    return len([i for i in interactions if i.get('type') == 'voice_command'])

def get_achievement_points(achievement_id):
    """Get points for achievement"""
    points_map = {
        'first_interaction': 10,
        'decision_maker': 25,
        'explorer': 50,
        'wisdom_seeker': 100,
        'meditation_master': 75,
        'social_butterfly': 30,
        'vr_pioneer': 40,
        'voice_commander': 35
    }
    return points_map.get(achievement_id, 10)

def calculate_level(experience):
    """Calculate level based on experience"""
    # Simple level calculation: level = sqrt(experience / 100)
    import math
    return int(math.sqrt(experience / 100)) + 1

# Branching Video API
@interactive_bp.route('/api/interactive/branching/<scene_id>', methods=['GET'])
def get_branching_data(scene_id):
    """Get branching data for a scene"""
    try:
        scene_data = branching_data.get(scene_id, {
            'branches': [],
            'hotspots': [],
            'metadata': {}
        })
        return jsonify({'success': True, 'data': scene_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@interactive_bp.route('/api/interactive/branching/<scene_id>', methods=['POST'])
def update_branching_data(scene_id):
    """Update branching data for a scene"""
    try:
        data = request.get_json()
        branching_data[scene_id] = data
        return jsonify({'success': True, 'message': 'Branching data updated'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Hotspot Management API
@interactive_bp.route('/api/interactive/hotspots/<scene_id>', methods=['GET'])
def get_hotspots(scene_id):
    """Get hotspots for a scene"""
    try:
        hotspots = hotspot_data.get(scene_id, [])
        return jsonify({'success': True, 'hotspots': hotspots})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@interactive_bp.route('/api/interactive/hotspots/<scene_id>', methods=['POST'])
def add_hotspot(scene_id):
    """Add a hotspot to a scene"""
    try:
        data = request.get_json()
        
        if scene_id not in hotspot_data:
            hotspot_data[scene_id] = []
        
        hotspot = {
            'id': str(uuid.uuid4()),
            'timeStart': data.get('timeStart'),
            'timeEnd': data.get('timeEnd'),
            'x': data.get('x'),
            'y': data.get('y'),
            'content': data.get('content'),
            'action': data.get('action'),
            'created_at': datetime.utcnow().isoformat()
        }
        
        hotspot_data[scene_id].append(hotspot)
        
        return jsonify({'success': True, 'hotspot': hotspot})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Live Streaming API
@interactive_bp.route('/api/interactive/live/start', methods=['POST'])
def start_live_stream():
    """Start a live streaming session"""
    try:
        data = request.get_json()
        session_id = data.get('session_id', str(uuid.uuid4()))
        stream_url = data.get('stream_url')
        
        live_sessions[session_id] = {
            'viewers': [],
            'is_live': True,
            'stream_url': stream_url,
            'created_at': datetime.utcnow(),
            'instructor': data.get('instructor', 'Anonymous')
        }
        
        # Notify all viewers
        if socketio:
            socketio.emit('stream_status', {
                'isLive': True,
                'streamUrl': stream_url,
                'sessionId': session_id
            }, room=session_id)
        
        return jsonify({'success': True, 'session_id': session_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@interactive_bp.route('/api/interactive/live/stop/<session_id>', methods=['POST'])
def stop_live_stream(session_id):
    """Stop a live streaming session"""
    try:
        if session_id in live_sessions:
            live_sessions[session_id]['is_live'] = False
            
            # Notify all viewers
            if socketio:
                socketio.emit('stream_status', {
                    'isLive': False,
                    'streamUrl': None
                }, room=session_id)
        
        return jsonify({'success': True, 'message': 'Stream stopped'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Leaderboard API
@interactive_bp.route('/api/interactive/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get the global leaderboard"""
    try:
        # Calculate leaderboard from user progress
        leaderboard = []
        for user_id, progress in user_progress.items():
            leaderboard.append({
                'userId': user_id,
                'username': f"User_{user_id[:8]}",  # In production, get actual usernames
                'level': progress.get('level', 1),
                'experience': progress.get('experience', 0),
                'achievements': len(progress.get('achievements', [])),
                'completedScenes': len(progress.get('completedScenes', []))
            })
        
        # Sort by experience points
        leaderboard.sort(key=lambda x: x['experience'], reverse=True)
        
        return jsonify({'success': True, 'leaderboard': leaderboard[:50]})  # Top 50
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Analytics API
@interactive_bp.route('/api/interactive/analytics', methods=['GET'])
def get_analytics():
    """Get interaction analytics"""
    try:
        analytics = {
            'totalUsers': len(user_progress),
            'totalInteractions': sum(len(p.get('interactions', [])) for p in user_progress.values()),
            'averageLevel': sum(p.get('level', 1) for p in user_progress.values()) / len(user_progress) if user_progress else 0,
            'mostPopularScene': get_most_popular_scene(),
            'achievementStats': get_achievement_stats(),
            'liveSessionStats': {
                'activeSessions': len([s for s in live_sessions.values() if s['is_live']]),
                'totalViewers': sum(len(s['viewers']) for s in live_sessions.values())
            }
        }
        
        return jsonify({'success': True, 'analytics': analytics})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def get_most_popular_scene():
    """Get the most popular scene based on completion"""
    scene_counts = {}
    for progress in user_progress.values():
        for scene in progress.get('completedScenes', []):
            scene_counts[scene] = scene_counts.get(scene, 0) + 1
    
    if scene_counts:
        return max(scene_counts.items(), key=lambda x: x[1])[0]
    return None

def get_achievement_stats():
    """Get achievement statistics"""
    achievement_counts = {}
    for progress in user_progress.values():
        for achievement in progress.get('achievements', []):
            achievement_counts[achievement] = achievement_counts.get(achievement, 0) + 1
    
    return achievement_counts

# VR/AR Content API
@interactive_bp.route('/api/interactive/vr-content', methods=['GET'])
def get_vr_content():
    """Get VR-specific content and environments"""
    vr_content = {
        'environments': [
            {
                'id': 'meditation_garden',
                'name': 'Meditation Garden',
                'description': 'Peaceful garden environment for meditation',
                'assets': {
                    'skybox': '/static/vr/meditation-garden-skybox.jpg',
                    'sounds': '/static/vr/nature-sounds.mp3'
                }
            },
            {
                'id': 'wisdom_temple',
                'name': 'Wisdom Temple',
                'description': 'Ancient temple for wisdom teachings',
                'assets': {
                    'skybox': '/static/vr/temple-skybox.jpg',
                    'sounds': '/static/vr/temple-ambience.mp3'
                }
            }
        ],
        'interactions': [
            {
                'type': 'floating_orb',
                'position': [2, 2, -5],
                'action': 'show_wisdom_quote'
            },
            {
                'type': 'meditation_bell',
                'position': [0, 1, -3],
                'action': 'start_meditation'
            }
        ]
    }
    
    return jsonify({'success': True, 'content': vr_content})

@interactive_bp.route('/api/interactive/ar-markers', methods=['GET'])
def get_ar_markers():
    """Get AR marker data"""
    ar_markers = {
        'markers': [
            {
                'id': 'spiritual_symbol',
                'pattern': '/static/ar/spiritual-pattern.patt',
                'content': {
                    'video': '/static/videos/spiritual-guidance.mp4',
                    'text': 'Om Mani Padme Hum',
                    'interactions': ['meditation_start', 'wisdom_quote']
                }
            }
        ]
    }
    
    return jsonify({'success': True, 'markers': ar_markers})

# Voice Commands API
@interactive_bp.route('/api/interactive/voice-commands', methods=['GET'])
def get_voice_commands():
    """Get available voice commands"""
    commands = {
        'video_controls': [
            'play', 'pause', 'stop', 'restart', 'mute', 'unmute',
            'volume up', 'volume down'
        ],
        'navigation': [
            'next scene', 'previous scene', 'go to meditation',
            'go to wisdom', 'go to practice'
        ],
        'spiritual': [
            'start meditation', 'end meditation', 'wisdom quote',
            'breathing exercise'
        ],
        'immersive': [
            'enter vr', 'enter ar', 'theater mode', '360 mode'
        ],
        'interactive': [
            'show achievements', 'show chat', 'show hotspots'
        ],
        'system': [
            'help', 'commands', 'stop listening'
        ]
    }
    
    return jsonify({'success': True, 'commands': commands})

# Content Management API
@interactive_bp.route('/api/interactive/content/<content_type>', methods=['GET'])
def get_interactive_content(content_type):
    """Get interactive content by type"""
    try:
        content_data = load_content_data(content_type)
        return jsonify({'success': True, 'content': content_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def load_content_data(content_type):
    """Load content data from files or database"""
    # This would typically load from a database or content management system
    content_map = {
        'meditation': {
            'videos': [
                {
                    'id': 'guided_meditation_1',
                    'title': 'Basic Mindfulness Meditation',
                    'duration': 600,
                    'url': '/static/videos/meditation/basic-mindfulness.mp4',
                    'hotspots': [
                        {'time': 60, 'x': 50, 'y': 30, 'content': 'Focus on your breath'},
                        {'time': 300, 'x': 70, 'y': 50, 'content': 'Let thoughts pass by'}
                    ]
                }
            ]
        },
        'wisdom': {
            'videos': [
                {
                    'id': 'wisdom_talk_1',
                    'title': 'The Path to Inner Peace',
                    'duration': 900,
                    'url': '/static/videos/wisdom/inner-peace.mp4',
                    'branches': [
                        {
                            'time': 450,
                            'question': 'What brings you the most peace?',
                            'options': [
                                {'text': 'Nature', 'nextScene': 'nature_wisdom'},
                                {'text': 'Meditation', 'nextScene': 'meditation_wisdom'},
                                {'text': 'Helping others', 'nextScene': 'service_wisdom'}
                            ]
                        }
                    ]
                }
            ]
        }
    }
    
    return content_map.get(content_type, {})

# Error handlers
@interactive_bp.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@interactive_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500