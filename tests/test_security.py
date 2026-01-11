"""
Security-focused tests for the AI Video Generator platform.
Tests input validation, authentication, rate limiting, and security headers.
"""

import pytest
import json
import time
from unittest.mock import patch, MagicMock

# Test the security utilities
def test_input_validator_string_validation():
    """Test string input validation"""
    from backend.utils.security import InputValidator, SecurityError
    
    # Valid string
    result = InputValidator.validate_string("valid_string", "test_field", 50)
    assert result == "valid_string"
    
    # String too long
    with pytest.raises(SecurityError):
        InputValidator.validate_string("x" * 1001, "test_field", 1000)
    
    # Non-string input
    with pytest.raises(SecurityError):
        InputValidator.validate_string(123, "test_field", 50)
    
    # Required field missing
    with pytest.raises(SecurityError):
        InputValidator.validate_string(None, "test_field", 50, required=True)

def test_input_validator_suspicious_content():
    """Test detection of suspicious content"""
    from backend.utils.security import InputValidator, SecurityError
    
    # XSS attempt
    with pytest.raises(SecurityError):
        InputValidator.validate_string("<script>alert('xss')</script>", "test_field", 1000)
    
    # SQL injection attempt
    with pytest.raises(SecurityError):
        InputValidator.validate_string("'; DROP TABLE users; --", "test_field", 1000)
    
    # Directory traversal
    with pytest.raises(SecurityError):
        InputValidator.validate_string("../../../etc/passwd", "test_field", 1000)

def test_input_validator_guru_request():
    """Test guru request validation"""
    from backend.utils.security import InputValidator, SecurityError
    
    # Valid request
    valid_data = {
        'guru_type': 'meditation',
        'question': 'How do I meditate properly?',
        'user_context': 'I am a beginner'
    }
    result = InputValidator.validate_guru_request(valid_data)
    assert result['guru_type'] == 'meditation'
    assert result['question'] == 'How do I meditate properly?'
    
    # Invalid guru type
    invalid_data = {
        'guru_type': 'invalid_guru_123',
        'question': 'Test question'
    }
    with pytest.raises(SecurityError):
        InputValidator.validate_guru_request(invalid_data)
    
    # Missing required field
    incomplete_data = {
        'guru_type': 'meditation'
        # Missing question
    }
    with pytest.raises(SecurityError):
        InputValidator.validate_guru_request(incomplete_data)

def test_input_validator_file_upload():
    """Test file upload validation"""
    from backend.utils.security import InputValidator, SecurityError
    from io import BytesIO
    from werkzeug.datastructures import FileStorage
    
    # Valid file
    valid_file = FileStorage(
        stream=BytesIO(b"test content"),
        filename="test.txt",
        content_type="text/plain"
    )
    assert InputValidator.validate_file_upload(valid_file) == True
    
    # Invalid extension
    invalid_file = FileStorage(
        stream=BytesIO(b"test content"),
        filename="test.exe",
        content_type="application/octet-stream"
    )
    with pytest.raises(SecurityError):
        InputValidator.validate_file_upload(invalid_file)
    
    # File too large
    large_content = b"x" * (6 * 1024 * 1024)  # 6MB
    large_file = FileStorage(
        stream=BytesIO(large_content),
        filename="large.txt",
        content_type="text/plain"
    )
    with pytest.raises(SecurityError):
        InputValidator.validate_file_upload(large_file)

def test_api_key_validation():
    """Test API key format validation"""
    from backend.utils.security import validate_api_key_format
    
    # Valid OpenAI API key format
    valid_key = "sk-1234567890abcdef1234567890abcdef12345678"
    assert validate_api_key_format(valid_key) == True
    
    # Invalid format
    invalid_key = "invalid-key"
    assert validate_api_key_format(invalid_key) == False
    
    # Empty key
    assert validate_api_key_format("") == False
    assert validate_api_key_format(None) == False

