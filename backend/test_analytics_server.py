#!/usr/bin/env python3
"""
Simple test server for analytics functionality
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import sys

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
CORS(app)

# Import just the analytics blueprint
from api.analytics import analytics_bp

# Register the analytics blueprint
app.register_blueprint(analytics_bp, url_prefix='/api/analytics')

@app.route('/')
def serve_index():
    """Serve the main HTML file"""
    return send_from_directory('..', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('..', filename)

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Analytics API is running',
        'endpoints': [
            '/api/analytics/heatmap/<video_id>',
            '/api/analytics/viewer-behavior/<video_id>',
            '/api/analytics/conversion-tracking/<video_id>',
            '/api/analytics/predictive-modeling/<video_id>',
            '/api/analytics/competitor-analysis',
            '/api/analytics/analytics-summary'
        ]
    })

if __name__ == '__main__':
    print("🚀 Starting Analytics API Server...")
    print("📊 Analytics endpoints available at: http://localhost:5000/api/analytics/")
    print("🌐 Web interface available at: http://localhost:5000/")
    print("❤️ Health check: http://localhost:5000/health")
    app.run(debug=True, host='0.0.0.0', port=5000)