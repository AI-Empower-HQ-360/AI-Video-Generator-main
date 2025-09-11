"""
Tests for third-party integrations.
"""

import pytest
import json
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# Test data
sample_video_data = {
    'video_id': 'test_vid_123',
    'title': 'Test Spiritual Video',
    'duration': 120,
    'url': 'https://example.com/test-video.mp4',
    'thumbnail': 'https://example.com/test-thumb.jpg',
    'guru': 'spiritual',
    'created_at': datetime.utcnow().isoformat()
}

sample_user_data = {
    'user_id': 'test_user_456',
    'email': 'test@example.com',
    'first_name': 'Test',
    'last_name': 'User',
    'subscription_type': 'free'
}


class TestWebhookSystem:
    """Test webhook functionality."""
    
    def test_webhook_registration(self):
        """Test webhook registration."""
        from integrations.webhook_system import WebhookManager
        
        manager = WebhookManager()
        webhook_id = manager.register_webhook(
            'https://example.com/webhook',
            ['video.generated'],
            'secret123'
        )
        
        assert webhook_id is not None
        assert len(webhook_id) > 0
        
        webhook = manager.get_webhook(webhook_id)
        assert webhook['url'] == 'https://example.com/webhook'
        assert 'video.generated' in webhook['events']
        assert webhook['secret'] == 'secret123'
    
    @patch('requests.post')
    def test_webhook_delivery(self, mock_post):
        """Test webhook delivery."""
        from integrations.webhook_system import WebhookManager
        
        mock_post.return_value.status_code = 200
        
        manager = WebhookManager()
        webhook_id = manager.register_webhook(
            'https://example.com/webhook',
            ['video.generated']
        )
        
        manager.trigger_webhook('video.generated', sample_video_data)
        
        # Verify webhook was called
        assert mock_post.called
        
        # Verify payload
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        
        assert payload['event'] == 'video.generated'
        assert payload['data'] == sample_video_data
        assert 'timestamp' in payload


class TestZapierIntegration:
    """Test Zapier integration."""
    
    def test_trigger_registration(self):
        """Test Zapier trigger registration."""
        from integrations.zapier_integration import ZapierIntegration
        
        zapier = ZapierIntegration()
        trigger_id = zapier.register_trigger(
            'video.generated',
            'https://hooks.zapier.com/hooks/catch/123/abc/'
        )
        
        assert trigger_id is not None
        assert trigger_id.startswith('zapier_')
        
        subscription = zapier.subscriptions[trigger_id]
        assert subscription['event'] == 'video.generated'
        assert subscription['active'] is True
    
    @patch('requests.post')
    def test_zapier_trigger_event(self, mock_post):
        """Test Zapier event triggering."""
        from integrations.zapier_integration import ZapierIntegration
        
        mock_post.return_value.status_code = 200
        
        zapier = ZapierIntegration()
        zapier.register_trigger(
            'video.generated',
            'https://hooks.zapier.com/hooks/catch/123/abc/'
        )
        
        zapier.trigger_event('video.generated', sample_video_data)
        
        assert mock_post.called
        
        # Verify payload format
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        
        assert 'timestamp' in payload
        assert 'platform' in payload
        assert payload['video_id'] == sample_video_data['video_id']
    
    def test_sample_data_generation(self):
        """Test sample data for Zapier setup."""
        from integrations.zapier_integration import ZapierIntegration
        
        zapier = ZapierIntegration()
        sample = zapier.get_sample_data('video.generated')
        
        assert 'video_id' in sample
        assert 'title' in sample
        assert 'duration' in sample
        assert 'url' in sample


class TestMessagingBots:
    """Test messaging bot integrations."""
    
    @patch('requests.post')
    def test_slack_notification(self, mock_post):
        """Test Slack notification sending."""
        from integrations.messaging_bots import SlackBot
        
        mock_post.return_value.status_code = 200
        
        slack_bot = SlackBot(webhook_url='https://hooks.slack.com/test')
        result = slack_bot.send_video_notification('#test', sample_video_data)
        
        assert result is True
        assert mock_post.called
        
        # Verify payload structure
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        
        assert 'blocks' in payload
        assert len(payload['blocks']) > 0
    
    @patch('requests.post')
    def test_teams_notification(self, mock_post):
        """Test Teams notification sending."""
        from integrations.messaging_bots import TeamsBot
        
        mock_post.return_value.status_code = 200
        
        teams_bot = TeamsBot(webhook_url='https://outlook.office.com/test')
        result = teams_bot.send_video_notification(sample_video_data)
        
        assert result is True
        assert mock_post.called
        
        # Verify MessageCard format
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        
        assert payload['@type'] == 'MessageCard'
        assert 'sections' in payload
    
    @patch('requests.post')
    def test_discord_notification(self, mock_post):
        """Test Discord notification sending."""
        from integrations.messaging_bots import DiscordBot
        
        mock_post.return_value.status_code = 200
        
        discord_bot = DiscordBot(webhook_url='https://discord.com/api/webhooks/test')
        result = discord_bot.send_video_notification(sample_video_data)
        
        assert result is True
        assert mock_post.called
        
        # Verify embed format
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        
        assert 'embeds' in payload
        assert len(payload['embeds']) > 0