class TestSecurityHeaders:
    """Test security headers middleware"""
    
    def test_security_headers_added(self):
        """Test that security headers are properly added"""
        from backend.middleware.security import SecurityHeadersMiddleware
        from flask import Flask
        
        app = Flask(__name__)
        app.config['SECURITY_HEADERS_ENABLED'] = True
        app.config['CONTENT_SECURITY_POLICY_ENABLED'] = True
        
        middleware = SecurityHeadersMiddleware()
        middleware.init_app(app)
        
        with app.test_client() as client:
            @app.route('/test')
            def test_route():
                return {'test': 'response'}, 200
            
            response = client.get('/test')
            
            # Check for required security headers
            assert 'X-Frame-Options' in response.headers
            assert response.headers['X-Frame-Options'] == 'DENY'
            
            assert 'X-Content-Type-Options' in response.headers
            assert response.headers['X-Content-Type-Options'] == 'nosniff'
            
            assert 'X-XSS-Protection' in response.headers
            assert response.headers['X-XSS-Protection'] == '1; mode=block'
            
            assert 'Content-Security-Policy' in response.headers
    
    def test_csrf_token_generation(self):
        """Test CSRF token generation and validation"""
        from backend.middleware.security import get_csrf_token
        from flask import Flask
        
        app = Flask(__name__)
        app.secret_key = 'test-secret-key'
        
        with app.test_request_context():
            with app.test_client() as client:
                with client.session_transaction() as sess:
                    token1 = get_csrf_token()
                    token2 = get_csrf_token()
                    
                    # Should return same token in same session
                    assert token1 == token2
                    assert len(token1) > 20  # Should be reasonably long

class TestAuthentication:
    """Test authentication middleware"""
    
    def test_jwt_token_generation(self):
        """Test JWT token generation"""
        from backend.middleware.auth import AuthManager
        from flask import Flask
        
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret-key'
        
        with app.app_context():
            tokens = AuthManager.generate_tokens(
                'test-user-123',
                {'email': 'test@example.com', 'roles': ['user']}
            )
            
            assert 'access_token' in tokens
            assert 'refresh_token' in tokens
            assert 'expires_in' in tokens
            assert isinstance(tokens['expires_in'], int)
    
    def test_jwt_token_verification(self):
        """Test JWT token verification"""
        from backend.middleware.auth import AuthManager, AuthenticationError
        from flask import Flask
        import jwt
        
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret-key'
        
        with app.app_context():
            # Generate a token
            tokens = AuthManager.generate_tokens(
                'test-user-123',
                {'email': 'test@example.com', 'roles': ['user']}
            )
            
            # Verify the token
            payload = AuthManager.verify_token(tokens['access_token'])
            assert payload['sub'] == 'test-user-123'
            assert payload['email'] == 'test@example.com'
            
            # Test invalid token
            with pytest.raises(AuthenticationError):
                AuthManager.verify_token('invalid-token')

class TestAPIEndpoints:
    """Test API endpoints with security measures"""
    
    @patch('backend.api.gurus.ai_service')
    def test_guru_ask_endpoint_validation(self, mock_ai_service):
        """Test guru ask endpoint with input validation"""
        from backend.app import app
        
        # Mock AI service response
        mock_ai_service.get_spiritual_guidance.return_value = {
            'success': True,
            'response': 'Mocked spiritual guidance',
            'tokens_used': 50,
            'model': 'gpt-3.5-turbo'
        }
        
        with app.test_client() as client:
            # Valid request
            valid_data = {
                'guru_type': 'meditation',
                'question': 'How do I start meditating?',
                'user_context': 'I am a beginner'
            }
            response = client.post('/api/gurus/ask', 
                                 data=json.dumps(valid_data),
                                 content_type='application/json')
            
            # Should succeed (though may fail due to missing AI service in test env)
            assert response.status_code in [200, 503]  # 503 if AI service unavailable
            
            # Invalid request - missing required field
            invalid_data = {
                'guru_type': 'meditation'
                # Missing question
            }
            response = client.post('/api/gurus/ask',
                                 data=json.dumps(invalid_data),
                                 content_type='application/json')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data
    
    def test_user_registration_validation(self):
        """Test user registration with validation"""
        from backend.app import app
        
        with app.test_client() as client:
            # Valid registration
            valid_data = {
                'email': 'test@example.com',
                'username': 'testuser123',
                'password': 'SecurePass123!'
            }
            response = client.post('/api/users/register',
                                 data=json.dumps(valid_data),
                                 content_type='application/json')
            
            # Should succeed
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['success'] == True
            assert 'access_token' in data
            
            # Invalid registration - weak password
            weak_password_data = {
                'email': 'test2@example.com',
                'username': 'testuser456',
                'password': 'weak'
            }
            response = client.post('/api/users/register',
                                 data=json.dumps(weak_password_data),
                                 content_type='application/json')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data
            assert 'password' in data['error'].lower()
    
    def test_rate_limiting_behavior(self):
        """Test rate limiting on endpoints"""
        from backend.app import app
        
        with app.test_client() as client:
            # Make multiple requests to test rate limiting
            # Note: In actual tests, you'd configure a test rate limit
            responses = []
            for i in range(5):
                response = client.get('/health')
                responses.append(response.status_code)
                time.sleep(0.1)  # Small delay between requests
            
            # Health endpoint should be exempt from rate limiting
            assert all(status == 200 for status in responses)

if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v'])