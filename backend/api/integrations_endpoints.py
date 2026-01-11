"""
Integration endpoints for third-party services.
Provides API endpoints for webhook management and integration configuration.
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import json

# Import integration managers
from integrations.webhook_system import webhook_manager
from integrations.zapier_integration import zapier_integration, ZapierActions
from integrations.messaging_bots import notification_manager
from integrations.crm_integrations import crm_manager
from integrations.cms_plugins import cms_manager
from integrations.analytics_tracking import analytics_manager

integrations_bp = Blueprint('integrations', __name__)


# Webhook Management Endpoints
@integrations_bp.route('/webhooks', methods=['POST'])
def register_webhook():
    """Register a new webhook endpoint."""
    try:
        data = request.get_json()
        
        url = data.get('url')
        events = data.get('events', [])
        secret = data.get('secret')
        
        if not url or not events:
            return jsonify({'error': 'URL and events are required'}), 400
        
        webhook_id = webhook_manager.register_webhook(url, events, secret)
        
        return jsonify({
            'webhook_id': webhook_id,
            'url': url,
            'events': events,
            'status': 'registered'
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Webhook registration failed: {str(e)}")
        return jsonify({'error': 'Failed to register webhook'}), 500


@integrations_bp.route('/webhooks', methods=['GET'])
def list_webhooks():
    """List all registered webhooks."""
    try:
        webhooks = webhook_manager.list_webhooks()
        return jsonify({'webhooks': webhooks})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@integrations_bp.route('/webhooks/<webhook_id>', methods=['DELETE'])
def delete_webhook(webhook_id):
    """Delete a webhook registration."""
    try:
        success = webhook_manager.delete_webhook(webhook_id)
        if success:
            return jsonify({'message': 'Webhook deleted successfully'})
        else:
            return jsonify({'error': 'Webhook not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@integrations_bp.route('/webhooks/test', methods=['POST'])
def test_webhook():
    """Test webhook delivery with sample data."""
    try:
        data = request.get_json()
        event = data.get('event', 'video.generated')
        
        test_payload = {
            'video_id': 'test_123',
            'title': 'Test Video',
            'duration': 60,
            'url': 'https://example.com/test.mp4',
            'created_at': datetime.utcnow().isoformat()
        }
        
        webhook_manager.trigger_webhook(event, test_payload)
        
        return jsonify({
            'message': 'Test webhook triggered',
            'event': event,
            'payload': test_payload
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Zapier Integration Endpoints
@integrations_bp.route('/zapier/triggers', methods=['POST'])
def register_zapier_trigger():
    """Register a Zapier trigger webhook."""
    try:
        data = request.get_json()
        
        event = data.get('event')
        hook_url = data.get('hook_url')
        
        if not event or not hook_url:
            return jsonify({'error': 'Event and hook_url are required'}), 400
        
        trigger_id = zapier_integration.register_trigger(event, hook_url)
        
        return jsonify({
            'trigger_id': trigger_id,
            'event': event,
            'hook_url': hook_url,
            'status': 'registered'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@integrations_bp.route('/zapier/sample/<event>', methods=['GET'])
def get_zapier_sample_data(event):
    """Get sample data for Zapier trigger setup."""
    try:
        sample_data = zapier_integration.get_sample_data(event)
        return jsonify({'event': event, 'sample_data': sample_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@integrations_bp.route('/zapier/actions/create-video', methods=['POST'])
def zapier_create_video():
    """Handle Zapier action to create a video."""
    try:
        data = request.get_json()
        result = ZapierActions.create_video_from_zapier(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@integrations_bp.route('/zapier/actions/send-notification', methods=['POST'])
def zapier_send_notification():
    """Handle Zapier action to send notification."""
    try:
        data = request.get_json()
        result = ZapierActions.send_notification_from_zapier(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Messaging Bot Configuration
@integrations_bp.route('/messaging/slack/configure', methods=['POST'])
def configure_slack():
    """Configure Slack bot integration."""
    try:
        data = request.get_json()
        
        bot_token = data.get('bot_token')
        webhook_url = data.get('webhook_url')
        
        notification_manager.configure_slack(bot_token, webhook_url)
        
        return jsonify({
            'platform': 'slack',
            'status': 'configured',
            'features': ['video_notifications', 'user_commands']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@integrations_bp.route('/messaging/teams/configure', methods=['POST'])
def configure_teams():
    """Configure Microsoft Teams integration."""
    try:
        data = request.get_json()
        webhook_url = data.get('webhook_url')
        
        if not webhook_url:
            return jsonify({'error': 'webhook_url is required'}), 400
        
        notification_manager.configure_teams(webhook_url)
        
        return jsonify({
            'platform': 'teams',
            'status': 'configured',
            'features': ['video_notifications']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@integrations_bp.route('/messaging/discord/configure', methods=['POST'])
def configure_discord():
    """Configure Discord bot integration."""
    try:
        data = request.get_json()
        
        webhook_url = data.get('webhook_url')
        bot_token = data.get('bot_token')
        
        notification_manager.configure_discord(webhook_url, bot_token)
        
        return jsonify({
            'platform': 'discord',
            'status': 'configured',
            'features': ['video_notifications', 'community_sharing']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@integrations_bp.route('/messaging/notify', methods=['POST'])
def send_video_notification():
    """Send video notification to configured platforms."""
    try:
        data = request.get_json()
        
        video_data = data.get('video_data', {})
        platforms = data.get('platforms', [])
        
        results = notification_manager.notify_video_generated(video_data, platforms)
        
        return jsonify({
            'message': 'Notifications sent',
            'results': results,
            'video_id': video_data.get('video_id')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# CRM Integration Configuration
@integrations_bp.route('/crm/salesforce/configure', methods=['POST'])
def configure_salesforce():
    """Configure Salesforce CRM integration."""
    try:
        data = request.get_json()
        
        instance_url = data.get('instance_url')
        client_id = data.get('client_id')
        client_secret = data.get('client_secret')
        username = data.get('username')
        password = data.get('password')
        
        success = crm_manager.configure_salesforce(
            instance_url, client_id, client_secret, username, password
        )
        
        if success:
            return jsonify({
                'platform': 'salesforce',
                'status': 'configured',
                'features': ['lead_tracking', 'opportunity_management', 'activity_logging']
            })
        else:
            return jsonify({'error': 'Salesforce authentication failed'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@integrations_bp.route('/crm/hubspot/configure', methods=['POST'])
def configure_hubspot():
    """Configure HubSpot CRM integration."""
    try:
        data = request.get_json()
        api_key = data.get('api_key')
        
        if not api_key:
            return jsonify({'error': 'api_key is required'}), 400
        
        crm_manager.configure_hubspot(api_key)
        
        return jsonify({
            'platform': 'hubspot',
            'status': 'configured',
            'features': ['contact_management', 'deal_tracking', 'timeline_events']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@integrations_bp.route('/crm/sync-user', methods=['POST'])
def sync_user_to_crm():
    """Sync user data to configured CRM systems."""
    try:
        data = request.get_json()
        
        user_data = data.get('user_data', {})
        crms = data.get('crms', [])
        
        results = crm_manager.sync_user_to_crm(user_data, crms)
        
        return jsonify({
            'message': 'User synced to CRM',
            'results': results,
            'user_id': user_data.get('user_id')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# CMS Integration Configuration
@integrations_bp.route('/cms/wordpress/configure', methods=['POST'])
def configure_wordpress():
    """Configure WordPress CMS integration."""
    try:
        data = request.get_json()
        
        site_url = data.get('site_url')
        username = data.get('username')
        password = data.get('password')
        
        if not all([site_url, username, password]):
            return jsonify({'error': 'site_url, username, and password are required'}), 400
        
        cms_manager.configure_wordpress(site_url, username, password)
        
        return jsonify({
            'platform': 'wordpress',
            'status': 'configured',
            'features': ['video_posts', 'video_pages', 'shortcode_support']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@integrations_bp.route('/cms/shopify/configure', methods=['POST'])
def configure_shopify():
    """Configure Shopify integration."""
    try:
        data = request.get_json()
        
        shop_domain = data.get('shop_domain')
        access_token = data.get('access_token')
        
        if not all([shop_domain, access_token]):
            return jsonify({'error': 'shop_domain and access_token are required'}), 400
        
        cms_manager.configure_shopify(shop_domain, access_token)
        
        return jsonify({
            'platform': 'shopify',
            'status': 'configured',
            'features': ['product_videos', 'video_collections', 'description_enhancement']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@integrations_bp.route('/cms/publish', methods=['POST'])
def publish_video_to_cms():
    """Publish video to configured CMS platforms."""
    try:
        data = request.get_json()
        
        video_data = data.get('video_data', {})
        platforms = data.get('platforms', [])
        options = data.get('options', {})
        
        results = cms_manager.publish_video_to_cms(video_data, platforms, options)
        
        return jsonify({
            'message': 'Video published to CMS',
            'results': results,
            'video_id': video_data.get('video_id')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Analytics Configuration
@integrations_bp.route('/analytics/google/configure', methods=['POST'])
def configure_google_analytics():
    """Configure Google Analytics integration."""
    try:
        data = request.get_json()
        
        measurement_id = data.get('measurement_id')
        api_secret = data.get('api_secret')
        
        if not all([measurement_id, api_secret]):
            return jsonify({'error': 'measurement_id and api_secret are required'}), 400
        
        analytics_manager.configure_google_analytics(measurement_id, api_secret)
        
        return jsonify({
            'platform': 'google_analytics',
            'status': 'configured',
            'features': ['video_tracking', 'conversion_tracking', 'user_engagement']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@integrations_bp.route('/analytics/facebook/configure', methods=['POST'])
def configure_facebook_pixel():
    """Configure Facebook Pixel integration."""
    try:
        data = request.get_json()
        
        pixel_id = data.get('pixel_id')
        access_token = data.get('access_token')
        
        if not all([pixel_id, access_token]):
            return jsonify({'error': 'pixel_id and access_token are required'}), 400
        
        analytics_manager.configure_facebook_pixel(pixel_id, access_token)
        
        return jsonify({
            'platform': 'facebook_pixel',
            'status': 'configured',
            'features': ['conversion_tracking', 'video_views', 'custom_events']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@integrations_bp.route('/analytics/track', methods=['POST'])
def track_analytics_event():
    """Track analytics event across configured platforms."""
    try:
        data = request.get_json()
        
        event_type = data.get('event_type')
        event_data = data.get('event_data', {})
        user_data = data.get('user_data', {})
        platforms = data.get('platforms', [])
        
        if event_type in ['video_start', 'video_complete', 'video_generated']:
            results = analytics_manager.track_video_event(event_type, event_data, user_data, platforms)
        elif event_type in ['subscription', 'purchase', 'lead']:
            results = analytics_manager.track_conversion(event_type, event_data, platforms)
        else:
            return jsonify({'error': 'Unknown event type'}), 400
        
        return jsonify({
            'message': 'Event tracked',
            'event_type': event_type,
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@integrations_bp.route('/analytics/tracking-code/<platform>', methods=['GET'])
def get_tracking_code(platform):
    """Get client-side tracking code for analytics platforms."""
    try:
        tracking_code = analytics_manager.get_tracking_code(platform)
        
        if tracking_code:
            return jsonify({
                'platform': platform,
                'tracking_code': tracking_code,
                'content_type': 'text/html'
            })
        else:
            return jsonify({'error': 'Platform not configured or supported'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Integration Status and Health Check
@integrations_bp.route('/status', methods=['GET'])
def integration_status():
    """Get status of all integrations."""
    try:
        status = {
            'messaging': {
                'enabled_platforms': notification_manager.enabled_platforms,
                'features': ['slack', 'teams', 'discord']
            },
            'crm': {
                'enabled_platforms': crm_manager.enabled_crms,
                'features': ['salesforce', 'hubspot']
            },
            'cms': {
                'enabled_platforms': cms_manager.enabled_platforms,
                'features': ['wordpress', 'shopify']
            },
            'analytics': {
                'enabled_platforms': analytics_manager.enabled_platforms,
                'features': ['google_analytics', 'facebook_pixel']
            },
            'webhooks': {
                'registered_count': len(webhook_manager.list_webhooks()),
                'supported_events': webhook_manager.events
            },
            'zapier': {
                'triggers_registered': len(zapier_integration.subscriptions),
                'supported_events': ['video.generated', 'video.completed', 'user.registered']
            }
        }
        
        return jsonify({
            'status': 'active',
            'integrations': status,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500