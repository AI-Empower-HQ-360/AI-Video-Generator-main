# Cost Management System Documentation

## Overview

The Cost Management System provides comprehensive monitoring, optimization, and control of AI API costs for the AI Video Generator platform. It includes usage tracking, caching, user quotas, and intelligent cost optimization strategies.

## Features

### 1. Cost Tracking and Analytics
- Real-time cost calculation for all AI API calls
- Support for multiple models (GPT-4, GPT-3.5-turbo, Claude variants)
- Detailed analytics with breakdowns by user, model, and guru type
- Historical usage data with configurable retention periods

### 2. Intelligent Caching
- Automatic caching of API responses to reduce duplicate calls
- Configurable cache TTL (time-to-live) and size limits
- Cache hit rate monitoring and optimization suggestions
- MD5-based cache keys for consistent lookups

### 3. User Quota Management
- Per-user daily and monthly limits for tokens and costs
- Automatic quota resets (daily/monthly)
- Quota enforcement before API calls
- Flexible quota configuration per user

### 4. Cost Optimization
- Model selection optimization based on query type
- Prompt strategy recommendations
- Token usage estimation
- Cost-effective model suggestions

### 5. Alerting System
- Configurable cost thresholds
- Real-time alert generation
- Daily and monthly budget monitoring
- Email notifications (configurable)

## API Endpoints

### Cost Analytics
```http
GET /api/cost/analytics?user_id={user_id}&days={days}
```
Returns comprehensive cost analytics including:
- Total costs and token usage
- Model and guru type breakdowns
- Cache efficiency metrics
- Cost savings from caching

### User Quota Management
```http
GET /api/cost/quota/{user_id}
PUT /api/cost/quota/{user_id}
```
Get or update user quota settings:
- Daily/monthly token limits
- Daily/monthly cost limits
- Current usage status

### Optimization Suggestions
```http
POST /api/cost/optimize
```
Get cost optimization recommendations:
- Optimal model selection
- Estimated costs and token usage
- Prompt optimization suggestions

### Cache Management
```http
GET /api/cost/cache/stats
POST /api/cost/cache/clear
```
Monitor and manage the response cache:
- Cache utilization statistics
- Hit rate monitoring
- Manual cache clearing

### Cost Alerts
```http
GET /api/cost/alerts
```
Retrieve current cost alerts and threshold violations.

### Budget Recommendations
```http
GET /api/cost/budget/recommendations?user_id={user_id}
```
Get intelligent budget and optimization recommendations.

## Configuration

### Environment Variables

```bash
# Cost Management Settings
COST_DAILY_LIMIT=10.0              # Default daily cost limit (USD)
COST_MONTHLY_LIMIT=100.0           # Default monthly cost limit (USD)
TOKEN_DAILY_LIMIT=10000            # Default daily token limit
TOKEN_MONTHLY_LIMIT=100000         # Default monthly token limit
CACHE_TTL=3600                     # Cache time-to-live (seconds)
MAX_CACHE_SIZE=1000                # Maximum cache entries

# Alert Thresholds
ALERT_DAILY_COST_THRESHOLD=10.0    # Daily cost alert threshold
ALERT_MONTHLY_COST_THRESHOLD=100.0 # Monthly cost alert threshold
```

### Model Pricing

Current pricing per 1K tokens (USD):

| Model | Input | Output |
|-------|-------|--------|
| gpt-4 | $0.03 | $0.06 |
| gpt-4-32k | $0.06 | $0.12 |
| gpt-3.5-turbo | $0.0015 | $0.002 |
| gpt-3.5-turbo-16k | $0.003 | $0.004 |
| claude-3-opus | $0.015 | $0.075 |
| claude-3-sonnet | $0.003 | $0.015 |
| claude-3-haiku | $0.00025 | $0.00125 |

## Usage Examples

### Basic Cost Tracking

```python
from backend.services.ai_service import AIService

ai_service = AIService()

# Get spiritual guidance with cost tracking
response = await ai_service.get_spiritual_guidance(
    guru_type="spiritual",
    question="What is meditation?",
    user_id="user123"
)

print(f"Response: {response['response']}")
print(f"Cost: ${response['cost_usd']}")
print(f"Tokens used: {response['tokens_used']}")
print(f"Cached: {response['cached']}")
```

### Check User Quota

```python
# Check if user can make a request
quota_status = ai_service.get_user_quota_status("user123")

if quota_status["within_limits"]:
    # Proceed with request
    response = await ai_service.get_spiritual_guidance(...)
else:
    # Handle quota exceeded
    print("Daily quota exceeded")
    print(f"Remaining tokens: {quota_status['daily_tokens_remaining']}")
```

### Get Optimization Suggestions

```python
# Get cost optimization suggestions
suggestions = ai_service.get_prompt_optimization_suggestions(
    guru_type="meditation",
    question="How do I meditate effectively?"
)

print(f"Recommended model: {suggestions['optimal_strategy']['model']}")
print(f"Estimated cost: ${suggestions['estimated_cost']}")
for suggestion in suggestions['suggestions']:
    print(f"- {suggestion['message']}")
```

