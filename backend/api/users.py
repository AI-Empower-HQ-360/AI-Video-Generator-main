from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
import re
from datetime import datetime

# Import security components
from utils.security import (
    InputValidator, SecurityError, validate_request_size, 
    validate_content_type, log_security_event, generate_secure_token
)
from middleware.auth import (
    require_auth, optional_auth, get_current_user, 
    create_user_session, AuthenticationError
)

users_bp = Blueprint('users', __name__)

# In-memory user store for demo (replace with proper database in production)
# This would typically be a proper database model
USER_STORE = {}

# User validation patterns
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{3,30}$')

@users_bp.route('/register', methods=['POST'])
@validate_request_size
@validate_content_type(['application/json'])
def register_user():
    """Register a new user with secure validation"""
    try:
        if not request.is_json:
            return jsonify({'success': False, 'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data provided'}), 400
        
        # Validate JSON payload
        data = InputValidator.validate_json_payload(data)
        
        # Validate required fields
        email = InputValidator.validate_string(
            data.get('email'), 'email', 100, 'email', required=True
        )
        username = InputValidator.validate_string(
            data.get('username'), 'username', 30, 'username', required=True
        )
        password = data.get('password')
        
        if not password:
            return jsonify({'success': False, 'error': 'Password is required'}), 400
        
        # Password strength validation
        if len(password) < 8:
            return jsonify({
                'success': False, 
                'error': 'Password must be at least 8 characters long'
            }), 400
        
        if not re.search(r'[A-Z]', password):
            return jsonify({
                'success': False, 
                'error': 'Password must contain at least one uppercase letter'
            }), 400
        
        if not re.search(r'[a-z]', password):
            return jsonify({
                'success': False, 
                'error': 'Password must contain at least one lowercase letter'
            }), 400
        
        if not re.search(r'\d', password):
            return jsonify({
                'success': False, 
                'error': 'Password must contain at least one number'
            }), 400
        
        # Check if user already exists
        if email in USER_STORE:
            log_security_event('registration_attempt_duplicate_email', {
                'email': email,
                'username': username
            })
            return jsonify({
                'success': False, 
                'error': 'User with this email already exists'
            }), 409
        
        # Check username uniqueness
        for user_data in USER_STORE.values():
            if user_data.get('username') == username:
                log_security_event('registration_attempt_duplicate_username', {
                    'username': username
                })
                return jsonify({
                    'success': False, 
                    'error': 'Username already taken'
                }), 409
        
        # Create user account
        user_id = generate_secure_token()
        password_hash = generate_password_hash(password)
        
        user_data = {
            'user_id': user_id,
            'email': email,
            'username': username,
            'password_hash': password_hash,
            'roles': ['user'],
            'preferences': {},
            'created_at': datetime.utcnow().isoformat(),
            'is_verified': False,
            'login_attempts': 0,
            'last_login': None
        }
        
        USER_STORE[email] = user_data
        
        # Create session tokens
        tokens = create_user_session(user_id, user_data)
        
        log_security_event('user_registered', {
            'user_id': user_id,
            'email': email,
            'username': username
        })
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'user': {
                'user_id': user_id,
                'email': email,
                'username': username,
                'roles': user_data['roles']
            },
            **tokens
        }), 201
        
    except SecurityError as e:
        log_security_event('registration_security_error', {
            'error': str(e),
            'remote_addr': request.remote_addr
        })
        return jsonify({'success': False, 'error': str(e), 'code': 'SECURITY_ERROR'}), 400
    except Exception as e:
        log_security_event('registration_unexpected_error', {
            'error': str(e),
            'remote_addr': request.remote_addr
        })
        return jsonify({'success': False, 'error': 'Registration failed', 'code': 'REGISTRATION_ERROR'}), 500

