# AI Empower Heart Platform - Troubleshooting Guide

## Quick Diagnostic Checklist

Before diving into specific issues, run through this quick checklist:

1. **Service Health Check**
   ```bash
   curl http://localhost:5000/health
   ```

2. **Environment Variables**
   ```bash
   # Check if OpenAI API key is set
   echo $OPENAI_API_KEY
   
   # Check backend environment file
   cat backend/.env
   ```

3. **Dependencies**
   ```bash
   # Python dependencies
   cd backend && pip list | grep -E "(flask|openai)"
   
   # Node.js dependencies  
   npm list --depth=0
   ```

4. **Port Availability**
   ```bash
   # Check if ports are available
   netstat -tulpn | grep -E ":5000|:3000"
   ```

## Backend Issues

### OpenAI API Integration

#### Issue: "OPENAI_API_KEY environment variable is required"

**Symptoms:**
- Backend fails to start
- AI guru endpoints return 503 errors
- Service health shows gurus_available: false

**Diagnosis:**
```bash
# Check if API key is set
echo $OPENAI_API_KEY

# Check .env file
cat backend/.env | grep OPENAI_API_KEY
```

**Solutions:**

1. **Set environment variable:**
   ```bash
   export OPENAI_API_KEY=sk-your-api-key-here
   ```

2. **Update .env file:**
   ```bash
   cd backend
   echo "OPENAI_API_KEY=sk-your-api-key-here" >> .env
   ```

3. **Verify API key validity:**
   ```bash
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer $OPENAI_API_KEY"
   ```

#### Issue: "Rate limit exceeded" (HTTP 429)

**Symptoms:**
- Intermittent API failures
- Error: "Rate limit exceeded for gpt-4"
- Slow response times

**Diagnosis:**
```bash
# Check current usage
curl https://api.openai.com/v1/usage \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

**Solutions:**

1. **Implement exponential backoff:**
   ```python
   # In ai_service.py - already implemented
   for attempt in range(self.max_retries):
       try:
           response = await self._create_completion(...)
           return response
       except openai.RateLimitError:
           if attempt == self.max_retries - 1:
               raise
           await asyncio.sleep(self.retry_delay * (attempt + 1))
   ```

2. **Use GPT-3.5-turbo for less critical requests:**
   ```python
   # Fallback to faster model
   model = self.models['fast']  # gpt-3.5-turbo
   ```

3. **Monitor usage:**
   ```bash
   # Set up monitoring script
   watch -n 60 'curl -s https://api.openai.com/v1/usage -H "Authorization: Bearer $OPENAI_API_KEY"'
   ```

#### Issue: "Token limit exceeded"

**Symptoms:**
- Error: "This model's maximum context length is 8192 tokens"
- Truncated responses
- Failed API calls with large inputs

**Diagnosis:**
```python
# Count tokens in request
import tiktoken

