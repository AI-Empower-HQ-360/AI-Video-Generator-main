"""
Webhook system for custom integrations.
Provides endpoints and management for third-party webhook integrations.
"""

import requests
import json
import hashlib
import hmac
from datetime import datetime
from typing import Dict, List, Optional, Any
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


class WebhookManager:
    """Manages webhook registrations and deliveries."""
    
    def __init__(self):
        self.webhooks = {}
        self.events = [
            'video.generated',
            'video.completed',
            'video.failed',
            'user.registered',
            'session.started',
            'session.completed'
        ]
    
    def register_webhook(self, url: str, events: List[str], secret: Optional[str] = None) -> str:
        """Register a new webhook endpoint."""
        webhook_id = hashlib.md5(f"{url}{datetime.utcnow()}".encode()).hexdigest()
        
        self.webhooks[webhook_id] = {
            'url': url,
            'events': events,
            'secret': secret,
            'active': True,
            'created_at': datetime.utcnow().isoformat(),
            'delivery_count': 0,
            'last_delivery': None
        }
        
        return webhook_id
    
    def trigger_webhook(self, event: str, payload: Dict[str, Any]) -> None:
        """Trigger webhooks for a specific event."""
        for webhook_id, webhook in self.webhooks.items():
            if webhook['active'] and event in webhook['events']:
                self._deliver_webhook(webhook_id, webhook, event, payload)
    
    def _deliver_webhook(self, webhook_id: str, webhook: Dict, event: str, payload: Dict) -> None:
        """Deliver webhook payload to endpoint."""
        try:
            webhook_payload = {
                'event': event,
                'timestamp': datetime.utcnow().isoformat(),
                'data': payload,
                'webhook_id': webhook_id
            }
            
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'AI-Video-Generator-Webhook/1.0'
            }
            
            # Add signature if secret is provided
            if webhook['secret']:
                signature = self._generate_signature(
                    json.dumps(webhook_payload), 
                    webhook['secret']
                )
                headers['X-Webhook-Signature'] = f"sha256={signature}"
            
            response = requests.post(
                webhook['url'],
                json=webhook_payload,
                headers=headers,
                timeout=30
            )
            
            # Update delivery stats
            self.webhooks[webhook_id]['delivery_count'] += 1
            self.webhooks[webhook_id]['last_delivery'] = {
                'timestamp': datetime.utcnow().isoformat(),
                'status_code': response.status_code,
                'success': response.status_code < 400
            }
            
        except Exception as e:
            current_app.logger.error(f"Webhook delivery failed for {webhook_id}: {str(e)}")
            
            self.webhooks[webhook_id]['last_delivery'] = {
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e),
                'success': False
            }
    
    def _generate_signature(self, payload: str, secret: str) -> str:
        """Generate HMAC-SHA256 signature for webhook verification."""
        return hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def get_webhook(self, webhook_id: str) -> Optional[Dict]:
        """Get webhook details by ID."""
        return self.webhooks.get(webhook_id)
    
    def list_webhooks(self) -> Dict[str, Dict]:
        """List all registered webhooks."""
        return self.webhooks
    
    def delete_webhook(self, webhook_id: str) -> bool:
        """Delete a webhook registration."""
        if webhook_id in self.webhooks:
            del self.webhooks[webhook_id]
            return True
        return False
    
    def deactivate_webhook(self, webhook_id: str) -> bool:
        """Deactivate a webhook without deleting it."""
        if webhook_id in self.webhooks:
            self.webhooks[webhook_id]['active'] = False
            return True
        return False


# Global webhook manager instance
webhook_manager = WebhookManager()