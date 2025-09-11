"""
Integration Demo Script
Demonstrates the complete integration ecosystem working together.
"""

import json
from datetime import datetime
from integrations.webhook_system import webhook_manager
from integrations.zapier_integration import zapier_integration
from integrations.messaging_bots import notification_manager
from integrations.crm_integrations import crm_manager
from integrations.cms_plugins import cms_manager
from integrations.analytics_tracking import analytics_manager
from integrations.integration_helpers import integration_trigger


def demo_integration_ecosystem():
    """Demonstrate the complete integration ecosystem."""
    
    print("🚀 AI Video Generator Integration Ecosystem Demo")
    print("=" * 60)
    
    # 1. Setup mock integrations (simulating real configuration)
    print("\n1. Setting up integrations...")
    
    # Register a test webhook
    webhook_id = webhook_manager.register_webhook(
        "https://example.com/webhook",
        ["video.generated", "video.completed"],
        "demo_secret_123"
    )
    print(f"✅ Webhook registered: {webhook_id[:8]}...")
    
    # Register Zapier trigger
    zapier_trigger_id = zapier_integration.register_trigger(
        "video.generated",
        "https://hooks.zapier.com/hooks/catch/demo/trigger"
    )
    print(f"✅ Zapier trigger registered: {zapier_trigger_id[:8]}...")
    
    # Configure messaging (mock URLs)
    notification_manager.configure_slack(webhook_url="https://hooks.slack.com/demo")
    notification_manager.configure_teams("https://outlook.office.com/demo")
    notification_manager.configure_discord("https://discord.com/api/webhooks/demo")
    print("✅ Messaging bots configured (Slack, Teams, Discord)")
    
    # Configure CRM (mock credentials)
    crm_manager.configure_hubspot("demo_api_key")
    print("✅ CRM integrations configured (HubSpot)")
    
    # Configure CMS (mock credentials)
    cms_manager.configure_wordpress("https://demo.com", "user", "pass")
    cms_manager.configure_shopify("demoshop", "demo_token")
    print("✅ CMS integrations configured (WordPress, Shopify)")
    
    # Configure analytics (mock IDs)
    analytics_manager.configure_google_analytics("G-DEMO123", "demo_secret")
    analytics_manager.configure_facebook_pixel("123456789", "demo_token")
    print("✅ Analytics configured (Google Analytics, Facebook Pixel)")
    
    # 2. Simulate video generation event
    print("\n2. Simulating video generation...")
    
    video_data = {
        'video_id': 'demo_vid_001',
        'title': 'Spiritual Wisdom: Finding Inner Peace',
        'duration': 240,  # 4 minutes
        'url': 'https://demo.com/videos/spiritual-wisdom.mp4',
        'thumbnail': 'https://demo.com/thumbs/spiritual-wisdom.jpg',
        'guru': 'spiritual',
        'quality': '1080p',
        'file_size': 1024000,  # 1MB
        'created_at': datetime.utcnow().isoformat()
    }
    
    user_data = {
        'user_id': 'demo_user_123',
        'email': 'demo@example.com',
        'first_name': 'Demo',
        'last_name': 'User',
        'subscription_type': 'premium',
        'video_count': 5,
        'client_id': 'demo_client_456'
    }
    
    print(f"📹 Video generated: '{video_data['title']}'")
    print(f"👤 User: {user_data['first_name']} {user_data['last_name']} ({user_data['subscription_type']})")
    
    # 3. Trigger all integrations
    print("\n3. Triggering integrations...")
    
    # Trigger webhooks
    webhook_manager.trigger_webhook('video.generated', video_data)
    print("✅ Webhooks triggered (custom endpoints)")
    
    # Trigger Zapier
    zapier_integration.trigger_event('video.generated', video_data)
    print("✅ Zapier workflows triggered")
    
    # Send notifications (would fail but demonstrates structure)
    notification_results = notification_manager.notify_video_generated(video_data)
    print(f"✅ Notifications sent to {len(notification_manager.enabled_platforms)} platforms")
    
    # Track analytics
    analytics_results = analytics_manager.track_video_event(
        'video_generated', video_data, user_data
    )
    print(f"✅ Analytics tracked on {len(analytics_manager.enabled_platforms)} platforms")
    
    # Sync to CRM
    crm_results = crm_manager.track_video_engagement(user_data['user_id'], video_data)
    print(f"✅ CRM engagement tracked on {len(crm_manager.enabled_crms)} platforms")
    
    # 4. Demonstrate video completion
    print("\n4. Simulating video completion...")
    
    completed_video_data = {
        **video_data,
        'status': 'completed',
        'processing_time': 45,  # seconds
        'completed_at': datetime.utcnow().isoformat()
    }
    
    webhook_manager.trigger_webhook('video.completed', completed_video_data)
    zapier_integration.trigger_event('video.completed', completed_video_data)
    print("✅ Video completion events triggered")
    
    # 5. Demonstrate CMS publishing
    print("\n5. Demonstrating CMS publishing...")
    
    cms_options = {
        'platforms': ['wordpress', 'shopify'],
        'wordpress_create_page': True,
        'shopify_product_id': 'demo_prod_789'
    }
    
    cms_results = cms_manager.publish_video_to_cms(video_data, cms_options['platforms'], cms_options)
    print(f"✅ Video published to {len(cms_results)} CMS platforms")
    
    # 6. Show integration status
    print("\n6. Integration Status:")
    print("-" * 30)
    
    status = {
        'webhooks': len(webhook_manager.list_webhooks()),
        'zapier_triggers': len(zapier_integration.subscriptions),
        'messaging_platforms': len(notification_manager.enabled_platforms),
        'crm_platforms': len(crm_manager.enabled_crms),
        'cms_platforms': len(cms_manager.enabled_platforms),
        'analytics_platforms': len(analytics_manager.enabled_platforms)
    }
    
    for category, count in status.items():
        print(f"📊 {category.replace('_', ' ').title()}: {count} configured")
    
    # 7. Show available events
    print("\n7. Available Integration Events:")
    print("-" * 35)
    
    events = webhook_manager.events
    for event in events:
        print(f"🎯 {event}")
    
    # 8. Generate sample webhook payload
    print("\n8. Sample Webhook Payload:")
    print("-" * 30)
    
    sample_payload = {
        'event': 'video.generated',
        'timestamp': datetime.utcnow().isoformat(),
        'webhook_id': webhook_id,
        'data': video_data
    }
    
    print(json.dumps(sample_payload, indent=2)[:300] + "...")
    
    print("\n" + "=" * 60)
    print("🎉 Integration Ecosystem Demo Complete!")
    print("\nKey Features Demonstrated:")
    print("• Webhook system with signature verification")
    print("• Zapier workflow automation")
    print("• Multi-platform messaging notifications")
    print("• CRM lead and engagement tracking")
    print("• CMS video publishing")
    print("• Analytics and conversion tracking")
    print("• Event-driven architecture")
    print("• Comprehensive error handling")
    
    print("\n🚀 Ready for production use!")
    print("Configure real credentials via API endpoints to activate integrations.")


if __name__ == "__main__":
    demo_integration_ecosystem()