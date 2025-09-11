# AI Provider Limitations and Error Handling

## Overview

The AI Empower Heart Platform primarily uses OpenAI's GPT models for spiritual guidance generation. This document outlines the limitations, constraints, and error handling strategies for AI providers integrated into the platform.

## OpenAI Integration

### API Limits and Constraints

#### Rate Limits

OpenAI enforces various rate limits depending on your plan and usage tier:

**Free Tier:**
- **Requests per minute (RPM):** 3 for GPT-4, 20 for GPT-3.5-turbo
- **Tokens per minute (TPM):** 40,000 for GPT-4, 90,000 for GPT-3.5-turbo
- **Requests per day (RPD):** 200 for GPT-4, 10,000 for GPT-3.5-turbo

**Pay-as-you-go ($5+ spent):**
- **RPM:** 500 for GPT-4, 3,500 for GPT-3.5-turbo
- **TPM:** 150,000 for GPT-4, 350,000 for GPT-3.5-turbo
- **RPD:** No limit

**Current Implementation:**
```python
# Rate limiting handling in ai_service.py
for attempt in range(self.max_retries):
    try:
        response = await self._create_completion(...)
        return response
    except openai.RateLimitError:
        if attempt == self.max_retries - 1:
            raise
        # Exponential backoff: 1s, 2s, 3s
        await asyncio.sleep(self.retry_delay * (attempt + 1))
```

#### Token Limits

**Context Window Limitations:**
- **GPT-4:** 8,192 tokens (~6,000 words)
- **GPT-3.5-turbo:** 4,096 tokens (~3,000 words)  
- **GPT-4-32k:** 32,768 tokens (~24,000 words)

**Token Counting:**
```python
import tiktoken

def count_tokens(text, model="gpt-4"):
    """Count tokens in text for specific model."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

# Example usage
question_tokens = count_tokens(user_question)
context_tokens = count_tokens(user_context)
total_tokens = question_tokens + context_tokens + 800  # Reserve for response

if total_tokens > 8000:  # Leave buffer for GPT-4
    # Implement truncation or summarization
    user_context = summarize_context(user_context)
```

#### Cost Considerations

**Pricing (as of 2024):**
- **GPT-4:** $0.03/1K input tokens, $0.06/1K output tokens
- **GPT-3.5-turbo:** $0.0015/1K input tokens, $0.002/1K output tokens

**Cost Management Strategies:**
```python
class CostTracker:
    def __init__(self):
        self.total_tokens = 0
        self.estimated_cost = 0.0
        
    def track_usage(self, input_tokens, output_tokens, model):
        rates = {
            'gpt-4': {'input': 0.00003, 'output': 0.00006},
            'gpt-3.5-turbo': {'input': 0.0000015, 'output': 0.000002}
        }
        
        cost = (input_tokens * rates[model]['input'] + 
                output_tokens * rates[model]['output'])
        
        self.total_tokens += input_tokens + output_tokens
        self.estimated_cost += cost
        
        return cost
```

### Error Types and Handling

#### Authentication Errors

**Error Code:** `401 Unauthorized`

**Cause:** Invalid or missing API key

**Implementation:**
```python
class AIService:
    def __init__(self):
        self.api_key = os.environ.get('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        # Validate API key format
        if not self.api_key.startswith('sk-'):
            raise ValueError("Invalid OpenAI API key format")
```

**User-Facing Error:**
```json
{
  "success": false,
  "error": "AI service authentication failed. Please check configuration.",
  "error_type": "AuthenticationError",
  "user_message": "We're experiencing technical difficulties. Please try again later.",
  "support_contact": "support@empowerhub360.org"
}
```

#### Rate Limit Errors

**Error Code:** `429 Too Many Requests`

**Cause:** Exceeded API rate limits

