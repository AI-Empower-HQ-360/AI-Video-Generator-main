"""
Example usage of AI Video Generator integrations.
This demonstrates how to use the integration ecosystem in your application.
"""

from datetime import datetime
from integrations.integration_helpers import integration_trigger, integration_config

# Example: When a video is generated
def on_video_generated_example():
    """Example of triggering integrations when a video is generated."""
    
    # Sample video data
    video_data = {
        'video_id': 'vid_12345',
        'title': 'Spiritual Meditation Guide',
        'duration': 180,  # 3 minutes
        'url': 'https://yourvideo.com/spiritual-meditation.mp4',
        'thumbnail': 'https://yourvideo.com/thumb/spiritual-meditation.jpg',
        'guru': 'meditation',
        'quality': '1080p',
        'created_at': datetime.utcnow().isoformat()
    }
    
    # Sample user data
    user_data = {
        'user_id': 'user_67890',
        'email': 'user@example.com',
        'first_name': 'John',
        'last_name': 'Doe',
        'subscription_type': 'premium',
        'video_count': 15
    }
    
    # Trigger all integrations automatically
    integration_trigger.on_video_generated(video_data, user_data)
    
    print("✅ Video generation integrations triggered!")
    print("- Webhooks sent to registered endpoints")
    print("- Zapier workflows activated")
    print("- Slack/Teams/Discord notifications sent")
    print("- Analytics events tracked")
    print("- CRM engagement logged")


# Example: When a user subscribes
def on_subscription_example():
    """Example of triggering integrations when a user subscribes."""
    
    subscription_data = {
        'user_id': 'user_67890',
        'plan_name': 'Premium Monthly',
        'amount': 29.99,
        'currency': 'USD',
        'transaction_id': 'txn_abc123',
        'user_data': {
            'email': 'user@example.com',
            'first_name': 'John',
            'last_name': 'Doe'
        },
        'page_url': 'https://yourdomain.com/checkout'
    }
    
    # Trigger subscription integrations
    integration_trigger.on_subscription_purchased(subscription_data)
    
    print("✅ Subscription integrations triggered!")
    print("- Conversion tracking sent to analytics")
    print("- CRM opportunities created")
    print("- Webhooks notified of subscription")


# Example: Manual CMS publishing
def publish_to_cms_example():
    """Example of manually publishing video to CMS platforms."""
    
    video_data = {
        'video_id': 'vid_12345',
        'title': 'Spiritual Meditation Guide',
        'duration': 180,
        'url': 'https://yourvideo.com/spiritual-meditation.mp4',
        'thumbnail': 'https://yourvideo.com/thumb/spiritual-meditation.jpg',
        'description': 'A peaceful meditation guide for spiritual growth.',
        'guru': 'meditation'
    }
    
    # CMS publishing options
    cms_options = {
        'platforms': ['wordpress', 'shopify'],
        'wordpress_create_page': True,
        'wordpress_status': 'publish',
        'shopify_product_id': 'prod_987654',
        'shopify_update_description': True
    }
    
    # Publish to CMS platforms
    results = integration_trigger.publish_video_to_cms(video_data, cms_options)
    
    print("✅ Video published to CMS platforms!")
    for platform, result in results.items():
        if result.get('success'):
            print(f"- {platform}: Successfully published")
        else:
            print(f"- {platform}: Publishing failed")


# Example: Check integration status
def check_integration_status():
    """Example of checking integration status."""
    
    status = integration_config.get_integration_status()
    
    print("🔍 Integration Status:")
    print(f"- Messaging: {status['messaging']}")
    print(f"- CRM: {status['crm']}")
    print(f"- CMS: {status['cms']}")
    print(f"- Analytics: {status['analytics']}")
    print(f"- Webhooks: {status['webhooks']['total_registered']} registered")


# Example: List available integrations
def list_available_integrations():
    """Example of listing available integrations."""
    
    integrations = integration_config.get_available_integrations()
    
    print("📋 Available Integrations:")
    
    categories = {}
    for integration in integrations:
        category = integration['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(integration)
    
    for category, items in categories.items():
        print(f"\n{category.upper()}:")
        for item in items:
            print(f"  - {item['name']}: {', '.join(item['features'])}")


if __name__ == "__main__":
    print("🚀 AI Video Generator Integration Examples")
    print("=" * 50)
    
    # Run examples
    print("\n1. Video Generation Integration:")
    on_video_generated_example()
    
    print("\n2. Subscription Integration:")
    on_subscription_example()
    
    print("\n3. CMS Publishing:")
    publish_to_cms_example()
    
    print("\n4. Integration Status:")
    check_integration_status()
    
    print("\n5. Available Integrations:")
    list_available_integrations()
    
    print("\n🎉 Integration examples completed!")
    print("\nTo use these integrations in your application:")
    print("1. Configure each integration via the API endpoints")
    print("2. Call integration_trigger methods when events occur")
    print("3. Monitor integration status for debugging")
    print("4. Use webhook system for custom integrations")