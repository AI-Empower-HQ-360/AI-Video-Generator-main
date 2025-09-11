# AI Video Generator - Third-Party Integrations

This document provides comprehensive information about the extensive third-party integrations available in the AI Video Generator platform.

## 🔗 Available Integrations

### Workflow Automation
- **Zapier** - Connect with 5000+ apps and automate video workflows
- **Custom Webhooks** - Build custom integrations with your own endpoints

### Communication & Notifications
- **Slack** - Get video notifications in your team channels
- **Microsoft Teams** - Workplace video sharing and notifications
- **Discord** - Community video sharing and bot integration

### CRM Integration
- **Salesforce** - Track leads and video engagement
- **HubSpot** - Manage contacts and video interactions

### CMS & E-commerce
- **WordPress** - Embed videos in posts and pages
- **Shopify** - Add AI-generated videos to products

### Analytics & Tracking
- **Google Analytics** - Track video metrics and conversions
- **Facebook Pixel** - Monitor ad conversions and video views

## 🚀 Quick Start

### 1. Configure Integrations

Each integration can be configured via the API:

```bash
# Configure Slack notifications
curl -X POST /api/integrations/messaging/slack/configure \
  -H "Content-Type: application/json" \
  -d '{"webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"}'

# Configure Google Analytics
curl -X POST /api/integrations/analytics/google/configure \
  -H "Content-Type: application/json" \
  -d '{"measurement_id": "G-XXXXXXXXXX", "api_secret": "your-api-secret"}'
```

### 2. Trigger Events

Integrations are automatically triggered when events occur:

```python
from integrations.integration_helpers import integration_trigger

# When a video is generated
video_data = {
    'video_id': 'vid_123',
    'title': 'My Spiritual Video',
    'duration': 120,
    'url': 'https://example.com/video.mp4'
}

integration_trigger.on_video_generated(video_data, user_data)
```

### 3. Manual Publishing

You can also manually publish videos to CMS platforms:

```python
cms_options = {
    'platforms': ['wordpress', 'shopify'],
    'wordpress_create_page': True,
    'shopify_product_id': 'prod_123'
}

results = integration_trigger.publish_video_to_cms(video_data, cms_options)
```

## 📋 Integration Details

### Zapier Integration

**Features:**
- Automatic trigger creation for video events
- Action handlers for video creation
- Sample data for trigger setup

**Supported Events:**
- `video.generated` - When a new video is created
- `video.completed` - When video processing finishes
- `user.registered` - When a new user signs up

**Setup:**
1. Create a Zap in Zapier
2. Choose "AI Video Generator" as trigger app
3. Configure webhook URL via API
4. Test with sample data

### Slack Bot Integration

**Features:**
- Rich message formatting with video thumbnails
- Interactive buttons for video actions
- Channel-specific notifications

**Setup:**
1. Create a Slack app in your workspace
2. Generate bot token or webhook URL
3. Configure via `/api/integrations/messaging/slack/configure`

**Message Format:**
```
🎥 New Video Generated!
My Spiritual Video

Duration: 120 seconds
Guru: Spiritual

[Watch Video] (button)
```

### CRM Integrations

#### Salesforce
**Features:**
- Lead creation from video engagement
- Opportunity tracking for premium upgrades
- Activity logging for video interactions

**Required Fields:**
- Instance URL
- Client ID/Secret
- Username/Password

#### HubSpot
**Features:**
- Contact management
- Deal pipeline tracking
- Timeline events for video engagement

**Required Fields:**
- API Key

### CMS Integrations

#### WordPress
**Features:**
- Automatic post/page creation
- Video shortcode generation
- Custom meta fields

**Shortcode Example:**
```
[ai_video id="vid_123" url="https://example.com/video.mp4"]
```

#### Shopify
**Features:**
- Product video attachments
- Automated description updates
- Video collections

**Implementation:**
- Videos stored as product metafields
- Automatic thumbnail generation
- Collection management

### Analytics Integrations

#### Google Analytics (GA4)
**Tracked Events:**
- `video_start` - Video playback begins
- `video_complete` - Video watched to completion
- `video_share` - Video shared
- `purchase` - Subscription purchases

#### Facebook Pixel
**Tracked Events:**
- `ViewContent` - Video views
- `Subscribe` - Subscription conversions
- `Lead` - Lead generation

## 🔧 Configuration Examples

