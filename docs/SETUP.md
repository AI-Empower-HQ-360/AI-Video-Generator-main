# AI Empower Heart Platform - Setup Guide

## Prerequisites

Before setting up the AI Empower Heart Platform, ensure you have the following installed:

### Required Software

- **Python 3.9+** - Backend API framework
- **Node.js 18+** - Frontend build tools and dependencies  
- **npm 8+ or yarn 1.22+** - Package manager for JavaScript dependencies
- **Git** - Version control system

### Optional Software

- **Docker** - For containerized deployment
- **Redis** - Session storage and caching (production)
- **PostgreSQL** - Database (production)

### API Keys Required

- **OpenAI API Key** - For AI spiritual guidance features
- **Claude API Key** (Optional) - Alternative AI provider

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/AI-Empower-HQ-360/AI-Video-Generator-main.git
cd AI-Video-Generator-main
```

### 2. Backend Setup

#### Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

#### Environment Configuration

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```bash
# Flask Configuration
SECRET_KEY=your-secret-key-here-make-it-long-and-random
FLASK_ENV=development
DEBUG=True

# Database Configuration
DATABASE_URL=sqlite:///spiritual_platform.db

# OpenAI API Configuration (Required)
OPENAI_API_KEY=sk-your-openai-api-key-here

# Redis Configuration (Optional for development)
REDIS_URL=redis://localhost:6379

# CORS Origins (Production)
CORS_ORIGINS=https://empowerhub360.org,https://ai-empower-hq-360.github.io

# Rate Limiting
RATE_LIMIT_PER_HOUR=100
```

#### Google Cloud Services (Optional)

If using Google Cloud services, copy and configure the service account key:

```bash
cp key.example.json key.json
```

Edit `key.json` with your Google Cloud service account credentials.

#### Start the Backend Server

```bash
# Development server
python app.py

# Or using Flask CLI
flask run --host=0.0.0.0 --port=5000

# Production with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 3. Frontend Setup

#### Install Node.js Dependencies

```bash
# From project root
npm install

# Or with yarn
yarn install
```

#### Start Development Server

```bash
# Development server with hot reload
npm run dev

# Or with yarn
yarn dev
```

The frontend will be available at http://localhost:3000

### 4. Verify Installation

#### Check Backend Health

```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "spiritual-guidance-platform",
  "gurus_available": true
}
```

#### Test AI Functionality

```bash
curl -X POST http://localhost:5000/api/gurus/ask \
  -H "Content-Type: application/json" \
  -d '{
    "guru_type": "spiritual",
    "question": "What is the meaning of life?"
  }'
```

## Development Environment

### Project Structure

```
AI-Video-Generator-main/
├── backend/                 # Flask API backend
│   ├── api/                # API route blueprints
│   ├── services/           # Business logic services
│   ├── models/             # Data models
│   ├── utils/              # Utility functions
│   ├── app.py              # Main Flask application
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Environment variables template
├── src/                    # React frontend source
├── static/                 # Static assets
├── templates/              # HTML templates
├── docs/                   # Documentation
├── tests/                  # Test suites
├── package.json            # Node.js dependencies
└── docker-compose.yml      # Docker configuration
```

### Environment Variables Reference

#### Flask Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Yes | - | Flask secret key for session management |
| `FLASK_ENV` | No | development | Flask environment (development/production) |
| `DEBUG` | No | True | Enable debug mode |

#### Database Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | No | sqlite:///spiritual_platform.db | Database connection string |

#### AI Service Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | - | OpenAI API key for GPT models |
| `CLAUDE_API_KEY` | No | - | Claude API key (alternative AI) |

#### External Services

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `REDIS_URL` | No | redis://localhost:6379 | Redis connection for sessions |
| `CORS_ORIGINS` | No | * | Allowed CORS origins (comma-separated) |

#### Email Configuration (Optional)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SMTP_SERVER` | No | smtp.gmail.com | SMTP server for notifications |
| `SMTP_PORT` | No | 587 | SMTP port |
| `EMAIL_USER` | No | - | Email username |
| `EMAIL_PASSWORD` | No | - | Email password |

#### Analytics (Optional)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_ANALYTICS_ID` | No | - | Google Analytics tracking ID |

### Development Scripts

#### Backend Scripts

```bash
# Run development server
./run_dev.sh

# Run Flask directly
./run_flask.sh

# Start backend only
./start_backend.sh

# Run tests
./run_tests.sh

# Run Docker tests
./run_docker_tests.sh
```

#### Frontend Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run tests
npm test

# Run E2E tests
npm run test:e2e

# Lint code
npm run lint

# Format code
npm run format
```

## Production Deployment

### Docker Deployment

#### Build and Run with Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

#### Environment Configuration for Production

Create `.env.production`:

```bash
# Production Flask Configuration
SECRET_KEY=your-very-secure-production-secret-key
FLASK_ENV=production
DEBUG=False

# Production Database
DATABASE_URL=postgresql://user:password@postgres:5432/spiritual_platform

# OpenAI Configuration
OPENAI_API_KEY=your-production-openai-api-key

# Redis Configuration
REDIS_URL=redis://redis:6379

# CORS Configuration
CORS_ORIGINS=https://empowerhub360.org,https://www.empowerhub360.org

# Rate Limiting
RATE_LIMIT_PER_HOUR=50

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=noreply@empowerhub360.org
EMAIL_PASSWORD=your-email-app-password
```

### Manual Production Setup

#### System Dependencies

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip nodejs npm nginx redis-server postgresql

# CentOS/RHEL
sudo yum install python3 python3-pip nodejs npm nginx redis postgresql-server
```

