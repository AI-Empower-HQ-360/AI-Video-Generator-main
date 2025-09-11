# AI Empower Heart Platform - API Documentation

## Overview

The AI Empower Heart Platform provides RESTful APIs for AI-powered spiritual guidance through various specialized gurus. This documentation covers all available endpoints, request/response formats, authentication, and usage examples.

## Base URL

```
Development: http://localhost:5000
Production: https://empowerhub360.org/api
```

## Authentication

Currently, the API uses basic authentication with API keys. Include your API key in the request headers:

```http
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

## Rate Limiting

- **Development**: 100 requests per hour per IP
- **Production**: 50 requests per hour per authenticated user
- **Burst**: Maximum 10 requests per minute

Rate limit headers are included in responses:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1640995200
```

## Error Handling

All errors follow a consistent format:

```json
{
  "success": false,
  "error": "Error description",
  "error_type": "ErrorClassName",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Common HTTP Status Codes

- `200` - Success
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (missing/invalid API key)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (resource doesn't exist)
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error
- `503` - Service Unavailable (AI service down)

## Core Endpoints

### Health Check

Check service status and availability.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "service": "spiritual-guidance-platform",
  "gurus_available": true,
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Service Information

Get API metadata and available features.

**Endpoint:** `GET /`

**Response:**
```json
{
  "message": "AI Empower Heart Spiritual Platform API",
  "version": "1.0.0",
  "status": "active",
  "available_gurus": ["karma", "bhakti", "meditation", "yoga", "spiritual", "sloka"],
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

## Spiritual Gurus API

### List All Gurus

Get information about all available spiritual gurus.

**Endpoint:** `GET /api/gurus`

**Response:**
```json
{
  "success": true,
  "gurus": {
    "spiritual": {
      "name": "🙏 AI Spiritual Guru",
      "specialization": "Soul consciousness and eternal identity"
    },
    "meditation": {
      "name": "🧘 AI Meditation Guru", 
      "specialization": "Inner peace and mindfulness"
    },
    "bhakti": {
      "name": "💝 AI Bhakti Guru",
      "specialization": "Devotion and divine love"
    },
    "karma": {
      "name": "⚖️ AI Karma Guru",
      "specialization": "Ethics and dharma"
    },
    "yoga": {
      "name": "🧘‍♀️ AI Yoga Guru",
      "specialization": "Breath and energy alignment"
    },
    "sloka": {
      "name": "🕉️ AI Sloka Guru",
      "specialization": "Sanskrit verses and sacred wisdom"
    }
  },
  "total": 6
}
```

### Get Specific Guru

Get information about a specific guru.

**Endpoint:** `GET /api/gurus/{guru_type}`

**Parameters:**
- `guru_type` (path): Type of guru (spiritual, meditation, bhakti, karma, yoga, sloka)

**Response:**
```json
{
  "success": true,
  "guru": {
    "name": "🙏 AI Spiritual Guru",
    "specialization": "Soul consciousness and eternal identity"
  }
}
```

### Ask Guru (Standard)

Get spiritual guidance from a specific guru.

**Endpoint:** `POST /api/gurus/ask`

**Request Body:**
```json
{
  "guru_type": "spiritual",
  "question": "How can I find inner peace?",
  "user_context": {
    "experience_level": "beginner",
    "previous_topics": ["meditation", "stress"],
    "preferred_style": "practical"
  }
}
```

**Response:**
```json
{
  "success": true,
  "guru_name": "🙏 AI Spiritual Guru",
  "guru_type": "spiritual",
  "question": "How can I find inner peace?",
  "response": "Inner peace comes from understanding your true nature as an eternal soul...",
  "specialization": "Soul consciousness and eternal identity",
  "tokens_used": 150,
  "model": "gpt-4",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Ask Guru (Streaming)

Get streaming spiritual guidance for real-time responses.

**Endpoint:** `POST /api/gurus/ask/stream`

**Request Body:** Same as standard ask endpoint

**Response:** Server-Sent Events (SSE) stream
```
data: {"chunk": "Inner peace comes"}
data: {"chunk": " from understanding"}
data: {"chunk": " your true nature..."}
data: [DONE]
```

### Spiritual Guidance (Alternative Endpoint)

Alternative endpoint for spiritual guidance (maintains backward compatibility).

**Endpoint:** `POST /api/spiritual/guidance`

Same request/response format as `/api/gurus/ask`

## Advanced Features

### Workflow Configuration

Get available AI workflows and their configurations.

**Endpoint:** `GET /api/gurus/workflows`

**Response:**
```json
{
  "success": true,
  "available_workflows": {
    "spiritual": {
      "name": "Spiritual Guidance Workflow",
      "model": "gpt-4",
      "workflow_type": "spiritual_guidance",
      "priority": "high",
      "streaming_available": true
    }
  },
  "total_workflows": 6
}
```

### Get Workflow Config

Get detailed configuration for a specific guru workflow.

**Endpoint:** `GET /api/gurus/workflow/{guru_type}/config`

**Response:**
```json
{
  "success": true,
  "workflow_config": {
    "name": "Spiritual Guidance Workflow",
    "chatgpt_model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 800,
    "system_prompt": "You are the AI Spiritual Guru...",
    "workflow_type": "spiritual_guidance",
    "priority": "high"
  }
}
```

## User Management API

### Create User

**Endpoint:** `POST /api/users`

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "preferences": {
    "favorite_gurus": ["spiritual", "meditation"],
    "experience_level": "intermediate"
  }
}
```

### Get User Profile

**Endpoint:** `GET /api/users/{user_id}`

### Update User Preferences

**Endpoint:** `PUT /api/users/{user_id}/preferences`

## Session Management API

### Create Session

**Endpoint:** `POST /api/sessions`

**Request Body:**
```json
{
  "user_id": "user123",
  "guru_type": "spiritual",
  "session_type": "guidance"
}
```

### Get Session History

**Endpoint:** `GET /api/sessions/{session_id}/history`

## Sanskrit Slokas API

### Get Random Sloka

**Endpoint:** `GET /api/slokas/random`

**Response:**
```json
{
  "success": true,
  "sloka": {
    "sanskrit": "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन",
    "transliteration": "karmaṇy-evādhikāras te mā phaleṣu kadācana",
    "translation": "You have a right to perform your prescribed duty, but not to the fruits of action",
    "source": "Bhagavad Gita 2.47",
    "meaning": "This verse teaches the importance of performing duty without attachment to results..."
  }
}
```

### Search Slokas

**Endpoint:** `GET /api/slokas/search?q={query}`

## Speech-to-Text (Whisper) API

### Upload Audio

**Endpoint:** `POST /api/whisper/transcribe`

**Request:** Multipart form data with audio file

**Response:**
```json
{
  "success": true,
  "transcription": "How can I find inner peace?",
  "confidence": 0.95,
  "language": "en",
  "duration": 3.2
}
```

## Durable Functions Integration

### Execute Durable Function

**Endpoint:** `POST /durable/functions/{function_name}`

Used for long-running AI processes and workflow orchestration.

## Usage Examples

### JavaScript/Frontend Integration

```javascript
// Ask a spiritual guru
const response = await fetch('/api/gurus/ask', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer YOUR_API_KEY'
  },
  body: JSON.stringify({
    guru_type: 'spiritual',
    question: 'How can I overcome anxiety?',
    user_context: {
      experience_level: 'beginner'
    }
  })
});

const data = await response.json();
console.log(data.response);
```

### Python Integration

```python
import requests

url = "http://localhost:5000/api/gurus/ask"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer YOUR_API_KEY"
}
data = {
    "guru_type": "meditation",
    "question": "Guide me through a breathing exercise",
    "user_context": {
        "experience_level": "intermediate"
    }
}

response = requests.post(url, json=data, headers=headers)
result = response.json()
print(result["response"])
```

### Streaming Response Example

```javascript
// Handle streaming responses
const eventSource = new EventSource('/api/gurus/ask/stream', {
  method: 'POST',
  body: JSON.stringify({
    guru_type: 'spiritual',
    question: 'What is the meaning of life?'
  })
});

eventSource.onmessage = function(event) {
  if (event.data === '[DONE]') {
    eventSource.close();
    return;
  }
  
  const chunk = JSON.parse(event.data);
  console.log(chunk.chunk);
};
```

## AI Provider Limitations

### OpenAI API Limits

- **Rate Limits**: Varies by plan and model
- **Token Limits**: 
  - GPT-4: 8,192 tokens per request
  - GPT-3.5-turbo: 4,096 tokens per request
- **Context Window**: Maximum conversation length varies by model
- **Cost**: Usage-based pricing per token

### Error Scenarios

1. **Rate Limit Exceeded**: HTTP 429, retry with exponential backoff
2. **Token Limit Exceeded**: Truncate input or use summarization
3. **Model Unavailable**: Automatic fallback to alternative models
4. **Network Timeout**: Retry with increased timeout
5. **Invalid API Key**: HTTP 401, check environment configuration

## Security Considerations

1. **API Key Protection**: Never expose API keys in client-side code
2. **CORS Configuration**: Properly configured for production domains
3. **Input Validation**: All inputs are sanitized and validated
4. **Rate Limiting**: Prevents abuse and ensures fair usage
5. **Error Information**: Error messages don't expose sensitive details

## Support

For API support and questions:
- Email: support@empowerhub360.org
- Documentation: https://docs.empowerhub360.org
- GitHub Issues: https://github.com/AI-Empower-HQ-360/AI-Video-Generator-main/issues