**Implementation:**
```python
async def handle_rate_limit(self, error, attempt):
    """Handle rate limiting with exponential backoff and user feedback."""
    
    # Extract retry-after header if available
    retry_after = getattr(error, 'retry_after', None) or (attempt + 1)
    
    # Log for monitoring
    logger.warning(f"Rate limit hit. Retrying in {retry_after}s. Attempt {attempt}/{self.max_retries}")
    
    # User-friendly message
    if attempt < self.max_retries:
        await asyncio.sleep(retry_after)
        return True  # Retry
    else:
        raise ServiceUnavailableError(
            "High demand detected. Please try again in a few minutes.",
            retry_after=retry_after
        )
```

**User-Facing Response:**
```json
{
  "success": false,
  "error": "Service temporarily busy due to high demand",
  "error_type": "RateLimitError",
  "retry_after": 60,
  "user_message": "Many users are seeking guidance right now. Please try again in a moment.",
  "alternative_action": "Browse our meditation library while you wait"
}
```

#### Content Policy Violations

**Error Code:** `400 Bad Request` with content policy flag

**Cause:** Input violates OpenAI's usage policies

**Implementation:**
```python
def sanitize_input(self, text):
    """Sanitize user input to prevent policy violations."""
    
    # Remove potentially harmful content
    prohibited_patterns = [
        r'\b(harm|violence|illegal)\b',
        r'\b(self-harm|suicide)\b'
    ]
    
    for pattern in prohibited_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return None, "Please rephrase your question focusing on positive spiritual growth."
    
    return text, None

async def get_spiritual_guidance(self, guru_type, question, user_context=None):
    # Sanitize input
    cleaned_question, error_message = self.sanitize_input(question)
    if error_message:
        return {
            "success": False,
            "error": error_message,
            "error_type": "ContentPolicyViolation"
        }
```

#### Token Limit Exceeded

**Error Code:** `400 Bad Request` - context length exceeded

**Implementation:**
```python
def manage_context_length(self, messages, model="gpt-4"):
    """Manage context length to stay within model limits."""
    
    max_tokens = {
        'gpt-4': 8192,
        'gpt-3.5-turbo': 4096
    }
    
    limit = max_tokens.get(model, 4096)
    current_tokens = sum(count_tokens(msg['content']) for msg in messages)
    
    if current_tokens > limit - 800:  # Reserve 800 tokens for response
        # Truncate older messages, keeping system prompt
        system_msg = messages[0]
        user_msg = messages[-1]
        
        # Summarize middle context if needed
        middle_content = " ".join([msg['content'] for msg in messages[1:-1]])
        if middle_content:
            summary = self.summarize_text(middle_content)
            messages = [
                system_msg,
                {"role": "system", "content": f"Previous context summary: {summary}"},
                user_msg
            ]
        else:
            messages = [system_msg, user_msg]
    
    return messages
```

#### Model Unavailability

**Error Code:** `503 Service Unavailable`

**Implementation:**
```python
class ModelFallbackStrategy:
    def __init__(self):
        self.model_hierarchy = [
            'gpt-4',
            'gpt-3.5-turbo-16k', 
            'gpt-3.5-turbo'
        ]
    
    async def get_response_with_fallback(self, messages, preferred_model='gpt-4'):
        """Try models in order of preference."""
        
        for model in self.model_hierarchy:
            try:
                response = await self._create_completion(messages, model=model)
                if model != preferred_model:
                    # Log fallback usage for monitoring
                    logger.info(f"Fallback to {model} from {preferred_model}")
                return response
                
            except openai.APIError as e:
                if model == self.model_hierarchy[-1]:
                    # Last resort failed
                    raise ServiceUnavailableError("AI services temporarily unavailable")
                continue
```

### Performance Optimization

#### Response Time Optimization

**Streaming Responses:**
```python
async def get_spiritual_guidance_stream(self, guru_type, question, user_context=None):
    """Stream responses for better perceived performance."""
    
    messages = self._prepare_messages(guru_type, question, user_context)
    
    try:
        stream = self.client.chat.completions.create(
            model=self.models['default'],
            messages=messages,
            stream=True,
            max_tokens=800,
            temperature=0.7
        )
        
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
                
    except Exception as e:
        yield f"[Error: {str(e)}]"
```