### Environment Variables
```bash
# Slack
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...

# Salesforce
SALESFORCE_INSTANCE_URL=https://yourinstance.salesforce.com
SALESFORCE_CLIENT_ID=your-client-id
SALESFORCE_CLIENT_SECRET=your-client-secret

# Google Analytics
GA_MEASUREMENT_ID=G-XXXXXXXXXX
GA_API_SECRET=your-api-secret

# Facebook Pixel
FB_PIXEL_ID=123456789
FB_ACCESS_TOKEN=your-access-token
```

### JSON Configuration
```json
{
  "integrations": {
    "messaging": {
      "slack": {
        "enabled": true,
        "webhook_url": "https://hooks.slack.com/services/...",
        "default_channel": "#videos"
      },
      "teams": {
        "enabled": true,
        "webhook_url": "https://outlook.office.com/webhook/..."
      }
    },
    "crm": {
      "salesforce": {
        "enabled": true,
        "instance_url": "https://yourinstance.salesforce.com"
      },
      "hubspot": {
        "enabled": true,
        "api_key": "your-api-key"
      }
    },
    "analytics": {
      "google_analytics": {
        "enabled": true,
        "measurement_id": "G-XXXXXXXXXX"
      },
      "facebook_pixel": {
        "enabled": true,
        "pixel_id": "123456789"
      }
    }
  }
}
```

## 📊 Webhook Events

### Event Types
- `video.generated` - New video created
- `video.completed` - Video processing finished
- `video.failed` - Video generation failed
- `user.registered` - New user signup
- `session.started` - User session began
- `session.completed` - User session ended

### Webhook Payload Example
```json
{
  "event": "video.generated",
  "timestamp": "2024-01-15T10:30:00Z",
  "webhook_id": "wh_abc123",
  "data": {
    "video_id": "vid_123456",
    "title": "Spiritual Guidance Video",
    "duration": 120,
    "url": "https://example.com/video.mp4",
    "thumbnail": "https://example.com/thumb.jpg",
    "guru": "spiritual",
    "user_id": "user_789",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### Webhook Security
- HMAC-SHA256 signature verification
- Configurable secrets per webhook
- Automatic retry logic
- Delivery status tracking

## 🔍 Monitoring & Analytics

### Integration Status Endpoint
```bash
GET /api/integrations/status
```

**Response:**
```json
{
  "status": "active",
  "integrations": {
    "messaging": {
      "enabled_platforms": ["slack", "teams"],
      "features": ["slack", "teams", "discord"]
    },
    "crm": {
      "enabled_platforms": ["hubspot"],
      "features": ["salesforce", "hubspot"]
    },
    "webhooks": {
      "registered_count": 5,
      "supported_events": ["video.generated", "video.completed", ...]
    }
  }
}
```

### Delivery Tracking
- Webhook delivery success/failure rates
- Integration response times
- Error logging and debugging
- Automatic retry mechanisms

## 🛠️ Troubleshooting

### Common Issues

1. **Webhook Not Receiving Data**
   - Check webhook URL accessibility
   - Verify event subscription
   - Review webhook signature verification

2. **CRM Sync Failures**
   - Validate API credentials
   - Check rate limiting
   - Review field mapping

3. **Analytics Not Tracking**
   - Verify tracking IDs
   - Check client-side implementation
   - Review event parameter format

### Debug Endpoints
```bash
# Test webhook delivery
POST /api/integrations/webhooks/test

# Get integration status
GET /api/integrations/status

# Test specific integrations
POST /api/integrations/messaging/notify
POST /api/integrations/analytics/track
```

## 📚 API Reference

All integration endpoints are available under `/api/integrations/`:

- **Webhooks:** `/webhooks`
- **Zapier:** `/zapier`
- **Messaging:** `/messaging`
- **CRM:** `/crm`
- **CMS:** `/cms`
- **Analytics:** `/analytics`

Each endpoint supports standard REST operations (GET, POST, PUT, DELETE) where applicable.

## 🤝 Support

For integration support:
1. Check the integration status endpoint
2. Review webhook delivery logs
3. Test with sample data
4. Contact support with integration details

## 🚀 Future Integrations

Coming soon:
- **LinkedIn** - Professional video sharing
- **Instagram** - Social media publishing
- **Mailchimp** - Email marketing automation
- **Stripe** - Enhanced payment tracking
- **Notion** - Knowledge base integration