# Testing Framework Documentation

## Overview
This document describes the comprehensive testing framework set up for the AI Empower Heart application, including unit tests, integration tests, and end-to-end (E2E) tests.

## Test Structure

### Unit Tests (Python - pytest)
Located in `/tests/` directory:

1. **test_youtube_service.py** - YouTube Integration Tests
   - URL extraction from various YouTube formats
   - Video information retrieval via YouTube API
   - Transcript fetching and processing
   - Error handling for disabled transcripts and unavailable videos
   - Tests: 13 passing, 2 skipped (require API key)

2. **test_ai_chat.py** - AI Chat Features Tests
   - Gurus API endpoint testing
   - Quick questions validation
   - Chat message validation and security
   - Guru configuration and prompt structure
   - Chat history and streaming functionality
   - Tests: 16 passing

3. **test_authentication.py** - Authentication & Security Tests
   - User registration validation
   - Login and authentication flows
   - Password security and hashing
   - JWT token management
   - Rate limiting configuration
   - CSRF protection
   - Tests: 22 passing

### End-to-End Tests (JavaScript - Playwright)
Located in `/tests/e2e/` directory:

1. **test_signin_navigation.spec.js** - Front-end E2E Tests
   - Sign-in functionality and form validation
   - Navigation between pages
   - Guru selection and interaction
   - AI chat interface with quick questions
   - Responsive design testing (mobile, tablet, desktop)

## Running Tests

### Python Unit Tests

```bash
# Run all unit tests
pytest

# Run specific test file
pytest tests/test_youtube_service.py

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test class
pytest tests/test_ai_chat.py::TestGurusAPI

# Run with verbose output
pytest -v
```

### JavaScript E2E Tests

```bash
# Install Playwright browsers (first time only)
npx playwright install

# Run all E2E tests
npm run test:e2e

# Run E2E tests in UI mode
npm run test:e2e:ui

# Run specific test file
npx playwright test tests/e2e/test_signin_navigation.spec.js
```

## Test Coverage

Current test coverage statistics:
- **Total Tests**: 51 unit tests + E2E tests
- **Passing**: 51/51 (100% of unit tests)
- **Skipped**: 3 (integration tests requiring API keys)
- **Code Coverage**: 25% (focused on new functionality)

### Coverage by Module
- YouTube Service: 36% coverage
- AI Chat Features: 39% coverage
- Authentication: 34% coverage
- Security Utils: 68% coverage

## Environment Setup for Tests

### Required Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# For YouTube integration tests
YOUTUBE_API_KEY=your-youtube-api-key

# For OpenAI integration tests
OPENAI_API_KEY=sk-your-openai-api-key

# For authentication tests
SECRET_KEY=test-secret-key
JWT_SECRET_KEY=test-jwt-secret
```

### Test Database

Tests use an in-memory SQLite database by default. No additional database setup required.

## Quick Questions Feature

The testing framework includes comprehensive tests for the AI assistance chat quick questions feature:

### Quick Questions Test Coverage
- Predefined questions for each guru type
- Question format validation (must end with '?')
- Question length validation (minimum 10 characters)
- Quick question button functionality (E2E)
- Quick question display and selection (E2E)

### Tested Guru Types
- Meditation Guru
- Spiritual Guru
- Karma Guru
- Bhakti Guru
- Yoga Guru
- Sloka Guru
- Bojan Guru

## Continuous Integration

Tests are configured to run automatically on:
- Pull request creation
- Push to main branch
- Scheduled daily runs

### CI Configuration
Tests run in GitHub Actions with:
- Python 3.12
- Node.js 20.x
- Playwright browsers (Chromium, Firefox, WebKit)

## Security Testing

Security-focused tests include:
- XSS attack prevention
- SQL injection prevention
- CSRF token validation
- Password strength requirements
- Rate limiting enforcement
- JWT token security
- Input validation and sanitization

## Best Practices

1. **Write tests first** - Follow TDD when adding new features
2. **Mock external APIs** - Use mocks for YouTube, OpenAI, etc.
3. **Test edge cases** - Include tests for error conditions
4. **Keep tests fast** - Use fixtures and mocks appropriately
5. **Maintain coverage** - Aim for >80% code coverage
6. **Update docs** - Keep this documentation current

## Troubleshooting

### Common Issues

1. **Import errors** - Ensure all dependencies are installed:
   ```bash
   pip install -r backend/requirements.txt
   npm install
   ```

2. **Playwright browser not installed**:
   ```bash
   npx playwright install chromium
   ```

3. **Tests failing due to missing API keys**:
   - Integration tests are skipped if API keys are not configured
   - Unit tests use mocks and don't require real API keys

## Future Enhancements

Planned improvements to the testing framework:
- [ ] Increase code coverage to >80%
- [ ] Add performance testing
- [ ] Add load testing for API endpoints
- [ ] Add visual regression testing
- [ ] Implement mutation testing
- [ ] Add API contract testing
- [ ] Expand E2E test scenarios

## Contributing

When adding new features:
1. Write unit tests for new functions/methods
2. Add integration tests for API endpoints
3. Create E2E tests for user-facing features
4. Update this documentation
5. Ensure all tests pass before submitting PR

## Test Results Summary

Last test run: 2024-01-11

```
======================== 51 passed, 3 skipped in 5.10s =========================

Unit Tests:
✅ YouTube Service: 13/13 passing
✅ AI Chat Features: 16/16 passing  
✅ Authentication: 22/22 passing

E2E Tests:
📝 Sign-in and Navigation (comprehensive test suite created)
```

## References

- [pytest Documentation](https://docs.pytest.org/)
- [Playwright Documentation](https://playwright.dev/)
- [Jest Documentation](https://jestjs.io/)
- [Testing Best Practices](https://testingjavascript.com/)