@users_bp.route('/login', methods=['POST'])
@validate_request_size
@validate_content_type(['application/json'])
def login_user():
    """Authenticate user with secure login"""
    try:
        if not request.is_json:
            return jsonify({'success': False, 'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data provided'}), 400
        
        # Validate JSON payload
        data = InputValidator.validate_json_payload(data)
        
        # Validate credentials
        email = InputValidator.validate_string(
            data.get('email'), 'email', 100, 'email', required=True
        )
        password = data.get('password')
        
        if not password:
            return jsonify({'success': False, 'error': 'Password is required'}), 400
        
        # Check if user exists
        user_data = USER_STORE.get(email)
        if not user_data:
            log_security_event('login_attempt_nonexistent_user', {
                'email': email,
                'remote_addr': request.remote_addr
            })
            return jsonify({
                'success': False, 
                'error': 'Invalid email or password'
            }), 401
        
        # Check for account lockout (basic brute force protection)
        if user_data.get('login_attempts', 0) >= 5:
            log_security_event('login_attempt_locked_account', {
                'email': email,
                'login_attempts': user_data.get('login_attempts', 0)
            })
            return jsonify({
                'success': False, 
                'error': 'Account temporarily locked due to multiple failed login attempts',
                'code': 'ACCOUNT_LOCKED'
            }), 423
        
        # Verify password
        if not check_password_hash(user_data['password_hash'], password):
            # Increment login attempts
            user_data['login_attempts'] = user_data.get('login_attempts', 0) + 1
            USER_STORE[email] = user_data
            
            log_security_event('login_attempt_invalid_password', {
                'email': email,
                'login_attempts': user_data['login_attempts']
            })
            return jsonify({
                'success': False, 
                'error': 'Invalid email or password'
            }), 401
        
        # Reset login attempts on successful login
        user_data['login_attempts'] = 0
        user_data['last_login'] = datetime.utcnow().isoformat()
        USER_STORE[email] = user_data
        
        # Create session tokens
        tokens = create_user_session(user_data['user_id'], user_data)
        
        log_security_event('user_login_success', {
            'user_id': user_data['user_id'],
            'email': email,
            'username': user_data['username']
        })
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'user_id': user_data['user_id'],
                'email': email,
                'username': user_data['username'],
                'roles': user_data['roles']
            },
            **tokens
        })
        
    except SecurityError as e:
        log_security_event('login_security_error', {
            'error': str(e),
            'remote_addr': request.remote_addr
        })
        return jsonify({'success': False, 'error': str(e), 'code': 'SECURITY_ERROR'}), 400
    except Exception as e:
        log_security_event('login_unexpected_error', {
            'error': str(e),
            'remote_addr': request.remote_addr
        })
        return jsonify({'success': False, 'error': 'Login failed', 'code': 'LOGIN_ERROR'}), 500

@users_bp.route('/profile', methods=['GET'])
@validate_request_size
@require_auth
def get_user_profile():
    """Get authenticated user's profile"""
    try:
        current_user = get_current_user()
        user_id = current_user['user_id']
        
        # Find user in store (in production, query database)
        user_data = None
        for email, data in USER_STORE.items():
            if data['user_id'] == user_id:
                user_data = data
                break
        
        if not user_data:
            log_security_event('profile_user_not_found', {
                'user_id': user_id
            })
            return jsonify({
                'success': False, 
                'error': 'User not found'
            }), 404
        
        log_security_event('profile_accessed', {
            'user_id': user_id,
            'email': user_data['email']
        })
        
        # Return safe user information (exclude sensitive data)
        profile_data = {
            'user_id': user_data['user_id'],
            'email': user_data['email'],
            'username': user_data['username'],
            'roles': user_data['roles'],
            'preferences': user_data.get('preferences', {}),
            'created_at': user_data['created_at'],
            'last_login': user_data.get('last_login'),
            'is_verified': user_data.get('is_verified', False)
        }
        
        return jsonify({
            'success': True,
            'profile': profile_data
        })
        
    except Exception as e:
        log_security_event('profile_error', {
            'error': str(e),
            'user_id': current_user['user_id'] if 'current_user' in locals() else None
        })
        return jsonify({'success': False, 'error': 'Failed to get profile'}), 500

