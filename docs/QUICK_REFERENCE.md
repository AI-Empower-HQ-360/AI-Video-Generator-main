# Quick Reference Guide

## Documentation Quick Links

### Essential Documentation
- 📖 **[Main README](../README.md)** - Project overview and quick start
- 🔌 **[API Documentation](API.md)** - Complete API reference
- ⚙️ **[Setup Guide](SETUP.md)** - Installation and configuration
- 🔧 **[Troubleshooting](TROUBLESHOOTING.md)** - Common issues and solutions

### Specialized Guides
- 🤖 **[AI Providers](AI_PROVIDERS.md)** - AI limitations and error handling
- 🌍 **[Environment Config](ENVIRONMENT.md)** - Environment variables and settings
- 📋 **[Documentation Standards](DOCUMENTATION_STANDARDS.md)** - Implementation summary

## Quick Start Commands

### Development Setup
```bash
# Clone repository
git clone https://github.com/AI-Empower-HQ-360/AI-Video-Generator-main.git
cd AI-Video-Generator-main

# Backend setup
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your OPENAI_API_KEY
python app.py

# Frontend setup (new terminal)
npm install
npm run dev
```

### Essential Environment Variables
```bash
# Required
OPENAI_API_KEY=sk-your-openai-api-key-here
SECRET_KEY=your-secret-key-here

# Optional but recommended
REDIS_URL=redis://localhost:6379
DATABASE_URL=sqlite:///spiritual_platform.db
CORS_ORIGINS=http://localhost:3000
```

## API Quick Reference

### Health Check
```bash
curl http://localhost:5000/health
```

### List Gurus
```bash
curl http://localhost:5000/api/gurus
```

### Ask Guru
```bash
curl -X POST http://localhost:5000/api/gurus/ask \
  -H "Content-Type: application/json" \
  -d '{
    "guru_type": "spiritual",
    "question": "How can I find inner peace?"
  }'
```

## Available Spiritual Gurus

| Guru Type | Name | Specialization |
|-----------|------|----------------|
| `spiritual` | 🙏 AI Spiritual Guru | Soul consciousness and eternal identity |
| `meditation` | 🧘 AI Meditation Guru | Inner peace and mindfulness |
| `bhakti` | 💝 AI Bhakti Guru | Devotion and divine love |
| `karma` | ⚖️ AI Karma Guru | Ethics and dharma |
| `yoga` | 🧘‍♀️ AI Yoga Guru | Breath and energy alignment |
| `sloka` | 🕉️ AI Sloka Guru | Sanskrit verses and sacred wisdom |

## Common Issues & Quick Fixes

### Backend Won't Start
```bash
# Check Python dependencies
pip install -r backend/requirements.txt

# Check environment variables
cat backend/.env | grep OPENAI_API_KEY

# Check port availability
lsof -i :5000
```

### Frontend Build Fails
```bash
# Clear and reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Check Node.js version
node --version  # Should be 18+
```

### API Errors
```bash
# Test API connectivity
curl http://localhost:5000/health

# Check CORS configuration
curl -H "Origin: http://localhost:3000" http://localhost:5000/api/gurus

# Validate OpenAI API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

## Development Workflow

### Running Tests
```bash
# Backend tests
cd backend
python -m pytest tests/ -v

# Frontend tests
npm test

# E2E tests
npm run test:e2e
```

### Code Quality
```bash
# Python linting
flake8 backend/

# JavaScript linting
npm run lint

# Format code
npm run format
```

### Docker Development
```bash
# Start all services
docker-compose up

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

## Deployment Quick Commands

### Production Build
```bash
# Frontend production build
npm run build

# Backend with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker Production
```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose ps
```

## Useful URLs

### Local Development
- Backend API: http://localhost:5000
- Frontend: http://localhost:3000
- Health Check: http://localhost:5000/health
- API Docs: http://localhost:5000/api/gurus

### Production
- Main Site: https://empowerhub360.org
- API Base: https://empowerhub360.org/api
- Health Check: https://empowerhub360.org/health

## Support Resources

### Documentation
- 📚 Complete guides in `/docs` folder
- 💻 Code examples in documentation
- 🔍 Troubleshooting guides for common issues

### Getting Help
- 🐛 GitHub Issues: Report bugs and request features
- 📧 Email: support@empowerhub360.org
- 📖 Docs: https://docs.empowerhub360.org

### Community
- 🌐 Website: https://empowerhub360.org
- 💬 GitHub Discussions: Ask questions and share ideas
- 🤝 Contributing: See README.md for contribution guidelines

## File Structure Overview

```
AI-Video-Generator-main/
├── backend/              # Flask API backend
│   ├── api/             # API endpoints
│   ├── services/        # Business logic
│   ├── app.py           # Main application
│   └── requirements.txt # Dependencies
├── docs/                # Documentation
├── static/              # Static assets
├── src/                 # React source
├── tests/               # Test suites
└── package.json         # Frontend dependencies
```

## Environment Variables Cheat Sheet

### Required
- `OPENAI_API_KEY` - OpenAI API key
- `SECRET_KEY` - Flask secret key

### Database
- `DATABASE_URL` - Database connection
- `REDIS_URL` - Redis cache URL

### Security
- `CORS_ORIGINS` - Allowed origins
- `RATE_LIMIT_PER_HOUR` - API rate limits

### Features
- `ENABLE_STREAMING=True` - Enable streaming responses
- `ENABLE_ANALYTICS=True` - Enable usage tracking

---

**Need more details?** Check the complete documentation in the `/docs` folder!