**Model Selection Strategy:**
```python
def select_optimal_model(self, question, user_context):
    """Select model based on complexity and requirements."""
    
    # Simple questions use faster model
    word_count = len(question.split())
    
    if word_count < 10 and not user_context:
        return self.models['fast']  # gpt-3.5-turbo
    
    # Complex spiritual guidance needs GPT-4
    if any(keyword in question.lower() for keyword in 
           ['meditation', 'consciousness', 'enlightenment', 'dharma']):
        return self.models['default']  # gpt-4
    
    return self.models['fast']
```

#### Caching Strategy

```python
import redis
import hashlib
import json

class ResponseCache:
    def __init__(self, redis_url=None):
        self.redis_client = redis.Redis.from_url(redis_url or 'redis://localhost:6379')
        self.cache_ttl = 3600  # 1 hour
    
    def get_cache_key(self, guru_type, question, user_context):
        """Generate cache key for request."""
        content = f"{guru_type}:{question}:{json.dumps(user_context, sort_keys=True)}"
        return f"ai_response:{hashlib.md5(content.encode()).hexdigest()}"
    
    async def get_cached_response(self, guru_type, question, user_context):
        """Get cached response if available."""
        cache_key = self.get_cache_key(guru_type, question, user_context)
        cached = self.redis_client.get(cache_key)
        
        if cached:
            return json.loads(cached)
        return None
    
    async def cache_response(self, guru_type, question, user_context, response):
        """Cache successful response."""
        cache_key = self.get_cache_key(guru_type, question, user_context)
        self.redis_client.setex(
            cache_key, 
            self.cache_ttl, 
            json.dumps(response)
        )
```

## Alternative AI Providers

### Claude Integration (Anthropic)

**Implementation:**
```python
class ClaudeService:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('CLAUDE_API_KEY')
        self.api_url = 'https://api.anthropic.com/v1/messages'
        self.model = 'claude-3-opus-20240229'
        
    async def get_response(self, prompt, max_tokens=1024, temperature=0.7):
        """Get response from Claude API."""
        headers = {
            'x-api-key': self.api_key,
            'anthropic-version': '2023-06-01',
            'content-type': 'application/json'
        }
        
        data = {
            'model': self.model,
            'max_tokens': max_tokens,
            'temperature': temperature,
            'messages': [
                {"role": "user", "content": prompt}
            ]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['content'][0]['text']
                else:
                    error_text = await response.text()
                    raise APIError(f"Claude API error: {response.status} - {error_text}")
```

**Fallback Implementation:**
```python
class AIServiceWithFallback:
    def __init__(self):
        self.openai_service = AIService()
        self.claude_service = ClaudeService() if os.getenv('CLAUDE_API_KEY') else None
        
    async def get_spiritual_guidance(self, guru_type, question, user_context=None):
        """Try OpenAI first, fallback to Claude if available."""
        
        try:
            return await self.openai_service.get_spiritual_guidance(
                guru_type, question, user_context
            )
        except (openai.RateLimitError, openai.APIError) as e:
            logger.warning(f"OpenAI failed: {e}. Trying Claude fallback.")
            
            if self.claude_service:
                try:
                    prompt = self._convert_to_claude_format(guru_type, question, user_context)
                    response = await self.claude_service.get_response(prompt)
                    
                    return {
                        "success": True,
                        "response": response,
                        "provider": "claude",
                        "fallback_used": True
                    }
                except Exception as claude_error:
                    logger.error(f"Claude fallback failed: {claude_error}")
            
            # No fallback available
            raise ServiceUnavailableError("All AI services temporarily unavailable")
```

## Monitoring and Analytics

### Usage Tracking

