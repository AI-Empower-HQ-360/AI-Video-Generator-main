"""
Integration helpers for triggering third-party integrations.
Provides utility functions to be called from other parts of the application.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import threading
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

# Import integration managers
from integrations.webhook_system import webhook_manager
from integrations.zapier_integration import zapier_integration
from integrations.messaging_bots import notification_manager
from integrations.crm_integrations import crm_manager
from integrations.cms_plugins import cms_manager
from integrations.analytics_tracking import analytics_manager


class IntegrationTrigger:
    """Helper class to trigger integrations throughout the application."""
    
    @staticmethod
    def on_video_generated(video_data: Dict[str, Any], user_data: Dict[str, Any] = None) -> None:
        """Trigger all integrations when a video is generated."""
        
        def async_trigger():
            try:
                # Trigger webhooks
                webhook_manager.trigger_webhook('video.generated', video_data)
                
                # Trigger Zapier
                zapier_integration.trigger_event('video.generated', video_data)
                
                # Send notifications
                notification_manager.notify_video_generated(video_data)
                
                # Track analytics
                analytics_manager.track_video_event('video_generated', video_data, user_data)
                
                # Track CRM engagement
                if user_data and user_data.get('user_id'):
                    crm_manager.track_video_engagement(user_data['user_id'], video_data)
                
                current_app.logger.info(f"Video integrations triggered for video {video_data.get('video_id')}")
                
            except Exception as e:
                current_app.logger.error(f"Integration trigger failed: {str(e)}")
        
        # Run integrations asynchronously to avoid blocking video generation
        threading.Thread(target=async_trigger).start()
    
    @staticmethod
    def on_video_completed(video_data: Dict[str, Any], user_data: Dict[str, Any] = None) -> None:
        """Trigger integrations when video processing is completed."""
        
        def async_trigger():
            try:
                # Update video data with completion status
                completed_data = {
                    **video_data,
                    'status': 'completed',
                    'completed_at': datetime.utcnow().isoformat()
                }
                
                # Trigger webhooks
                webhook_manager.trigger_webhook('video.completed', completed_data)
                
                # Trigger Zapier
                zapier_integration.trigger_event('video.completed', completed_data)
                
                # Track analytics
                analytics_manager.track_video_event('video_complete', completed_data, user_data)
                
                current_app.logger.info(f"Video completion integrations triggered for video {video_data.get('video_id')}")
                
            except Exception as e:
                current_app.logger.error(f"Video completion integration trigger failed: {str(e)}")
        
        threading.Thread(target=async_trigger).start()
    
    @staticmethod
    def on_user_registered(user_data: Dict[str, Any]) -> None:
        """Trigger integrations when a new user registers."""
        
        def async_trigger():
            try:
                # Trigger webhooks
                webhook_manager.trigger_webhook('user.registered', user_data)
                
                # Trigger Zapier
                zapier_integration.trigger_event('user.registered', user_data)
                
                # Sync to CRM
                crm_manager.sync_user_to_crm(user_data)
                
                # Track analytics
                analytics_manager.track_conversion('lead', {
                    'user_data': user_data,
                    'value': 1,
                    'page_url': user_data.get('signup_page', '')
                })
                
                current_app.logger.info(f"User registration integrations triggered for user {user_data.get('user_id')}")
                
            except Exception as e:
                current_app.logger.error(f"User registration integration trigger failed: {str(e)}")
        
        threading.Thread(target=async_trigger).start()
    
    @staticmethod
    def on_subscription_purchased(subscription_data: Dict[str, Any]) -> None:
        """Trigger integrations when a user purchases a subscription."""
        
        def async_trigger():
            try:
                # Track conversion analytics
                analytics_manager.track_conversion('subscription', subscription_data)
                
                # Create CRM opportunities
                if subscription_data.get('user_data'):
                    user_data = subscription_data['user_data']
                    opportunity_data = {
                        'user_email': user_data.get('email'),
                        'value': subscription_data.get('amount', 0),
                        'subscription_type': subscription_data.get('plan_name')
                    }
                    
                    # Create opportunities in enabled CRMs
                    if 'salesforce' in crm_manager.enabled_crms:
                        crm_manager.salesforce.create_opportunity(opportunity_data)
                    
                    if 'hubspot' in crm_manager.enabled_crms:
                        crm_manager.hubspot.create_deal(opportunity_data)
                
                # Trigger webhooks
                webhook_manager.trigger_webhook('subscription.purchased', subscription_data)
                
                current_app.logger.info(f"Subscription purchase integrations triggered for {subscription_data.get('user_id')}")
                
            except Exception as e:
                current_app.logger.error(f"Subscription purchase integration trigger failed: {str(e)}")
        
        threading.Thread(target=async_trigger).start()
    
    @staticmethod
    def on_session_started(session_data: Dict[str, Any]) -> None:
        """Trigger integrations when a user starts a session."""
        
        def async_trigger():
            try:
                # Trigger webhooks
                webhook_manager.trigger_webhook('session.started', session_data)
                
                # Track user engagement
                if session_data.get('user_data'):
                    analytics_manager.track_video_event('session_start', session_data, session_data['user_data'])
                
                current_app.logger.info(f"Session start integrations triggered for session {session_data.get('session_id')}")
                
            except Exception as e:
                current_app.logger.error(f"Session start integration trigger failed: {str(e)}")
        
        threading.Thread(target=async_trigger).start()
    
    @staticmethod
    def publish_video_to_cms(video_data: Dict[str, Any], cms_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Publish video to configured CMS platforms."""
        try:
            cms_options = cms_options or {}
            
            # Default options for different platforms
            default_options = {
                'wordpress': {
                    'create_page': cms_options.get('wordpress_create_page', False),
                    'post_data': {
                        'status': cms_options.get('wordpress_status', 'publish'),
                        'categories': cms_options.get('wordpress_categories', [1])
                    }
                },
                'shopify': {
                    'product_id': cms_options.get('shopify_product_id'),
                    'update_description': cms_options.get('shopify_update_description', True)
                }
            }
            
            platforms = cms_options.get('platforms', cms_manager.enabled_platforms)
            
            results = cms_manager.publish_video_to_cms(
                video_data, 
                platforms, 
                default_options
            )
            
            current_app.logger.info(f"Video published to CMS platforms: {list(results.keys())}")
            
            return results
            
        except Exception as e:
            current_app.logger.error(f"CMS publishing failed: {str(e)}")
            return {'error': str(e)}


