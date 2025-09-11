"""
Analytics and tracking integrations for Google Analytics and Facebook Pixel.
Provides comprehensive video engagement tracking and conversion analytics.
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
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
import uuid


class GoogleAnalyticsIntegration:
    """Google Analytics integration for video metrics tracking."""
    
    def __init__(self, measurement_id: str = None, api_secret: str = None):
        self.measurement_id = measurement_id
        self.api_secret = api_secret
        self.base_url = "https://www.google-analytics.com/mp/collect"
    
    def track_video_event(self, event_type: str, video_data: Dict[str, Any], 
                         user_data: Dict[str, Any] = None) -> bool:
        """Track video-related events in Google Analytics."""
        if not self._is_configured():
            return False
        
        # Generate client ID if not provided
        client_id = user_data.get('client_id', str(uuid.uuid4()))
        
        # Prepare event data
        event_data = {
            'client_id': client_id,
            'events': [{
                'name': self._map_event_name(event_type),
                'parameters': {
                    'video_id': video_data.get('video_id', ''),
                    'video_title': video_data.get('title', ''),
                    'video_duration': video_data.get('duration', 0),
                    'guru_type': video_data.get('guru', ''),
                    'engagement_time_msec': video_data.get('watch_time', 0) * 1000,
                    'custom_parameter_1': video_data.get('quality', 'standard'),
                    'custom_parameter_2': video_data.get('device_type', 'unknown')
                }
            }]
        }
        
        # Add user properties if available
        if user_data:
            event_data['user_properties'] = {
                'subscription_type': {'value': user_data.get('subscription_type', 'free')},
                'user_type': {'value': user_data.get('user_type', 'new')},
                'total_videos': {'value': user_data.get('video_count', 1)}
            }
        
        return self._send_event(event_data)
    
    def track_video_conversion(self, conversion_data: Dict[str, Any]) -> bool:
        """Track video-related conversions (subscriptions, purchases)."""
        if not self._is_configured():
            return False
        
        client_id = conversion_data.get('client_id', str(uuid.uuid4()))
        
        event_data = {
            'client_id': client_id,
            'events': [{
                'name': 'purchase',  # or 'sign_up' for subscriptions
                'parameters': {
                    'currency': conversion_data.get('currency', 'USD'),
                    'value': conversion_data.get('value', 0),
                    'transaction_id': conversion_data.get('transaction_id', ''),
                    'items': [{
                        'item_id': conversion_data.get('item_id', 'video_subscription'),
                        'item_name': conversion_data.get('item_name', 'AI Video Generator Subscription'),
                        'category': 'subscription',
                        'quantity': 1,
                        'price': conversion_data.get('value', 0)
                    }]
                }
            }]
        }
        
        return self._send_event(event_data)
    
    def track_user_engagement(self, engagement_data: Dict[str, Any]) -> bool:
        """Track overall user engagement metrics."""
        if not self._is_configured():
            return False
        
        client_id = engagement_data.get('client_id', str(uuid.uuid4()))
        
        event_data = {
            'client_id': client_id,
            'events': [{
                'name': 'user_engagement',
                'parameters': {
                    'engagement_time_msec': engagement_data.get('session_duration', 0) * 1000,
                    'page_title': 'AI Video Generator',
                    'page_location': engagement_data.get('page_url', ''),
                    'videos_viewed': engagement_data.get('videos_viewed', 0),
                    'features_used': engagement_data.get('features_used', [])
                }
            }]
        }
        
        return self._send_event(event_data)
    
    def _map_event_name(self, event_type: str) -> str:
        """Map internal event types to GA4 event names."""
        mapping = {
            'video_start': 'video_start',
            'video_complete': 'video_complete',
            'video_progress': 'video_progress',
            'video_generated': 'video_view',
            'video_shared': 'share',
            'guru_selected': 'select_content'
        }
        
        return mapping.get(event_type, 'custom_event')
    
    def _send_event(self, event_data: Dict[str, Any]) -> bool:
        """Send event to Google Analytics."""
        url = f"{self.base_url}?measurement_id={self.measurement_id}&api_secret={self.api_secret}"
        
        try:
            response = requests.post(url, json=event_data, timeout=10)
            return response.status_code == 204
        except Exception as e:
            current_app.logger.error(f"Google Analytics tracking failed: {str(e)}")
            return False
    
    def _is_configured(self) -> bool:
        """Check if Google Analytics is properly configured."""
        return bool(self.measurement_id and self.api_secret)


class FacebookPixelIntegration:
    """Facebook Pixel integration for conversion tracking."""
    
    def __init__(self, pixel_id: str = None, access_token: str = None):
        self.pixel_id = pixel_id
        self.access_token = access_token
        self.base_url = "https://graph.facebook.com/v18.0"
    
    def track_video_view(self, video_data: Dict[str, Any], user_data: Dict[str, Any] = None) -> bool:
        """Track video views for Facebook advertising."""
        if not self._is_configured():
            return False
        
        event_data = {
            'event_name': 'ViewContent',
            'event_time': int(datetime.utcnow().timestamp()),
            'action_source': 'website',
            'event_source_url': video_data.get('page_url', ''),
            'user_data': self._prepare_user_data(user_data),
            'custom_data': {
                'content_type': 'video',
                'content_ids': [video_data.get('video_id', '')],
                'content_name': video_data.get('title', ''),
                'content_category': video_data.get('guru', 'spiritual'),
                'value': 0,
                'currency': 'USD'
            }
        }
        
        return self._send_event(event_data)
    
    def track_subscription(self, subscription_data: Dict[str, Any]) -> bool:
        """Track subscription conversions."""
        if not self._is_configured():
            return False
        
        event_data = {
            'event_name': 'Subscribe',
            'event_time': int(datetime.utcnow().timestamp()),
            'action_source': 'website',
            'event_source_url': subscription_data.get('page_url', ''),
            'user_data': self._prepare_user_data(subscription_data.get('user_data', {})),
            'custom_data': {
                'content_type': 'subscription',
                'content_name': subscription_data.get('plan_name', 'Premium Subscription'),
                'value': subscription_data.get('value', 0),
                'currency': subscription_data.get('currency', 'USD'),
                'predicted_ltv': subscription_data.get('predicted_ltv', 0)
            }
        }
        
        return self._send_event(event_data)
    
    def track_lead_generation(self, lead_data: Dict[str, Any]) -> bool:
        """Track lead generation from video engagement."""
        if not self._is_configured():
            return False
        
        event_data = {
            'event_name': 'Lead',
            'event_time': int(datetime.utcnow().timestamp()),
            'action_source': 'website',
            'event_source_url': lead_data.get('page_url', ''),
            'user_data': self._prepare_user_data(lead_data.get('user_data', {})),
            'custom_data': {
                'content_type': 'lead_form',
                'content_name': 'Video Engagement Lead',
                'value': lead_data.get('value', 1),
                'currency': 'USD'
            }
        }
        
        return self._send_event(event_data)
    
    def track_custom_conversion(self, conversion_data: Dict[str, Any]) -> bool:
        """Track custom conversion events."""
        if not self._is_configured():
            return False
        
        event_data = {
            'event_name': conversion_data.get('event_name', 'CustomConversion'),
            'event_time': int(datetime.utcnow().timestamp()),
            'action_source': 'website',
            'event_source_url': conversion_data.get('page_url', ''),
            'user_data': self._prepare_user_data(conversion_data.get('user_data', {})),
            'custom_data': conversion_data.get('custom_data', {})
        }
        
        return self._send_event(event_data)
    
    def _prepare_user_data(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare user data for Facebook Pixel."""
        prepared_data = {}
        
        if user_data.get('email'):
            prepared_data['em'] = self._hash_data(user_data['email'].lower())
        
        if user_data.get('phone'):
            prepared_data['ph'] = self._hash_data(user_data['phone'])
        
        if user_data.get('first_name'):
            prepared_data['fn'] = self._hash_data(user_data['first_name'].lower())
        
        if user_data.get('last_name'):
            prepared_data['ln'] = self._hash_data(user_data['last_name'].lower())
        
        if user_data.get('city'):
            prepared_data['ct'] = self._hash_data(user_data['city'].lower())
        
        if user_data.get('state'):
            prepared_data['st'] = self._hash_data(user_data['state'].lower())
        
        if user_data.get('country'):
            prepared_data['country'] = self._hash_data(user_data['country'].lower())
        
        if user_data.get('zip_code'):
            prepared_data['zp'] = self._hash_data(user_data['zip_code'])
        
        # Add client user agent and IP if available
        if user_data.get('user_agent'):
            prepared_data['client_user_agent'] = user_data['user_agent']
        
        if user_data.get('client_ip'):
            prepared_data['client_ip_address'] = user_data['client_ip']
        
        return prepared_data
    
    def _hash_data(self, data: str) -> str:
        """Hash sensitive data for Facebook Pixel."""
        import hashlib
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _send_event(self, event_data: Dict[str, Any]) -> bool:
        """Send event to Facebook Pixel."""
        url = f"{self.base_url}/{self.pixel_id}/events"
        
        payload = {
            'data': [event_data],
            'access_token': self.access_token
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            current_app.logger.error(f"Facebook Pixel tracking failed: {str(e)}")
            return False
    
    def _is_configured(self) -> bool:
        """Check if Facebook Pixel is properly configured."""
        return bool(self.pixel_id and self.access_token)


class AnalyticsManager:
    """Manages analytics integrations and tracking."""
    
    def __init__(self):
        self.google_analytics = GoogleAnalyticsIntegration()
        self.facebook_pixel = FacebookPixelIntegration()
        self.enabled_platforms = []
        self.tracking_config = {
            'track_video_views': True,
            'track_conversions': True,
            'track_user_engagement': True,
            'track_custom_events': True
        }
    
    def configure_google_analytics(self, measurement_id: str, api_secret: str) -> bool:
        """Configure Google Analytics integration."""
        self.google_analytics = GoogleAnalyticsIntegration(measurement_id, api_secret)
        
        if 'google_analytics' not in self.enabled_platforms:
            self.enabled_platforms.append('google_analytics')
        
        return True
    
    def configure_facebook_pixel(self, pixel_id: str, access_token: str) -> bool:
        """Configure Facebook Pixel integration."""
        self.facebook_pixel = FacebookPixelIntegration(pixel_id, access_token)
        
        if 'facebook_pixel' not in self.enabled_platforms:
            self.enabled_platforms.append('facebook_pixel')
        
        return True
    
    def track_video_event(self, event_type: str, video_data: Dict[str, Any], 
                         user_data: Dict[str, Any] = None, platforms: List[str] = None) -> Dict[str, Any]:
        """Track video events across enabled platforms."""
        if not self.tracking_config.get('track_video_views', True):
            return {}
        
        target_platforms = platforms or self.enabled_platforms
        results = {}
        
        if 'google_analytics' in target_platforms and 'google_analytics' in self.enabled_platforms:
            success = self.google_analytics.track_video_event(event_type, video_data, user_data)
            results['google_analytics'] = {'success': success, 'event_type': event_type}
        
        if 'facebook_pixel' in target_platforms and 'facebook_pixel' in self.enabled_platforms:
            if event_type in ['video_start', 'video_generated', 'video_complete']:
                success = self.facebook_pixel.track_video_view(video_data, user_data)
                results['facebook_pixel'] = {'success': success, 'event_type': 'ViewContent'}
        
        return results
    
    def track_conversion(self, conversion_type: str, conversion_data: Dict[str, Any], 
                        platforms: List[str] = None) -> Dict[str, Any]:
        """Track conversions across enabled platforms."""
        if not self.tracking_config.get('track_conversions', True):
            return {}
        
        target_platforms = platforms or self.enabled_platforms
        results = {}
        
        if 'google_analytics' in target_platforms and 'google_analytics' in self.enabled_platforms:
            success = self.google_analytics.track_video_conversion(conversion_data)
            results['google_analytics'] = {'success': success, 'conversion_type': conversion_type}
        
        if 'facebook_pixel' in target_platforms and 'facebook_pixel' in self.enabled_platforms:
            if conversion_type == 'subscription':
                success = self.facebook_pixel.track_subscription(conversion_data)
                results['facebook_pixel'] = {'success': success, 'event_type': 'Subscribe'}
            elif conversion_type == 'lead':
                success = self.facebook_pixel.track_lead_generation(conversion_data)
                results['facebook_pixel'] = {'success': success, 'event_type': 'Lead'}
        
        return results
    
    def get_tracking_code(self, platform: str) -> str:
        """Generate client-side tracking code for platforms."""
        if platform == 'google_analytics' and 'google_analytics' in self.enabled_platforms:
            measurement_id = self.google_analytics.measurement_id
            return f"""
            <!-- Google Analytics -->
            <script async src="https://www.googletagmanager.com/gtag/js?id={measurement_id}"></script>
            <script>
              window.dataLayer = window.dataLayer || [];
              function gtag(){{dataLayer.push(arguments);}}
              gtag('js', new Date());
              gtag('config', '{measurement_id}');
              
              // Video tracking functions
              function trackVideoStart(videoId, title) {{
                gtag('event', 'video_start', {{
                  'video_id': videoId,
                  'video_title': title
                }});
              }}
              
              function trackVideoComplete(videoId, title) {{
                gtag('event', 'video_complete', {{
                  'video_id': videoId,
                  'video_title': title
                }});
              }}
            </script>
            """
        
        elif platform == 'facebook_pixel' and 'facebook_pixel' in self.enabled_platforms:
            pixel_id = self.facebook_pixel.pixel_id
            return f"""
            <!-- Facebook Pixel -->
            <script>
              !function(f,b,e,v,n,t,s)
              {{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?
              n.callMethod.apply(n,arguments):n.queue.push(arguments)}};
              if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
              n.queue=[];t=b.createElement(e);t.async=!0;
              t.src=v;s=b.getElementsByTagName(e)[0];
              s.parentNode.insertBefore(t,s)}}(window, document,'script',
              'https://connect.facebook.net/en_US/fbevents.js');
              
              fbq('init', '{pixel_id}');
              fbq('track', 'PageView');
              
              // Video tracking functions
              function trackVideoView(videoId, title) {{
                fbq('track', 'ViewContent', {{
                  content_type: 'video',
                  content_ids: [videoId],
                  content_name: title
                }});
              }}
            </script>
            <noscript>
              <img height="1" width="1" style="display:none"
                   src="https://www.facebook.com/tr?id={pixel_id}&ev=PageView&noscript=1"/>
            </noscript>
            """
        
        return ""


# Global analytics manager instance
analytics_manager = AnalyticsManager()