```python
class AIUsageTracker:
    def __init__(self):
        self.usage_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'rate_limit_hits': 0,
            'total_tokens': 0,
            'total_cost': 0.0,
            'by_guru_type': {},
            'by_model': {}
        }
    
    def track_request(self, guru_type, model, tokens_used, cost, success=True):
        """Track API usage for monitoring."""
        self.usage_stats['total_requests'] += 1
        
        if success:
            self.usage_stats['successful_requests'] += 1
            self.usage_stats['total_tokens'] += tokens_used
            self.usage_stats['total_cost'] += cost
        else:
            self.usage_stats['failed_requests'] += 1
        
        # Track by guru type
        if guru_type not in self.usage_stats['by_guru_type']:
            self.usage_stats['by_guru_type'][guru_type] = {
                'requests': 0, 'tokens': 0, 'cost': 0.0
            }
        
        guru_stats = self.usage_stats['by_guru_type'][guru_type]
        guru_stats['requests'] += 1
        if success:
            guru_stats['tokens'] += tokens_used
            guru_stats['cost'] += cost
        
        # Track by model
        if model not in self.usage_stats['by_model']:
            self.usage_stats['by_model'][model] = {
                'requests': 0, 'tokens': 0, 'cost': 0.0
            }
        
        model_stats = self.usage_stats['by_model'][model]
        model_stats['requests'] += 1
        if success:
            model_stats['tokens'] += tokens_used
            model_stats['cost'] += cost
    
    def get_usage_report(self):
        """Generate usage report for monitoring."""
        return {
            'summary': self.usage_stats,
            'success_rate': (self.usage_stats['successful_requests'] / 
                           max(self.usage_stats['total_requests'], 1) * 100),
            'average_cost_per_request': (self.usage_stats['total_cost'] / 
                                       max(self.usage_stats['successful_requests'], 1)),
            'most_used_guru': max(self.usage_stats['by_guru_type'].items(), 
                                key=lambda x: x[1]['requests'], default=('none', {}))[0]
        }
```

### Health Monitoring

```python
class AIServiceHealthMonitor:
    def __init__(self):
        self.health_status = {
            'openai': {'status': 'unknown', 'last_check': None},
            'claude': {'status': 'unknown', 'last_check': None}
        }
    
    async def check_openai_health(self):
        """Check OpenAI service health."""
        try:
            # Simple API call to test connectivity
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            
            self.health_status['openai'] = {
                'status': 'healthy',
                'last_check': datetime.utcnow(),
                'response_time': response.response_ms if hasattr(response, 'response_ms') else None
            }
            return True
            
        except Exception as e:
            self.health_status['openai'] = {
                'status': 'unhealthy',
                'last_check': datetime.utcnow(),
                'error': str(e)
            }
            return False
    
    async def get_health_status(self):
        """Get current health status of all AI providers."""
        await self.check_openai_health()
        # Add other provider checks as needed
        
        return {
            'overall_status': 'healthy' if any(
                provider['status'] == 'healthy' 
                for provider in self.health_status.values()
            ) else 'unhealthy',
            'providers': self.health_status,
            'timestamp': datetime.utcnow().isoformat()
        }
```

## Error Recovery Strategies

### Graceful Degradation

```python
class GracefulDegradationService:
    def __init__(self):
        self.fallback_responses = {
            'spiritual': "I'm currently unable to provide personalized guidance. Please take a moment for quiet reflection and remember that peace comes from within.",
            'meditation': "While our meditation guidance is temporarily unavailable, try focusing on your breath for a few minutes.",
            'bhakti': "Though our devotional guidance is offline, you can spend this time in gratitude for the blessings in your life."
        }
    
    async def get_fallback_response(self, guru_type, question):
        """Provide meaningful fallback when AI services are unavailable."""
        
        base_response = self.fallback_responses.get(
            guru_type, 
            "Our spiritual guidance is temporarily unavailable. Please try again shortly."
        )
        
        # Add suggestion based on question keywords
        suggestions = {
            'anxiety': "Consider taking deep breaths and focusing on the present moment.",
            'peace': "Remember that true peace is always available within you.",
            'purpose': "Your purpose unfolds naturally when you follow your authentic path.",
            'love': "Love begins with self-compassion and extends to all beings."
        }
        
        for keyword, suggestion in suggestions.items():
            if keyword in question.lower():
                base_response += f" {suggestion}"
                break
        
        return {
            "success": True,
            "response": base_response,
            "fallback_mode": True,
            "suggestion": "For immediate support, explore our meditation library or contact our support team."
        }
```