#### Production Web Server (Nginx)

Create `/etc/nginx/sites-available/empowerhub360`:

```nginx
server {
    listen 80;
    server_name empowerhub360.org www.empowerhub360.org;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name empowerhub360.org www.empowerhub360.org;

    # SSL Configuration
    ssl_certificate /path/to/ssl/certificate.crt;
    ssl_certificate_key /path/to/ssl/private.key;

    # Frontend static files
    location / {
        root /var/www/empowerhub360/dist;
        try_files $uri $uri/ /index.html;
    }

    # API proxy to Flask backend
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support for streaming
    location /api/gurus/ask/stream {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

#### Process Manager (Systemd)

Create `/etc/systemd/system/empowerhub-backend.service`:

```ini
[Unit]
Description=AI Empower Heart Backend
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/var/www/empowerhub360/backend
Environment=PATH=/var/www/empowerhub360/venv/bin
ExecStart=/var/www/empowerhub360/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable empowerhub-backend
sudo systemctl start empowerhub-backend
sudo systemctl status empowerhub-backend
```

## Testing

### Running Tests

#### Backend Tests

```bash
# Run all Python tests
cd backend
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_gurus.py -v

# Run with coverage
python -m pytest tests/ --cov=services --cov-report=html
```

#### Frontend Tests

```bash
# Run unit tests
npm test

# Run E2E tests
npm run test:e2e

# Run tests with UI
npm run test:e2e:ui

# Run tests in CI mode
npm run test:coverage
```

### Test Configuration

#### Jest Configuration (Frontend)

File: `jest.config.js`
```javascript
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/tests/jest.setup.js'],
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/src/$1'
  },
  collectCoverageFrom: [
    'src/**/*.{js,jsx}',
    '!src/main.jsx',
    '!src/vite-env.d.ts'
  ]
};
```

#### Pytest Configuration (Backend)

File: `backend/pytest.ini`
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

## Troubleshooting

### Common Issues

#### Backend Issues

**Issue: OpenAI API key error**
```
ValueError: OPENAI_API_KEY environment variable is required
```
**Solution:** Ensure your `.env` file contains a valid OpenAI API key.

**Issue: Import errors**
```
ModuleNotFoundError: No module named 'openai'
```
**Solution:** Install dependencies: `pip install -r requirements.txt`

**Issue: Port already in use**
```
OSError: [Errno 98] Address already in use
```
**Solution:** Change port or kill existing process:
```bash
# Find process using port 5000
lsof -i :5000

# Kill process
kill -9 <PID>
```

#### Frontend Issues

**Issue: Node modules not found**
```
Error: Cannot resolve module '@emotion/react'
```
**Solution:** Install dependencies: `npm install`

**Issue: Build failures**
```
Error: Build failed due to a user error
```
**Solution:** Check for syntax errors and ensure all dependencies are installed.

#### API Issues

**Issue: CORS errors**
```
Access to fetch blocked by CORS policy
```
**Solution:** Update CORS configuration in `backend/app.py` or ensure frontend runs on allowed origin.

**Issue: Rate limiting**
```
HTTP 429: Too Many Requests
```
**Solution:** Implement exponential backoff or increase rate limits in environment configuration.

### Debug Mode

Enable verbose logging for debugging:

```bash
# Backend debug mode
export FLASK_ENV=development
export DEBUG=True

# Frontend debug mode
export NODE_ENV=development
export VITE_DEBUG=true
```

### Performance Optimization

#### Backend Optimization

1. **Use Gunicorn with multiple workers:**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. **Enable Redis caching:**
   ```bash
   export REDIS_URL=redis://localhost:6379
   ```

3. **Database connection pooling:**
   ```python
   # In production configuration
   SQLALCHEMY_ENGINE_OPTIONS = {
       'pool_size': 10,
       'pool_recycle': 120,
       'pool_pre_ping': True
   }
   ```

#### Frontend Optimization

1. **Build for production:**
   ```bash
   npm run build
   ```

2. **Enable compression:**
   ```nginx
   gzip on;
   gzip_types text/css application/javascript application/json;
   ```

## Security Best Practices

### Environment Security

1. **Never commit secrets to Git:**
   ```bash
   # Ensure .env and key.json are in .gitignore
   echo ".env" >> .gitignore
   echo "key.json" >> .gitignore
   ```

2. **Use strong secret keys:**
   ```bash
   # Generate secure secret key
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

3. **Restrict CORS origins in production:**
   ```bash
   CORS_ORIGINS=https://empowerhub360.org,https://www.empowerhub360.org
   ```

### API Security

1. **Implement rate limiting**
2. **Validate all inputs**
3. **Use HTTPS in production**
4. **Monitor API usage**
5. **Implement API key rotation**

## Monitoring and Logging

### Application Logging

Configure logging in production:

```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/empowerhub.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Empowerhub startup')
```

### Health Monitoring

Set up health check endpoints for monitoring:

```bash
# Check backend health
curl http://localhost:5000/health

# Monitor specific services
curl http://localhost:5000/api/gurus/workflows
```

## Support

For setup assistance:
- **Documentation:** https://docs.empowerhub360.org
- **GitHub Issues:** https://github.com/AI-Empower-HQ-360/AI-Video-Generator-main/issues
- **Email:** support@empowerhub360.org