class TestCRMIntegrations:
    """Test CRM integration functionality."""
    
    @patch('requests.post')
    def test_salesforce_lead_creation(self, mock_post):
        """Test Salesforce lead creation."""
        from integrations.crm_integrations import SalesforceIntegration
        
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {'id': 'lead_123'}
        mock_post.return_value = mock_response
        
        sf = SalesforceIntegration(
            'https://test.salesforce.com',
            'test_token'
        )
        
        lead_id = sf.create_lead(sample_user_data)
        
        assert lead_id == 'lead_123'
        assert mock_post.called
    
    @patch('requests.post')
    def test_hubspot_contact_creation(self, mock_post):
        """Test HubSpot contact creation."""
        from integrations.crm_integrations import HubSpotIntegration
        
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {'id': 'contact_456'}
        mock_post.return_value = mock_response
        
        hs = HubSpotIntegration('test_api_key')
        contact_id = hs.create_contact(sample_user_data)
        
        assert contact_id == 'contact_456'
        assert mock_post.called


class TestAnalyticsIntegrations:
    """Test analytics tracking functionality."""
    
    @patch('requests.post')
    def test_google_analytics_tracking(self, mock_post):
        """Test Google Analytics event tracking."""
        from integrations.analytics_tracking import GoogleAnalyticsIntegration
        
        mock_post.return_value.status_code = 204
        
        ga = GoogleAnalyticsIntegration('G-TEST123', 'secret123')
        result = ga.track_video_event('video_start', sample_video_data, sample_user_data)
        
        assert result is True
        assert mock_post.called
        
        # Verify event format
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        
        assert 'client_id' in payload
        assert 'events' in payload
        assert len(payload['events']) > 0
    
    @patch('requests.post')
    def test_facebook_pixel_tracking(self, mock_post):
        """Test Facebook Pixel event tracking."""
        from integrations.analytics_tracking import FacebookPixelIntegration
        
        mock_post.return_value.status_code = 200
        
        fb = FacebookPixelIntegration('123456789', 'test_token')
        result = fb.track_video_view(sample_video_data, sample_user_data)
        
        assert result is True
        assert mock_post.called
        
        # Verify event format
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        
        assert 'data' in payload
        assert len(payload['data']) > 0
        assert payload['data'][0]['event_name'] == 'ViewContent'


class TestIntegrationHelpers:
    """Test integration helper functions."""
    
    @patch('threading.Thread')
    def test_video_generated_trigger(self, mock_thread):
        """Test video generation trigger."""
        from integrations.integration_helpers import IntegrationTrigger
        
        IntegrationTrigger.on_video_generated(sample_video_data, sample_user_data)
        
        # Verify thread was started
        assert mock_thread.called
        
        # Get the target function
        call_args = mock_thread.call_args
        target_func = call_args[1]['target']
        
        # Verify it's a function
        assert callable(target_func)
    
    def test_integration_status(self):
        """Test integration status reporting."""
        from integrations.integration_helpers import IntegrationConfig
        
        status = IntegrationConfig.get_integration_status()
        
        assert 'messaging' in status
        assert 'crm' in status
        assert 'cms' in status
        assert 'analytics' in status
        assert 'webhooks' in status
    
    def test_available_integrations_list(self):
        """Test available integrations listing."""
        from integrations.integration_helpers import IntegrationConfig
        
        integrations = IntegrationConfig.get_available_integrations()
        
        assert len(integrations) > 0
        
        # Check for key integrations
        integration_names = [i['name'] for i in integrations]
        
        assert 'Zapier' in integration_names
        assert 'Slack' in integration_names
        assert 'Salesforce' in integration_names
        assert 'WordPress' in integration_names
        assert 'Google Analytics' in integration_names


class TestCMSIntegrations:
    """Test CMS integration functionality."""
    
    @patch('requests.post')
    def test_wordpress_post_creation(self, mock_post):
        """Test WordPress post creation."""
        from integrations.cms_plugins import WordPressPlugin
        
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {'id': 123}
        mock_post.return_value = mock_response
        
        wp = WordPressPlugin('https://test.com', 'user', 'pass')
        post_id = wp.create_video_post(sample_video_data)
        
        assert post_id == '123'
        assert mock_post.called
    
    @patch('requests.post')
    def test_shopify_product_video(self, mock_post):
        """Test Shopify product video creation."""
        from integrations.cms_plugins import ShopifyIntegration
        
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {'id': 456}
        mock_post.return_value = mock_response
        
        shopify = ShopifyIntegration('testshop', 'token123')
        result = shopify.create_product_video('prod_123', sample_video_data)
        
        assert result == {'id': 456}
        assert mock_post.called


# Integration endpoint tests would require Flask test client
# These can be added when running the full application test suite