### Circuit Breaker Pattern

```python
import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open" 
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise ServiceUnavailableError("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
            
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
            
            raise e

# Usage
ai_circuit_breaker = CircuitBreaker(failure_threshold=3, timeout=120)

async def protected_ai_call(guru_type, question, user_context):
    return await ai_circuit_breaker.call(
        ai_service.get_spiritual_guidance,
        guru_type, question, user_context
    )
```

## Best Practices

### 1. Input Validation and Sanitization

```python
def validate_guru_request(data):
    """Validate incoming guru request."""
    errors = []
    
    # Required fields
    if not data.get('guru_type'):
        errors.append("guru_type is required")
    
    if not data.get('question'):
        errors.append("question is required")
    
    # Validate guru type
    valid_gurus = ['spiritual', 'meditation', 'bhakti', 'karma', 'yoga', 'sloka']
    if data.get('guru_type') not in valid_gurus:
        errors.append(f"guru_type must be one of: {', '.join(valid_gurus)}")
    
    # Question length validation
    question = data.get('question', '')
    if len(question) > 1000:
        errors.append("question must be less than 1000 characters")
    
    if len(question.split()) > 200:
        errors.append("question must be less than 200 words")
    
    return errors
```

### 2. Response Formatting

```python
def format_ai_response(response_data, guru_type, question):
    """Format AI response for consistent API output."""
    
    return {
        "success": True,
        "timestamp": datetime.utcnow().isoformat(),
        "guru": {
            "type": guru_type,
            "name": SPIRITUAL_GURUS[guru_type]['name'],
            "specialization": SPIRITUAL_GURUS[guru_type]['specialization']
        },
        "request": {
            "question": question[:100] + "..." if len(question) > 100 else question
        },
        "response": {
            "content": response_data['response'],
            "model_used": response_data.get('model'),
            "tokens_used": response_data.get('tokens_used'),
            "processing_time": response_data.get('processing_time')
        },
        "metadata": {
            "provider": "openai",
            "fallback_used": response_data.get('fallback_used', False),
            "cache_hit": response_data.get('cache_hit', False)
        }
    }
```

### 3. Logging and Monitoring

```python
import structlog

logger = structlog.get_logger(__name__)

async def get_spiritual_guidance_with_logging(guru_type, question, user_context):
    """Get spiritual guidance with comprehensive logging."""
    
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    logger.info(
        "ai_request_started",
        request_id=request_id,
        guru_type=guru_type,
        question_length=len(question),
        has_context=bool(user_context)
    )
    
    try:
        response = await ai_service.get_spiritual_guidance(
            guru_type, question, user_context
        )
        
        processing_time = time.time() - start_time
        
        logger.info(
            "ai_request_completed",
            request_id=request_id,
            processing_time=processing_time,
            tokens_used=response.get('tokens_used'),
            model=response.get('model'),
            success=response.get('success')
        )
        
        return response
        
    except Exception as e:
        processing_time = time.time() - start_time
        
        logger.error(
            "ai_request_failed",
            request_id=request_id,
            processing_time=processing_time,
            error_type=type(e).__name__,
            error_message=str(e),
            guru_type=guru_type
        )
        
        raise
```

## Conclusion

Understanding AI provider limitations and implementing robust error handling is crucial for maintaining a reliable spiritual guidance platform. Key takeaways:

1. **Rate Limiting**: Implement exponential backoff and consider multiple models
2. **Token Management**: Monitor context length and implement truncation strategies
3. **Error Recovery**: Use circuit breakers and fallback mechanisms
4. **Monitoring**: Track usage, costs, and performance metrics
5. **User Experience**: Provide meaningful error messages and alternative suggestions

Regular monitoring and testing of these systems ensure users receive consistent, high-quality spiritual guidance even when facing AI provider limitations.