class IntegrationConfig:
    """Helper class for managing integration configurations."""
    
    @staticmethod
    def get_integration_status() -> Dict[str, Any]:
        """Get comprehensive status of all integrations."""
        return {
            'messaging': {
                'slack': 'slack' in notification_manager.enabled_platforms,
                'teams': 'teams' in notification_manager.enabled_platforms,
                'discord': 'discord' in notification_manager.enabled_platforms
            },
            'crm': {
                'salesforce': 'salesforce' in crm_manager.enabled_crms,
                'hubspot': 'hubspot' in crm_manager.enabled_crms
            },
            'cms': {
                'wordpress': 'wordpress' in cms_manager.enabled_platforms,
                'shopify': 'shopify' in cms_manager.enabled_platforms
            },
            'analytics': {
                'google_analytics': 'google_analytics' in analytics_manager.enabled_platforms,
                'facebook_pixel': 'facebook_pixel' in analytics_manager.enabled_platforms
            },
            'webhooks': {
                'total_registered': len(webhook_manager.list_webhooks()),
                'active_webhooks': len([w for w in webhook_manager.list_webhooks().values() if w.get('active')])
            }
        }
    
    @staticmethod
    def get_available_integrations() -> List[Dict[str, Any]]:
        """Get list of all available integrations with their features."""
        return [
            {
                'name': 'Zapier',
                'category': 'automation',
                'features': ['workflow_automation', 'trigger_creation', 'action_handling'],
                'setup_url': '/api/integrations/zapier/triggers',
                'documentation': 'https://zapier.com/apps/ai-video-generator'
            },
            {
                'name': 'Slack',
                'category': 'messaging',
                'features': ['video_notifications', 'bot_commands', 'channel_integration'],
                'setup_url': '/api/integrations/messaging/slack/configure',
                'documentation': 'Setup Slack bot token or webhook URL'
            },
            {
                'name': 'Microsoft Teams',
                'category': 'messaging',
                'features': ['video_notifications', 'adaptive_cards'],
                'setup_url': '/api/integrations/messaging/teams/configure',
                'documentation': 'Configure Teams incoming webhook'
            },
            {
                'name': 'Discord',
                'category': 'messaging',
                'features': ['video_notifications', 'community_sharing', 'embed_support'],
                'setup_url': '/api/integrations/messaging/discord/configure',
                'documentation': 'Setup Discord webhook or bot token'
            },
            {
                'name': 'Salesforce',
                'category': 'crm',
                'features': ['lead_tracking', 'opportunity_management', 'activity_logging'],
                'setup_url': '/api/integrations/crm/salesforce/configure',
                'documentation': 'Configure Salesforce OAuth credentials'
            },
            {
                'name': 'HubSpot',
                'category': 'crm',
                'features': ['contact_management', 'deal_tracking', 'timeline_events'],
                'setup_url': '/api/integrations/crm/hubspot/configure',
                'documentation': 'Provide HubSpot API key'
            },
            {
                'name': 'WordPress',
                'category': 'cms',
                'features': ['video_posts', 'video_pages', 'shortcode_support'],
                'setup_url': '/api/integrations/cms/wordpress/configure',
                'documentation': 'Configure WordPress REST API credentials'
            },
            {
                'name': 'Shopify',
                'category': 'cms',
                'features': ['product_videos', 'video_collections', 'description_enhancement'],
                'setup_url': '/api/integrations/cms/shopify/configure',
                'documentation': 'Provide Shopify store domain and access token'
            },
            {
                'name': 'Google Analytics',
                'category': 'analytics',
                'features': ['video_tracking', 'conversion_tracking', 'user_engagement'],
                'setup_url': '/api/integrations/analytics/google/configure',
                'documentation': 'Configure GA4 Measurement ID and API Secret'
            },
            {
                'name': 'Facebook Pixel',
                'category': 'analytics',
                'features': ['conversion_tracking', 'video_views', 'custom_events'],
                'setup_url': '/api/integrations/analytics/facebook/configure',
                'documentation': 'Provide Facebook Pixel ID and Access Token'
            },
            {
                'name': 'Custom Webhooks',
                'category': 'automation',
                'features': ['custom_endpoints', 'event_filtering', 'signature_verification'],
                'setup_url': '/api/integrations/webhooks',
                'documentation': 'Register webhook URLs for specific events'
            }
        ]


# Global integration helpers
integration_trigger = IntegrationTrigger()
integration_config = IntegrationConfig()