def count_tokens(text, model="gpt-4"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

# Check token count
print(f"Tokens: {count_tokens(your_text)}")
```

**Solutions:**

1. **Implement text truncation:**
   ```python
   def truncate_text(text, max_tokens=6000):
       encoding = tiktoken.encoding_for_model("gpt-4")
       tokens = encoding.encode(text)
       if len(tokens) > max_tokens:
           tokens = tokens[:max_tokens]
           text = encoding.decode(tokens)
       return text
   ```

2. **Use text summarization for long inputs:**
   ```python
   # Summarize long context before processing
   if count_tokens(user_context) > 2000:
       user_context = await self.summarize_text(user_context)
   ```

### Flask Application Issues

#### Issue: "ModuleNotFoundError" during startup

**Symptoms:**
- Backend fails to start
- Import errors for custom modules
- Python path issues

**Diagnosis:**
```bash
# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Check if modules exist
ls backend/api/
ls backend/services/
```

**Solutions:**

1. **Add backend to Python path:**
   ```bash
   export PYTHONPATH="${PYTHONPATH}:/path/to/backend"
   ```

2. **Use relative imports:**
   ```python
   # In backend files, use relative imports
   from .services.ai_service import AIService
   ```

3. **Install in development mode:**
   ```bash
   cd backend
   pip install -e .
   ```

#### Issue: "Port already in use" (Address already in use)

**Symptoms:**
- Flask fails to start
- Error: "OSError: [Errno 98] Address already in use"

**Diagnosis:**
```bash
# Find process using port 5000
lsof -i :5000
netstat -tulpn | grep :5000
```

**Solutions:**

1. **Kill existing process:**
   ```bash
   # Find and kill process
   kill -9 $(lsof -t -i:5000)
   ```

2. **Use different port:**
   ```bash
   export FLASK_PORT=5001
   flask run --port=5001
   ```

3. **Use process manager:**
   ```bash
   # Use gunicorn with automatic restart
   gunicorn --bind 0.0.0.0:5000 --reload app:app
   ```

#### Issue: CORS errors from frontend

**Symptoms:**
- Frontend can't access API
- Browser console: "blocked by CORS policy"
- OPTIONS requests failing

**Diagnosis:**
```bash
# Test CORS with curl
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     http://localhost:5000/api/gurus/ask
```

**Solutions:**

1. **Update CORS configuration:**
   ```python
   # In app.py
   CORS(app, resources={
       r"/*": {
           "origins": ["http://localhost:3000", "https://empowerhub360.org"],
           "methods": ["GET", "POST", "OPTIONS"],
           "allow_headers": ["Content-Type", "Authorization"]
       }
   })
   ```

2. **Check environment variables:**
   ```bash
   echo $CORS_ORIGINS
   ```

3. **Test with specific origin:**
   ```bash
   curl -X POST http://localhost:5000/api/gurus/ask \
        -H "Origin: http://localhost:3000" \
        -H "Content-Type: application/json" \
        -d '{"guru_type": "spiritual", "question": "test"}'
   ```

### Database Issues

#### Issue: Database connection failures

**Symptoms:**
- Backend startup errors
- Database operation failures
- Connection timeout errors

**Diagnosis:**
```bash
# Check database URL
echo $DATABASE_URL

# Test database connection
python -c "
import os
from sqlalchemy import create_engine
engine = create_engine(os.getenv('DATABASE_URL', 'sqlite:///spiritual_platform.db'))
print('Database connection successful')
"
```

**Solutions:**

1. **SQLite (Development):**
   ```bash
   # Ensure directory exists
   mkdir -p backend/instance
   
   # Check file permissions
   ls -la backend/instance/
   ```

2. **PostgreSQL (Production):**
   ```bash
   # Test PostgreSQL connection
   psql $DATABASE_URL -c "SELECT version();"
   
   # Check if database exists
   psql $DATABASE_URL -c "\l"
   ```

3. **Create database tables:**
   ```bash
   cd backend
   python -c "
   from app import app
   from models import db
   with app.app_context():
       db.create_all()
   "
   ```

## Frontend Issues

### Node.js and npm Issues

#### Issue: "Module not found" errors

**Symptoms:**
- Build failures
- Runtime errors in browser
- Missing dependency errors

**Diagnosis:**
```bash
# Check if node_modules exists
ls node_modules/

# Check package.json vs package-lock.json
npm ls --depth=0
```

**Solutions:**

1. **Clean install:**
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

2. **Check Node.js version:**
   ```bash
   # Ensure Node.js 18+ is installed
   node --version
   npm --version
   ```

3. **Clear npm cache:**
   ```bash
   npm cache clean --force
   ```

#### Issue: Build process failures

**Symptoms:**
- Vite build errors
- TypeScript compilation errors
- Asset bundling failures

**Diagnosis:**
```bash
# Run build with verbose output
npm run build -- --verbose

# Check for syntax errors
npm run lint
```

**Solutions:**

1. **Fix ESLint errors:**
   ```bash
   npm run lint:fix
   ```

2. **Update dependencies:**
   ```bash
   npm update
   npm audit fix
   ```

3. **Clear build cache:**
   ```bash
   rm -rf dist/
   npm run build
   ```

### Browser Issues

#### Issue: JavaScript runtime errors

**Symptoms:**
- Console errors in browser
- React component failures
- API call failures

**Diagnosis:**
```javascript
// Open browser developer tools (F12)
// Check Console tab for errors
// Check Network tab for failed requests
```

**Solutions:**

1. **Check API endpoints:**
   ```javascript
   // Test API connection
   fetch('/api/health')
     .then(response => response.json())
     .then(data => console.log(data))
     .catch(error => console.error('API Error:', error));
   ```

2. **Verify environment variables:**
   ```bash
   # Check if .env.local exists
   cat .env.local
   ```

3. **Clear browser cache:**
   ```bash
   # Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
   # Or clear browser data in settings
   ```

## AI Service Issues

### Streaming Response Problems

#### Issue: Streaming responses not working

**Symptoms:**
- SSE connections fail
- Streaming endpoint returns 500 errors
- Responses don't appear in real-time

**Diagnosis:**
```bash
# Test streaming endpoint
curl -N -H "Accept: text/event-stream" \
     -H "Content-Type: application/json" \
     -X POST http://localhost:5000/api/gurus/ask/stream \
     -d '{"guru_type": "spiritual", "question": "test"}'
```

**Solutions:**

1. **Check SSE implementation:**
   ```python
   # Ensure proper SSE headers
   def generate():
       yield f"data: {json.dumps({'chunk': 'test'})}\n\n"
   
   return Response(generate(), mimetype='text/event-stream')
   ```

2. **Verify async/await usage:**
   ```python
   # Ensure async generators are properly handled
   async def stream_response():
       async for chunk in ai_service.get_spiritual_guidance_stream(...):
           yield f"data: {json.dumps({'chunk': chunk})}\n\n"
   ```

3. **Check proxy settings (production):**
   ```nginx
   # Nginx configuration for SSE
   location /api/gurus/ask/stream {
       proxy_pass http://127.0.0.1:5000;
       proxy_set_header Connection '';
       proxy_http_version 1.1;
       chunked_transfer_encoding off;
       proxy_buffering off;
       proxy_cache off;
   }
   ```

### Workflow Configuration Issues

#### Issue: Workflow manager not loading

**Symptoms:**
- Default prompts used instead of workflow configuration
- Warning: "Workflow manager not available"
- Configuration endpoints return 503

**Diagnosis:**
```python
# Check if workflow_assignment.py exists
ls backend/workflow_assignment.py

# Test import
python -c "from workflow_assignment import ChatGPTWorkflowManager; print('Import successful')"
```

**Solutions:**

1. **Create workflow_assignment.py if missing:**
   ```python
   # Basic workflow manager implementation
   class ChatGPTWorkflowManager:
       def __init__(self):
           self.workflows = {}
       
       def assign_chatgpt_to_workflow(self, guru_type, user_context=None):
           return {
               'chatgpt_config': {
                   'model': 'gpt-4',
                   'temperature': 0.7,
                   'max_tokens': 800,
                   'system_prompt': f"You are the {guru_type} guru..."
               }
           }
   ```

2. **Check dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Performance Issues

### Slow Response Times

#### Issue: API responses are slow

**Symptoms:**
- Long response times (>10 seconds)
- Frontend timeouts
- Poor user experience

**Diagnosis:**
```bash
# Measure API response time
time curl -X POST http://localhost:5000/api/gurus/ask \
     -H "Content-Type: application/json" \
     -d '{"guru_type": "spiritual", "question": "test"}'

# Check system resources
top
free -h
df -h
```

**Solutions:**

1. **Use faster model for simple queries:**
   ```python
   # Use GPT-3.5-turbo for basic questions
   if len(question.split()) < 10:
       model = self.models['fast']
   ```

2. **Implement caching:**
   ```python
   # Cache common responses
   import redis
   
   cache = redis.Redis()
   cache_key = f"guru:{guru_type}:{hash(question)}"
   
   cached_response = cache.get(cache_key)
   if cached_response:
       return json.loads(cached_response)
   ```

3. **Optimize model parameters:**
   ```python
   # Reduce max_tokens for faster responses
   response = self.client.chat.completions.create(
       model=model,
       messages=messages,
       max_tokens=400,  # Reduced from 800
       temperature=0.7
   )
   ```

### High Memory Usage

#### Issue: High memory consumption

**Symptoms:**
- System runs out of memory
- Process killed by OOM killer
- Slow performance

**Diagnosis:**
```bash
# Check memory usage
ps aux | grep -E "(python|node)"
free -h

# Monitor memory over time
while true; do
    echo "$(date): $(free -h | grep Mem:)"
    sleep 60
done
```

**Solutions:**

1. **Optimize Python memory usage:**
   ```python
   # Use generators instead of lists
   def process_large_data():
       for item in large_dataset:
           yield process(item)
   
   # Clear variables when done
   del large_variable
   import gc
   gc.collect()
   ```

2. **Configure Gunicorn workers:**
   ```bash
   # Use appropriate number of workers
   gunicorn -w 2 --max-requests 1000 --preload app:app
   ```

3. **Monitor memory leaks:**
   ```python
   # Use memory profiler
   from memory_profiler import profile
   
   @profile
   def memory_intensive_function():
       # Your code here
       pass
   ```

## Deployment Issues

### Docker Deployment Problems

#### Issue: Docker containers won't start

**Symptoms:**
- Container exits immediately
- Build failures
- Service unavailable

**Diagnosis:**
```bash
# Check container logs
docker-compose logs backend
docker-compose logs frontend

# Check container status
docker-compose ps

# Test individual services
docker run --rm -it backend-image /bin/bash
```

**Solutions:**

1. **Fix Dockerfile issues:**
   ```dockerfile
   # Ensure proper Python environment
   FROM python:3.9-slim
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   # Set environment variables
   ENV FLASK_APP=app.py
   ENV PYTHONPATH=/app
   
   CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
   ```

2. **Check environment variables in Docker:**
   ```yaml
   # docker-compose.yml
   version: '3.8'
   services:
     backend:
       build: ./backend
       environment:
         - OPENAI_API_KEY=${OPENAI_API_KEY}
       env_file:
         - backend/.env
   ```

3. **Debug container interactively:**
   ```bash
   # Run container with bash
   docker run --rm -it backend-image /bin/bash
   
   # Test Python imports
   python -c "from app import app; print('Success')"
   ```

### Production Deployment Issues

#### Issue: SSL/HTTPS problems

**Symptoms:**
- Certificate errors
- Mixed content warnings
- Insecure connection errors

**Diagnosis:**
```bash
# Test SSL certificate
openssl s_client -connect empowerhub360.org:443

# Check certificate expiration
echo | openssl s_client -servername empowerhub360.org -connect empowerhub360.org:443 2>/dev/null | openssl x509 -noout -dates
```

**Solutions:**

1. **Renew SSL certificate:**
   ```bash
   # Using Let's Encrypt
   certbot renew --nginx
   
   # Test renewal
   certbot renew --dry-run
   ```

2. **Update Nginx configuration:**
   ```nginx
   # Ensure proper SSL configuration
   ssl_protocols TLSv1.2 TLSv1.3;
   ssl_ciphers HIGH:!aNULL:!MD5;
   ssl_prefer_server_ciphers on;
   ```

## Monitoring and Logging

### Enable Debug Logging

**Backend:**
```python
# In app.py
import logging
logging.basicConfig(level=logging.DEBUG)

# For specific modules
logging.getLogger('services.ai_service').setLevel(logging.DEBUG)
```

**Frontend:**
```javascript
// Enable debug mode
localStorage.setItem('debug', 'true');

// Console logging
console.log('Debug info:', data);
```

### Health Monitoring Setup

```bash
# Create monitoring script
cat > monitor.sh << 'EOF'
#!/bin/bash

while true; do
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Check backend health
    backend_status=$(curl -s -w "%{http_code}" -o /dev/null http://localhost:5000/health)
    
    # Check frontend
    frontend_status=$(curl -s -w "%{http_code}" -o /dev/null http://localhost:3000)
    
    echo "$timestamp - Backend: $backend_status, Frontend: $frontend_status"
    
    sleep 60
done
EOF

chmod +x monitor.sh
./monitor.sh
```

## Getting Help

### Before Seeking Support

1. **Check logs:**
   ```bash
   # Backend logs
   tail -f backend/logs/app.log
   
   # System logs
   journalctl -u empowerhub-backend -f
   ```

2. **Gather system information:**
   ```bash
   # System info
   uname -a
   python --version
   node --version
   
   # Service status
   systemctl status empowerhub-backend
   ```

3. **Test minimal configuration:**
   ```bash
   # Start with minimal .env
   cp backend/.env.example backend/.env.minimal
   # Add only OPENAI_API_KEY
   ```

### Support Channels

- **GitHub Issues:** https://github.com/AI-Empower-HQ-360/AI-Video-Generator-main/issues
- **Documentation:** https://docs.empowerhub360.org
- **Email:** support@empowerhub360.org

### Creating Good Bug Reports

Include the following information:

1. **Environment details:**
   - Operating system and version
   - Python and Node.js versions
   - Installation method (Docker, manual, etc.)

2. **Steps to reproduce:**
   - Exact commands run
   - Configuration used
   - Expected vs actual behavior

3. **Error messages:**
   - Full error logs
   - Stack traces
   - Browser console errors

4. **Configuration:**
   - Anonymized .env file
   - Docker compose configuration
   - Network setup

### Emergency Recovery

**Quick service restart:**
```bash
# Stop all services
docker-compose down

# Clear caches
docker system prune -f

# Restart services
docker-compose up -d

# Check status
docker-compose ps
curl http://localhost:5000/health
```

**Database recovery:**
```bash
# Backup current database
cp backend/instance/spiritual_platform.db backup_$(date +%Y%m%d_%H%M%S).db

# Reset database
rm backend/instance/spiritual_platform.db
python -c "from app import app; from models import db; app.app_context().push(); db.create_all()"
```

This troubleshooting guide covers the most common issues you may encounter. For issues not covered here, please refer to the support channels listed above.