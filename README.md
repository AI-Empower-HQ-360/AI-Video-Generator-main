# AI Empower Heart Development

![CI/CD Workflow](https://github.com/AI-Empower-HQ-360/ai-heart-development-main/actions/workflows/ci.yml/badge.svg)
![Enhanced CI/CD](https://github.com/AI-Empower-HQ-360/ai-heart-development-main/actions/workflows/enhanced-ci.yml/badge.svg)
![Security](https://img.shields.io/badge/Security-Enhanced-green)

## About

AI Empower Heart is a spiritual guidance platform powered by artificial intelligence. It provides personalized guidance through various AI gurus specializing in different aspects of spiritual development.

**🛡️ Security-First Implementation**: This platform implements comprehensive security measures including input validation, authentication, rate limiting, and secure API practices.

## Security Features

- ✅ **Input Validation**: XSS/SQL injection prevention, content sanitization
- ✅ **Authentication**: JWT-based auth with role-based access control
- ✅ **Rate Limiting**: Endpoint-specific protection against abuse
- ✅ **Security Headers**: CSP, HSTS, anti-clickjacking protection
- ✅ **CSRF Protection**: Token-based validation for state changes
- ✅ **File Upload Security**: Type validation and size limits
- ✅ **API Security**: OpenAI key validation and secure practices
- ✅ **Security Monitoring**: Comprehensive logging and threat detection

See [Security Documentation](docs/security.md) for detailed implementation details.

## Development

This project uses GitHub Actions for continuous integration and deployment.

### Setup

1. Clone the repository
2. Install dependencies
   - Python: `pip install -r backend/requirements.txt`
   - Node.js (if applicable): `npm install`

### Security Testing

Run the security test suite:
```bash
pytest tests/test_security.py -v
```

Run the security demonstration:
```bash
python demo_security.py
```

### Testing

- Run Python tests: `pytest`
- Run linting: `flake8`

## Environment Setup

1. Copy the example environment file:

   ```bash
   cp backend/.env.example backend/.env
   ```

2. Configure your environment variables in `.env`:
   - Set your OpenAI API key (use proper `sk-` format)
   - Set a strong secret key for JWT tokens
   - Configure rate limiting settings
   - Set secure session configurations

3. For Google Cloud Services integration:

   ```bash
   cp key.example.json key.json
   ```

   Then update `key.json` with your Google Cloud service account credentials.

> ⚠️ **Security Important**: Never commit `.env` or `key.json` files to version control. These files contain sensitive information and are excluded in `.gitignore`.

## Security Configuration

### Production Deployment

For production deployment, ensure:

- Set `FLASK_ENV=production`
- Use strong, unique secrets for `SECRET_KEY` and `JWT_SECRET_KEY`
- Enable HTTPS and set `SESSION_COOKIE_SECURE=True`
- Configure restrictive CORS origins
- Set up Redis for rate limiting
- Enable all security headers
- Review [Security Checklist](SECURITY_IMPLEMENTATION_CHECKLIST.md)

### Environment-Specific Security

- **Development**: Relaxed settings for local development
- **Production**: Strict security settings for public deployment
- **Testing**: Security features that don't interfere with tests

## API Endpoints

### Gurus API
- `GET /api/gurus` - List all available spiritual gurus
- `POST /api/gurus/ask` - Ask for spiritual guidance (with input validation)
- `POST /api/gurus/ask/stream` - Stream spiritual guidance responses

### Users API
- `POST /api/users/register` - Register new user (with password strength validation)
- `POST /api/users/login` - User authentication
- `GET /api/users/profile` - Get user profile (requires authentication)
- `POST /api/users/preferences` - Save user preferences (requires authentication)

### Security Endpoints
- `GET /api/security/csrf-token` - Get CSRF token for forms
- `GET /health` - Health check (rate limit exempt)

All endpoints include:
- Input validation and sanitization
- Rate limiting protection
- Security headers
- Comprehensive logging

## Security

This project implements enterprise-grade security measures:

- **OWASP Top 10** compliance
- **NIST Cybersecurity Framework** alignment
- **JWT Best Practices** (RFC 8725)
- **Comprehensive threat protection**
- **Security monitoring and logging**

See [Security Documentation](docs/security.md) for complete details.

### Security Dependencies

This project uses Dependabot to keep dependencies up to date and secure.

### Reporting Security Issues

If you discover a security vulnerability, please follow our [Security Policy](SECURITY.md).

## License

[Add your license information here]

---

**🛡️ Built with Security-First Principles**
