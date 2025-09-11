# AI Empower Heart Development Platform

![CI/CD Workflow](https://github.com/AI-Empower-HQ-360/AI-Video-Generator-main/actions/workflows/ci.yml/badge.svg)
![Enhanced CI/CD](https://github.com/AI-Empower-HQ-360/AI-Video-Generator-main/actions/workflows/enhanced-ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-brightgreen.svg)
![Node.js](https://img.shields.io/badge/node.js-18+-brightgreen.svg)

## Overview

AI Empower Heart is a comprehensive spiritual guidance platform powered by artificial intelligence. It provides personalized spiritual guidance through various AI gurus specializing in different aspects of spiritual development including meditation, devotion (bhakti), ethics (karma), yoga practices, and sacred Sanskrit teachings.

### Key Features

- **🙏 Multiple AI Spiritual Gurus**: Specialized AI personalities for different spiritual paths
- **💬 Real-time Guidance**: Instant spiritual advice and teachings
- **🔄 Streaming Responses**: Real-time response generation for better user experience
- **📖 Sanskrit Slokas**: Authentic verses from Bhagavad Gita, Upanishads, and Vedas
- **🧘 Meditation Guidance**: Personalized meditation instructions and techniques
- **🎯 Personalized Experience**: Context-aware responses based on user history
- **🌐 Cross-platform Support**: Web application with mobile-responsive design
- **🔊 Speech Integration**: Voice input through Whisper API integration

### Available Spiritual Gurus

| Guru | Specialization | Focus Area |
|------|----------------|------------|
| 🙏 Spiritual Guru | Soul consciousness and eternal identity | General spiritual wisdom |
| 🧘 Meditation Guru | Inner peace and mindfulness | Meditation techniques |
| 💝 Bhakti Guru | Devotion and divine love | Devotional practices |
| ⚖️ Karma Guru | Ethics and dharma | Righteous action and ethics |
| 🧘‍♀️ Yoga Guru | Breath and energy alignment | Physical and energy practices |
| 🕉️ Sloka Guru | Sanskrit verses and sacred wisdom | Ancient texts and meanings |

## Quick Start

### Prerequisites

- **Python 3.9+** with pip
- **Node.js 18+** with npm or yarn
- **OpenAI API Key** (required for AI functionality)
- **Git** for version control

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/AI-Empower-HQ-360/AI-Video-Generator-main.git
   cd AI-Video-Generator-main
   ```

2. **Backend Setup**
   ```bash
   cd backend
   
   # Install Python dependencies
   pip install -r requirements.txt
   
   # Configure environment
   cp .env.example .env
   # Edit .env with your OpenAI API key and other settings
   
   # Start the backend server
   python app.py
   ```

3. **Frontend Setup**
   ```bash
   # From project root
   npm install
   
   # Start development server
   npm run dev
   ```

4. **Verify Installation**
   ```bash
   # Check backend health
   curl http://localhost:5000/health
   
   # Access frontend
   open http://localhost:3000
   ```

## Architecture

### System Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React Frontend │────│  Flask API Backend │────│  OpenAI GPT API │
│   (Port 3000)   │    │   (Port 5000)     │    │     Service     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         │                        │                        │
    ┌─────────┐              ┌─────────┐              ┌─────────┐
    │ Static  │              │Database │              │ Redis   │
    │ Assets  │              │(SQLite) │              │ Cache   │
    └─────────┘              └─────────┘              └─────────┘
```

### Technology Stack

**Backend:**
- **Framework**: Flask (Python)
- **AI Integration**: OpenAI GPT-4/GPT-3.5-turbo
- **Database**: SQLite (development), PostgreSQL (production)
- **Caching**: Redis
- **API**: RESTful with SSE streaming support

**Frontend:**
- **Framework**: React with Vite
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Animations**: Framer Motion

**DevOps:**
- **Containerization**: Docker & Docker Compose
- **CI/CD**: GitHub Actions
- **Testing**: Pytest (backend), Jest (frontend), Playwright (E2E)
- **Linting**: ESLint, Flake8
- **Security**: Dependabot, CORS configuration

## Environment Configuration

### Required Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# Flask Configuration
SECRET_KEY=your-secret-key-here-make-it-long-and-random
FLASK_ENV=development
DEBUG=True

# OpenAI Configuration (Required)
OPENAI_API_KEY=sk-your-openai-api-key-here

# Database Configuration
DATABASE_URL=sqlite:///spiritual_platform.db

# Redis Configuration (Optional)
REDIS_URL=redis://localhost:6379

# CORS Configuration (Production)
CORS_ORIGINS=https://empowerhub360.org,https://www.empowerhub360.org

# Rate Limiting
RATE_LIMIT_PER_HOUR=100

# Email Configuration (Optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your-email@example.com
EMAIL_PASSWORD=your-app-password

# Analytics (Optional)
GOOGLE_ANALYTICS_ID=your-ga-id
```

### Google Cloud Services (Optional)

For Google Cloud integration, copy and configure:

```bash
cp key.example.json key.json
# Edit key.json with your Google Cloud service account credentials
```

> ⚠️ **Security Note**: Never commit `.env` or `key.json` files to version control. These files contain sensitive information and are excluded in `.gitignore`.

## API Documentation

### Core Endpoints

#### Health Check
```http
GET /health
```
Returns service health status and availability.

#### List Available Gurus
```http
GET /api/gurus
```
Returns all available spiritual gurus and their specializations.

#### Ask Spiritual Guru
```http
POST /api/gurus/ask
Content-Type: application/json

{
  "guru_type": "spiritual",
  "question": "How can I find inner peace?",
  "user_context": {
    "experience_level": "beginner"
  }
}
```

#### Streaming Guidance
```http
POST /api/gurus/ask/stream
Content-Type: application/json
Accept: text/event-stream

{
  "guru_type": "meditation",
  "question": "Guide me through a breathing exercise"
}
```

For complete API documentation, see [docs/API.md](docs/API.md).

## Development

### Project Structure

```
AI-Video-Generator-main/
├── backend/                 # Flask API backend
│   ├── api/                # API route blueprints
│   │   ├── gurus.py        # Spiritual guru endpoints
│   │   ├── users.py        # User management
│   │   ├── sessions.py     # Session handling
│   │   └── slokas.py       # Sanskrit content
│   ├── services/           # Business logic
│   │   ├── ai_service.py   # OpenAI integration
│   │   └── spiritual_service.py  # Spiritual guidance logic
│   ├── models/             # Data models
│   ├── utils/              # Utility functions
│   ├── app.py              # Main Flask application
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Environment template
├── src/                    # React frontend source
├── static/                 # Static assets
│   └── js/main.js          # Frontend JavaScript
├── templates/              # HTML templates
├── docs/                   # Documentation
│   ├── API.md              # API documentation
│   ├── SETUP.md            # Setup guide
│   ├── TROUBLESHOOTING.md  # Troubleshooting guide
│   └── AI_PROVIDERS.md     # AI limitations and error handling
├── tests/                  # Test suites
│   ├── test_gurus.py       # Backend API tests
│   ├── e2e/                # End-to-end tests
│   └── integration/        # Integration tests
├── package.json            # Node.js dependencies
├── docker-compose.yml      # Docker configuration
└── README.md               # This file
```

### Development Scripts

#### Backend Development
```bash
# Start development server
./run_dev.sh

# Run with Flask CLI
./run_flask.sh

# Start background services
./start_backend.sh

# Run Python tests
python -m pytest backend/tests/ -v

# Run with coverage
python -m pytest --cov=backend/services --cov-report=html
```

#### Frontend Development
```bash
# Start development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run unit tests
npm test

# Run E2E tests
npm run test:e2e

# Lint and format code
npm run lint
npm run format
```

### Code Quality

#### Linting and Formatting
```bash
# Python linting
flake8 backend/

# JavaScript linting
npm run lint

# Auto-fix linting issues
npm run lint:fix

# Format code
npm run format
```

#### Testing Strategy
- **Unit Tests**: Individual component/function testing
- **Integration Tests**: API endpoint testing
- **E2E Tests**: Full user workflow testing
- **Coverage Goals**: >80% code coverage

### Docker Development

#### Development with Docker
```bash
# Build and start all services
docker-compose up --build

# Run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

#### Production Deployment
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d
```

## AI Provider Integration

### OpenAI Configuration

The platform uses OpenAI's GPT models for spiritual guidance generation:

- **GPT-4**: Primary model for complex spiritual guidance
- **GPT-3.5-turbo**: Fallback model for faster responses
- **Streaming Support**: Real-time response generation
- **Context Management**: Maintains conversation context

### Rate Limiting & Error Handling

- **Automatic Retries**: Exponential backoff for rate limits
- **Model Fallback**: Automatic fallback to alternative models
- **Error Recovery**: Graceful degradation when AI services are unavailable
- **Cost Optimization**: Smart model selection based on query complexity

For detailed information on AI provider limitations and error handling strategies, see [docs/AI_PROVIDERS.md](docs/AI_PROVIDERS.md).

## Deployment

### Production Deployment Options

#### Option 1: Docker Deployment (Recommended)
```bash
# Clone repository
git clone https://github.com/AI-Empower-HQ-360/AI-Video-Generator-main.git
cd AI-Video-Generator-main

# Configure production environment
cp backend/.env.example backend/.env.production
# Edit .env.production with production settings

# Deploy with Docker
docker-compose -f docker-compose.prod.yml up -d
```

#### Option 2: Manual Deployment
```bash
# Setup production server
sudo apt update
sudo apt install python3 python3-pip nodejs npm nginx

# Deploy backend
cd backend
pip install -r requirements.txt
gunicorn -w 4 -b 127.0.0.1:5000 app:app

# Deploy frontend
npm run build
# Serve dist/ directory with nginx
```

### Environment-Specific Configuration

#### Development
- Debug mode enabled
- Hot reloading
- Detailed error messages
- CORS allows all origins

#### Production
- Debug mode disabled
- Optimized builds
- Error logging
- Restricted CORS origins
- SSL/HTTPS required
- Rate limiting enforced

## Monitoring and Analytics

### Application Monitoring
- **Health Checks**: Automated service health monitoring
- **Error Tracking**: Comprehensive error logging and reporting
- **Performance Metrics**: Response time and throughput monitoring
- **Usage Analytics**: User interaction and guru selection tracking

### AI Usage Monitoring
- **Token Usage**: Track OpenAI API token consumption
- **Cost Tracking**: Monitor AI service costs
- **Model Performance**: Track response quality and user satisfaction
- **Rate Limit Monitoring**: Monitor API rate limit usage

## Security Considerations

### API Security
- **CORS Configuration**: Properly configured for production domains
- **Rate Limiting**: Prevents abuse and ensures fair usage
- **Input Validation**: All inputs sanitized and validated
- **Error Handling**: Error messages don't expose sensitive information

### Data Protection
- **Environment Variables**: Sensitive data stored in environment variables
- **API Key Management**: Secure storage and rotation of API keys
- **User Privacy**: No personal data stored without consent
- **HTTPS**: All production traffic encrypted

### Content Safety
- **Input Filtering**: Prevent harmful or inappropriate content
- **Content Policy**: Adherence to OpenAI's usage policies
- **Moderation**: Automated content moderation for user inputs

## Contributing

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/spiritual-enhancement
   ```
3. **Make your changes**
4. **Add tests for new features**
5. **Run the test suite**
   ```bash
   npm test
   python -m pytest
   ```
6. **Submit a pull request**

### Code Standards

- **Python**: Follow PEP 8 style guidelines
- **JavaScript**: Follow ESLint configuration
- **Documentation**: Update docs for new features
- **Testing**: Maintain >80% test coverage
- **Commits**: Use conventional commit messages

### Issue Reporting

When reporting issues, please include:
- Environment details (OS, Python/Node versions)
- Steps to reproduce
- Expected vs actual behavior
- Error logs and stack traces
- Configuration details (anonymized)

## Troubleshooting

### Common Issues

#### Backend Issues
- **OpenAI API Key Error**: Ensure `OPENAI_API_KEY` is set in `.env`
- **Module Import Errors**: Check Python path and virtual environment
- **Port Conflicts**: Ensure port 5000 is available
- **Database Issues**: Check SQLite file permissions

#### Frontend Issues
- **Build Failures**: Clear `node_modules` and reinstall dependencies
- **CORS Errors**: Verify backend CORS configuration
- **Module Not Found**: Run `npm install` to install dependencies

#### API Issues
- **Rate Limiting**: Implement exponential backoff
- **Timeout Errors**: Increase request timeout settings
- **Authentication Failures**: Verify API key format and validity

For comprehensive troubleshooting guidance, see [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

## Documentation

### Complete Documentation

- **[API Documentation](docs/API.md)**: Complete API reference with examples
- **[Setup Guide](docs/SETUP.md)**: Detailed setup instructions for all environments
- **[Troubleshooting](docs/TROUBLESHOOTING.md)**: Common issues and solutions
- **[AI Providers](docs/AI_PROVIDERS.md)**: AI limitations and error handling strategies

### Additional Resources

- **Architecture Documentation**: [docs/architecture.md](docs/architecture.md)
- **Workflow Configuration**: [docs/chatgpt-workflow-configuration.md](docs/chatgpt-workflow-configuration.md)
- **Spiritual Content**: [docs/sloka_progression.md](docs/sloka_progression.md)

## Support and Community

### Getting Help

- **GitHub Issues**: Report bugs and request features
- **Documentation**: Comprehensive guides and API reference
- **Email Support**: support@empowerhub360.org

### Community Resources

- **Website**: https://empowerhub360.org
- **GitHub**: https://github.com/AI-Empower-HQ-360/AI-Video-Generator-main
- **Documentation**: https://docs.empowerhub360.org

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **OpenAI**: For providing the GPT models that power our AI gurus
- **Ancient Wisdom Traditions**: For the timeless spiritual teachings we share
- **Open Source Community**: For the tools and libraries that make this possible
- **Contributors**: Everyone who has contributed to making this platform better

---

**Made with 🙏 by the AI-Empower-HQ-360 team**

*Empowering hearts through AI-guided spiritual wisdom*
