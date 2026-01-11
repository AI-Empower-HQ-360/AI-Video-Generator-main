"""
Zapier integration for workflow automation.
Provides triggers and actions for Zapier platform integration.
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
try:
    from flask import current_app
except ImportError:
    # Mock current_app when Flask is not available
    class MockApp:
        class Logger:
            def error(self, msg): print(f"ERROR: {msg}")
            def info(self, msg): print(f"INFO: {msg}")
        logger = Logger()
    current_app = MockApp()


class ZapierIntegration:
    """Handles Zapier webhook triggers and REST hooks."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://hooks.zapier.com/hooks/catch"
        self.subscriptions = {}
    
    def register_trigger(self, event: str, hook_url: str) -> str:
        """Register a Zapier trigger webhook."""
        trigger_id = f"zapier_{event}_{datetime.utcnow().timestamp()}"
        
        self.subscriptions[trigger_id] = {
            'event': event,
            'hook_url': hook_url,
            'created_at': datetime.utcnow().isoformat(),
            'active': True
        }
        
        return trigger_id
    
    def trigger_event(self, event: str, data: Dict[str, Any]) -> None:
        """Send data to Zapier triggers for specific event."""
        for trigger_id, subscription in self.subscriptions.items():
            if subscription['active'] and subscription['event'] == event:
                self._send_to_zapier(subscription['hook_url'], data)
    
    def _send_to_zapier(self, hook_url: str, data: Dict[str, Any]) -> None:
        """Send data to Zapier webhook."""
        try:
            # Format data for Zapier
            zapier_payload = {
                'timestamp': datetime.utcnow().isoformat(),
                'platform': 'AI Video Generator',
                **data
            }
            
            response = requests.post(
                hook_url,
                json=zapier_payload,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'AI-Video-Generator-Zapier/1.0'
                },
                timeout=30
            )
            
            if response.status_code >= 400:
                current_app.logger.error(f"Zapier webhook failed: {response.status_code}")
                
        except Exception as e:
            current_app.logger.error(f"Zapier integration error: {str(e)}")
    
    def get_sample_data(self, event: str) -> Dict[str, Any]:
        """Provide sample data for Zapier trigger setup."""
        samples = {
            'video.generated': {
                'video_id': 'vid_123456',
                'title': 'Sample Spiritual Video',
                'duration': 120,
                'url': 'https://example.com/video/123456',
                'thumbnail': 'https://example.com/thumb/123456.jpg',
                'guru': 'spiritual',
                'user_id': 'user_789',
                'created_at': datetime.utcnow().isoformat()
            },
            'video.completed': {
                'video_id': 'vid_123456',
                'title': 'Sample Spiritual Video',
                'processing_time': 45,
                'file_size': 1024000,
                'resolution': '1080p',
                'status': 'completed'
            },
            'user.registered': {
                'user_id': 'user_789',
                'email': 'user@example.com',
                'name': 'Sample User',
                'signup_date': datetime.utcnow().isoformat(),
                'subscription_type': 'free'
            }
        }
        
        return samples.get(event, {})
    
    def unsubscribe_trigger(self, trigger_id: str) -> bool:
        """Remove a Zapier trigger subscription."""
        if trigger_id in self.subscriptions:
            self.subscriptions[trigger_id]['active'] = False
            return True
        return False


class ZapierActions:
    """Handles incoming actions from Zapier workflows."""
    
    @staticmethod
    def create_video_from_zapier(data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a video from Zapier action data."""
        # Extract parameters from Zapier
        title = data.get('title', 'Zapier Generated Video')
        content = data.get('content', '')
        guru_type = data.get('guru_type', 'spiritual')
        user_id = data.get('user_id')
        
        # Simulate video creation (integrate with actual video generation)
        video_id = f"zap_{datetime.utcnow().timestamp()}"
        
        return {
            'success': True,
            'video_id': video_id,
            'title': title,
            'status': 'processing',
            'estimated_completion': datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def send_notification_from_zapier(data: Dict[str, Any]) -> Dict[str, Any]:
        """Send notification triggered by Zapier."""
        message = data.get('message', '')
        recipient = data.get('recipient', '')
        channel = data.get('channel', 'email')
        
        # Simulate notification sending
        notification_id = f"notif_{datetime.utcnow().timestamp()}"
        
        return {
            'success': True,
            'notification_id': notification_id,
            'recipient': recipient,
            'channel': channel,
            'sent_at': datetime.utcnow().isoformat()
        }


# Global Zapier integration instance
zapier_integration = ZapierIntegration()