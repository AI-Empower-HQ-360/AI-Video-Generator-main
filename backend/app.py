"""
AI Empower Heart Spiritual Platform - Main Flask Application

This module serves as the main entry point for the AI-powered spiritual guidance platform.
It provides RESTful APIs for various spiritual gurus, user management, and AI-driven content.

Dependencies:
    - Flask: Web framework for API endpoints
    - Flask-CORS: Cross-Origin Resource Sharing for frontend integration
    - OpenAI: AI service integration for spiritual guidance
    - Various custom services for guru-specific functionality

Environment Variables Required:
    - SECRET_KEY: Flask secret key for session management
    - OPENAI_API_KEY: OpenAI API key for AI services
    - CORS_ORIGINS: Allowed origins for CORS (production)
    - DEBUG: Enable debug mode (development only)

Author: AI-Empower-HQ-360
License: MIT
"""

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS, cross_origin
import os
from datetime import datetime

# Initialize Flask application with template and static file directories
app = Flask(__name__)

# Configure Cross-Origin Resource Sharing (CORS) for frontend integration
# This allows the React frontend to communicate with the Flask backend
CORS(app, resources={
    r"/*": {
        "origins": "*",  # For development - restrict to specific domains in production
        "methods": ["GET", "POST", "OPTIONS"],  # Allowed HTTP methods
        "allow_headers": ["Content-Type", "Authorization"]  # Allowed request headers
    }
})

# Application Configuration
# SECRET_KEY: Used for session management and CSRF protection
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'spiritual-wisdom-key')
# DEBUG: Enable debug mode for development (auto-reloading, detailed error pages)
app.config['DEBUG'] = True

# Import and register API blueprint modules
# These blueprints organize related routes into separate modules for better code organization
from api.gurus import gurus_bp          # Spiritual gurus API endpoints
from api.users import users_bp          # User management API endpoints  
from api.sessions import sessions_bp    # Session management API endpoints
from api.slokas import slokas_bp        # Sanskrit slokas API endpoints
from api.durable_endpoints import durable_bp  # Durable Functions integration
from api.whisper_endpoints import whisper_bp  # Speech-to-text Whisper integration

# Production CORS Configuration for Durable Functions
# This configuration is more restrictive and suitable for production deployment
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://empowerhub360.org",      # Main production domain
            "https://www.empowerhub360.org"   # www subdomain
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Register API blueprints with URL prefixes for organized routing
# Blueprint registration allows modular organization of routes
app.register_blueprint(gurus_bp, url_prefix='/api/gurus')     # Guru-specific endpoints
app.register_blueprint(gurus_bp, url_prefix='/api')          # Direct spiritual guidance access
app.register_blueprint(users_bp, url_prefix='/api/users')    # User management endpoints
app.register_blueprint(sessions_bp, url_prefix='/api/sessions')  # Session handling endpoints
app.register_blueprint(slokas_bp, url_prefix='/api/slokas')  # Sanskrit content endpoints
app.register_blueprint(whisper_bp, url_prefix='/api/whisper')  # Speech processing endpoints
app.register_blueprint(durable_bp)  # Durable Functions (no prefix - has its own routing)

@app.route('/')
def home():
    """
    Main API endpoint providing service information and available features.
    
    This endpoint serves as the primary entry point for API discovery.
    It returns metadata about the service, available gurus, and service status.
    
    Returns:
        JSON response containing:
        - message: Service description
        - version: API version
        - status: Service health status  
        - available_gurus: List of spiritual gurus available
        - timestamp: Current UTC timestamp
        
    Example:
        GET / 
        Response: {
            "message": "AI Empower Heart Spiritual Platform API",
            "version": "1.0.0",
            "status": "active",
            "available_gurus": ["karma", "bhakti", "meditation", "yoga", "spiritual", "sloka"],
            "timestamp": "2024-01-15T10:30:00.000Z"
        }
    """
    return jsonify({
        'message': 'AI Empower Heart Spiritual Platform API',
        'version': '1.0.0',
        'status': 'active',
        'available_gurus': ['karma', 'bhakti', 'meditation', 'yoga', 'spiritual', 'sloka'],
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/health')
def health_check():
    """
    Health check endpoint for monitoring and load balancer integration.
    
    This endpoint is used by monitoring systems, Docker health checks,
    and load balancers to verify service availability.
    
    Returns:
        JSON response with health status information:
        - status: 'healthy' if service is operational
        - service: Service name identifier
        - gurus_available: Boolean indicating if AI gurus are operational
        
    Example:
        GET /health
        Response: {
            "status": "healthy",
            "service": "spiritual-guidance-platform", 
            "gurus_available": true
        }
    """
    return jsonify({
        'status': 'healthy', 
        'service': 'spiritual-guidance-platform',
        'gurus_available': True
    })

@app.route('/ai-gurus/spiritual-guru')
def spiritual_guru_video():
    """
    Render the spiritual guru video interface page.
    
    This endpoint serves the HTML template for the spiritual guru video interface,
    providing an interactive web page for users to engage with AI spiritual guidance.
    
    Returns:
        Rendered HTML template for spiritual guru video interface
        
    Template:
        spiritual_guru_video.html - Main video interface template
    """
    return render_template('spiritual_guru_video.html')

@app.route('/api/test', methods=['GET', 'OPTIONS'])
@cross_origin(origins=['https://empowerhub360.org', 'https://www.empowerhub360.org'])
def test_connection():
    """
    Test endpoint for API connectivity verification.
    
    This endpoint is specifically designed for testing API connectivity
    from the production frontend domains. It includes CORS configuration
    for secure cross-origin requests.
    
    Methods:
        GET: Test API connectivity
        OPTIONS: CORS preflight handling
        
    CORS Origins:
        - https://empowerhub360.org
        - https://www.empowerhub360.org
        
    Returns:
        JSON response confirming successful API connection:
        - status: 'success' if connection is established
        - message: Confirmation message
        - service: Service identifier
        
    Example:
        GET /api/test
        Response: {
            "status": "success",
            "message": "API connection successful",
            "service": "AI Empower Heart API"
        }
    """
    return jsonify({
        'status': 'success',
        'message': 'API connection successful',
        'service': 'AI Empower Heart API'
    })

@app.route('/test', methods=['GET'])
def test():
    """
    Basic test endpoint for backend functionality verification.
    
    Simple endpoint to verify that the Flask backend is running
    and responding to requests. Used for development testing
    and basic connectivity checks.
    
    Returns:
        JSON response with basic status information:
        - status: 'success' if backend is operational
        - message: Simple confirmation message
        
    Example:
        GET /test
        Response: {
            "status": "success",
            "message": "Backend is running!"
        }
    """
    return jsonify({
        'status': 'success',
        'message': 'Backend is running!'
    })

# Application entry point for development server
if __name__ == '__main__':
    """
    Development server entry point.
    
    Starts the Flask development server with the following configuration:
    - host='0.0.0.0': Accept connections from any IP address
    - port=5000: Run on port 5000 (standard Flask port)
    - debug=True: Enable debug mode with auto-reloading and detailed error pages
    
    Note: This should only be used for development. 
    In production, use a WSGI server like Gunicorn or uWSGI.
    
    Environment Variables:
        - FLASK_ENV: Set to 'development' for development mode
        - SECRET_KEY: Flask secret key for session management
        - OPENAI_API_KEY: Required for AI services functionality
    """
    app.run(host='0.0.0.0', port=5000, debug=True)