@users_bp.route('/preferences', methods=['POST'])
@validate_request_size
@validate_content_type(['application/json'])
@require_auth
def save_user_preferences():
    """Save user preferences with validation"""
    try:
        current_user = get_current_user()
        user_id = current_user['user_id']
        
        if not request.is_json:
            return jsonify({'success': False, 'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data provided'}), 400
        
        # Validate JSON payload
        data = InputValidator.validate_json_payload(data, max_keys=20)
        
        # Validate preferences structure
        preferences = data.get('preferences', {})
        if not isinstance(preferences, dict):
            return jsonify({'success': False, 'error': 'Preferences must be an object'}), 400
        
        # Validate individual preference values
        validated_preferences = {}
        for key, value in preferences.items():
            # Validate key
            key = InputValidator.validate_string(key, f'preference_key_{key}', 50, required=True)
            
            # Validate value (allow strings, numbers, booleans)
            if isinstance(value, str):
                value = InputValidator.validate_string(value, f'preference_value_{key}', 200, required=False)
            elif not isinstance(value, (int, float, bool)):
                return jsonify({
                    'success': False, 
                    'error': f'Invalid value type for preference "{key}"'
                }), 400
            
            validated_preferences[key] = value
        
        # Find and update user
        user_data = None
        user_email = None
        for email, data in USER_STORE.items():
            if data['user_id'] == user_id:
                user_data = data
                user_email = email
                break
        
        if not user_data:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Update preferences
        user_data['preferences'] = validated_preferences
        USER_STORE[user_email] = user_data
        
        log_security_event('preferences_updated', {
            'user_id': user_id,
            'preference_keys': list(validated_preferences.keys())
        })
        
        return jsonify({
            'success': True,
            'message': 'Preferences saved successfully',
            'preferences': validated_preferences
        })
        
    except SecurityError as e:
        log_security_event('preferences_security_error', {
            'error': str(e),
            'user_id': current_user['user_id'] if 'current_user' in locals() else None
        })
        return jsonify({'success': False, 'error': str(e), 'code': 'SECURITY_ERROR'}), 400
    except Exception as e:
        log_security_event('preferences_error', {
            'error': str(e),
            'user_id': current_user['user_id'] if 'current_user' in locals() else None
        })
        return jsonify({'success': False, 'error': 'Failed to save preferences'}), 500

@users_bp.route('/logout', methods=['POST'])
@require_auth
def logout_user():
    """Logout user and invalidate session"""
    try:
        current_user = get_current_user()
        user_id = current_user['user_id']
        
        # In a full implementation, you would:
        # 1. Add the JWT token to a blacklist
        # 2. Update user's last logout time
        # 3. Clear any server-side session data
        
        log_security_event('user_logout', {
            'user_id': user_id
        })
        
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        })
        
    except Exception as e:
        log_security_event('logout_error', {
            'error': str(e),
            'user_id': current_user['user_id'] if 'current_user' in locals() else None
        })
        return jsonify({'success': False, 'error': 'Logout failed'}), 500

@users_bp.route('/change-password', methods=['POST'])
@validate_request_size
@validate_content_type(['application/json'])
@require_auth
def change_password():
    """Change user password with security validation"""
    try:
        current_user = get_current_user()
        user_id = current_user['user_id']
        
        if not request.is_json:
            return jsonify({'success': False, 'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data provided'}), 400
        
        # Validate JSON payload
        data = InputValidator.validate_json_payload(data)
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({
                'success': False, 
                'error': 'Current password and new password are required'
            }), 400
        
        # Find user
        user_data = None
        user_email = None
        for email, data in USER_STORE.items():
            if data['user_id'] == user_id:
                user_data = data
                user_email = email
                break
        
        if not user_data:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Verify current password
        if not check_password_hash(user_data['password_hash'], current_password):
            log_security_event('password_change_invalid_current', {
                'user_id': user_id
            })
            return jsonify({
                'success': False, 
                'error': 'Current password is incorrect'
            }), 401
        
        # Validate new password strength
        if len(new_password) < 8:
            return jsonify({
                'success': False, 
                'error': 'New password must be at least 8 characters long'
            }), 400
        
        if not re.search(r'[A-Z]', new_password):
            return jsonify({
                'success': False, 
                'error': 'New password must contain at least one uppercase letter'
            }), 400
        
        if not re.search(r'[a-z]', new_password):
            return jsonify({
                'success': False, 
                'error': 'New password must contain at least one lowercase letter'
            }), 400
        
        if not re.search(r'\d', new_password):
            return jsonify({
                'success': False, 
                'error': 'New password must contain at least one number'
            }), 400
        
        # Update password
        user_data['password_hash'] = generate_password_hash(new_password)
        USER_STORE[user_email] = user_data
        
        log_security_event('password_changed', {
            'user_id': user_id
        })
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        })
        
    except SecurityError as e:
        log_security_event('password_change_security_error', {
            'error': str(e),
            'user_id': current_user['user_id'] if 'current_user' in locals() else None
        })
        return jsonify({'success': False, 'error': str(e), 'code': 'SECURITY_ERROR'}), 400
    except Exception as e:
        log_security_event('password_change_error', {
            'error': str(e),
            'user_id': current_user['user_id'] if 'current_user' in locals() else None
        })
        return jsonify({'success': False, 'error': 'Password change failed'}), 500