### Monitor Cache Performance

```python
# Get cache statistics
analytics = ai_service.get_cost_analytics(days=7)
print(f"Cache hit rate: {analytics['cache_hit_rate']}%")
print(f"Cost savings from cache: ${analytics['cost_savings_from_cache']}")
```

## Optimization Strategies

### 1. Model Selection
- Use `gpt-3.5-turbo` for general spiritual guidance (80% cost savings vs GPT-4)
- Use `gpt-4` for complex tasks like Sanskrit sloka interpretation
- Use `claude-3-haiku` for simple, fast responses

### 2. Prompt Optimization
- Keep prompts concise while maintaining clarity
- Use structured prompts for better token efficiency
- Leverage system prompts for context reduction

### 3. Caching Strategy
- Enable caching for frequently asked questions
- Use appropriate cache TTL based on content freshness needs
- Monitor cache hit rates and adjust strategies

### 4. User Education
- Provide cost feedback to users
- Suggest more cost-effective alternatives
- Encourage use of cached responses

## Monitoring and Alerts

### Cost Thresholds
The system monitors several cost thresholds:
- Daily cost limits per user
- Monthly cost limits per user
- Global daily/monthly spending
- Model-specific usage patterns

### Alert Types
1. **Daily Cost Exceeded**: User or system exceeds daily cost threshold
2. **Monthly Cost Exceeded**: User or system exceeds monthly cost threshold
3. **Low Cache Utilization**: Cache hit rate below optimal level
4. **High GPT-4 Usage**: Excessive use of expensive models

### Response Actions
- Block requests when hard limits are exceeded
- Send warnings when approaching limits
- Suggest optimization strategies
- Provide usage analytics for decision making

## Best Practices

### For Developers
1. Always pass `user_id` to track usage per user
2. Check quota status before expensive operations
3. Use caching for repeated or similar queries
4. Monitor cost analytics regularly
5. Implement graceful degradation when quotas are exceeded

### For System Administrators
1. Set appropriate default quotas based on user types
2. Monitor global cost trends and adjust thresholds
3. Review optimization recommendations regularly
4. Keep model pricing information up to date
5. Set up automated alerts for budget management

### For Users
1. Review cost breakdown in response data
2. Consider shorter, more focused questions
3. Check for similar questions that might be cached
4. Use appropriate guru types for different needs

## Troubleshooting

### Common Issues

**High Costs**
- Check model usage patterns
- Review prompt lengths and complexity
- Verify cache hit rates
- Consider quota adjustments

**Low Cache Hit Rates**
- Review question patterns for similarities
- Adjust cache TTL settings
- Encourage users to check FAQ first

**Quota Exceeded Errors**
- Check current usage against limits
- Verify quota reset timing
- Consider temporary quota increases

**Missing Cost Data**
- Verify data persistence configuration
- Check file permissions for data directory
- Review error logs for save/load issues

## Integration Examples

### Frontend Integration

```javascript
// Check quota before making request
const checkQuota = async (userId) => {
    const response = await fetch(`/api/cost/quota/${userId}`);
    const data = await response.json();
    return data.quota_status.within_limits;
};

// Get optimization suggestions
const getOptimizations = async (guruType, question) => {
    const response = await fetch('/api/cost/optimize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ guru_type: guruType, question })
    });
    return await response.json();
};

// Display cost information
const displayCostInfo = (response) => {
    if (response.cached) {
        console.log('✅ Response served from cache (no cost)');
    } else {
        console.log(`💰 Cost: $${response.cost_usd}`);
        console.log(`🎯 Tokens: ${response.tokens_used}`);
    }
};
```

### Monitoring Dashboard

```python
# Create a simple monitoring dashboard
def get_dashboard_data():
    analytics = ai_service.get_cost_analytics(days=30)
    alerts = ai_service.get_cost_alerts()
    
    return {
        'total_cost': analytics['total_cost'],
        'total_requests': analytics['total_requests'],
        'cache_hit_rate': analytics['cache_hit_rate'],
        'active_alerts': len(alerts),
        'top_models': sorted(
            analytics['model_breakdown'].items(),
            key=lambda x: x[1]['cost'],
            reverse=True
        )[:5]
    }
```

## Security Considerations

1. **API Key Protection**: Never expose API keys in client-side code
2. **User Authentication**: Verify user identity before quota operations
3. **Data Privacy**: Ensure usage data is properly anonymized
4. **Rate Limiting**: Implement additional rate limiting to prevent abuse
5. **Audit Logging**: Log all quota changes and administrative actions

## Performance Optimization

1. **Database Indexing**: Index frequently queried fields (user_id, timestamp)
2. **Data Retention**: Implement automatic cleanup of old usage data
3. **Caching Strategy**: Use Redis for production cache storage
4. **Batch Operations**: Batch database writes for better performance
5. **Async Processing**: Use async operations for non-blocking responses