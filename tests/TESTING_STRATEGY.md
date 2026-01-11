# Comprehensive Testing Strategy for AI Video Generator

This document outlines the complete testing approach for the AI-powered spiritual guidance platform, including unit tests, integration tests, E2E tests, and proper mocking strategies for AI services.

## Table of Contents

1. [Testing Overview](#testing-overview)
2. [Unit Testing](#unit-testing)
3. [Integration Testing](#integration-testing)
4. [End-to-End Testing](#end-to-end-testing)
5. [AI Service Mocking](#ai-service-mocking)
6. [Test Coverage](#test-coverage)
7. [Running Tests](#running-tests)
8. [Best Practices](#best-practices)

## Testing Overview

Our testing strategy follows the testing pyramid approach:

```
      /\
     /  \
    / E2E \     <- Few, high-value end-to-end tests
   /______\
  /        \
 /Integration\ <- Medium number of integration tests
/__________\
/            \
/   Unit Tests  \ <- Many fast, focused unit tests
/______________\
```

### Technology Stack

- **Unit Tests**: Jest + React Testing Library
- **Integration Tests**: Jest + Supertest (for API testing)
- **E2E Tests**: Playwright
- **Mocking**: Custom AI service mocks
- **Coverage**: Jest built-in coverage reporting

## Unit Testing

### React Components

#### AvatarSystem Component

Tests cover:
- Loading states and avatar rendering
- Different guru types and sizes
- Click interactions and callbacks
- Error handling (image load failures)
- Accessibility features

```javascript
// Example test
it('handles click events correctly', async () => {
  const onAvatarClick = jest.fn();
  render(<AvatarSystem guruType="spiritual" onAvatarClick={onAvatarClick} />);
  
  await waitFor(() => {
    expect(screen.getByTestId('avatar-spiritual')).toBeInTheDocument();
  });

  fireEvent.click(screen.getByTestId('avatar-spiritual'));
  expect(onAvatarClick).toHaveBeenCalledWith('spiritual');
});
```

#### MultilingualEngine Component

Tests cover:
- Language selection and dropdown behavior
- Loading states during language changes
- Fallback handling for unknown languages
- Translation function integration

#### ScriptureDatabase Component

Tests cover:
- Search functionality and filtering
- Loading states and error handling
- Verse selection and callbacks
- Source filtering and pagination

### API Integration Modules

#### ChatGPT Integration

Tests cover:
- Basic chat functionality with different guru types
- Streaming responses and error handling
- Context preservation and user preferences
- Rate limiting and timeout scenarios

```javascript
// Example with mocking
import { chatWithGPT } from '../chatgpt-integration';
import { createMockFetch } from '../../__mocks__/aiServiceMocks';

global.fetch = createMockFetch({
  chatgpt: mockChatGPTResponses.spiritual
});

it('makes successful API call with custom parameters', async () => {
  const result = await chatWithGPT('What is dharma?', 'spiritual');
  
  expect(fetch).toHaveBeenCalledWith('http://localhost:5000/api/spiritual/guidance', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      guru_type: 'spiritual',
      question: 'What is dharma?',
      user_context: null,
      stream: false
    })
  });
  
  expect(result.success).toBe(true);
});
```

#### Claude Integration

Tests cover:
- Content generation for different spiritual topics
- Model selection and parameter configuration
- Streaming responses and error recovery
- Spiritual content quality validation

#### Text-to-Speech Integration

Tests cover:
- Audio generation with different voices and languages
- Spiritual tradition-specific voice mapping
- Streaming audio and download functionality
- Voice availability and fallback options

## Integration Testing

### Backend API Endpoints

#### Users API
- User registration and authentication
- Profile management and preferences
- Authorization and session handling

```python
# Example integration test
def test_save_user_preferences_success(self):
    preferences_data = {
        'language': 'hi',
        'guru_type': 'meditation',
        'notification_enabled': True
    }
    
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'message': 'Preferences saved'
        }
        mock_post.return_value = mock_response
        
        response = requests.post(
            f'{self.base_url}/api/users/preferences',
            headers=self.headers,
            json=preferences_data
        )
        
        assert response.status_code == 200
        assert response.json()['success'] is True
```

#### Sessions API
- Meditation session creation and tracking
- Session completion and feedback
- History retrieval and statistics

#### Gurus API
- Available guru types and specialties
- Chat interactions and context management
- Response quality and appropriateness

#### Slokas API
- Scripture search and retrieval
- Random verse generation
- Source filtering and categorization

## End-to-End Testing

### Critical User Flows

#### Complete User Journey
1. **Landing and Navigation**: Homepage display, responsive design
2. **Guru Selection**: Avatar interaction, chat interface activation
3. **Chat Experience**: Message sending, response handling, error scenarios
4. **User Registration**: Form validation, account creation, verification
5. **Session Tracking**: Meditation start/stop, feedback collection
6. **Multi-language Support**: Language switching, localized content

```javascript
// Example E2E test
test('should handle complete meditation session flow', async ({ page }) => {
  // Mock API responses
  await page.route('**/api/sessions', route => {
    route.fulfill({
      status: 201,
      contentType: 'application/json',
      body: JSON.stringify({
        success: true,
        session_id: 'session_456',
        status: 'active'
      })
    });
  });

  // Navigate through the flow
  await page.click('[data-testid="meditation-link"]');
  await page.click('[data-testid="guided-meditation"]');
  await page.click('[data-testid="start-session-button"]');
  
  // Verify session tracking
  await expect(page.locator('[data-testid="session-timer"]')).toBeVisible();
  await expect(page.locator('[data-testid="session-active"]')).toBeVisible();
  
  // Complete session
  await page.waitForTimeout(5000);
  await page.click('[data-testid="end-session-button"]');
  
  // Verify completion
  await expect(page.locator('[data-testid="session-completed"]')).toBeVisible();
});
```

### Error Handling and Edge Cases
- Network connectivity issues
- Slow API responses
- Invalid user input
- Browser compatibility

### Performance and Accessibility
- Load time optimization
- Keyboard navigation
- Screen reader compatibility
- Mobile responsiveness

## AI Service Mocking

### Comprehensive Mocking Strategy

We use a multi-layered mocking approach:

1. **Static Mocks**: Predefined responses for common scenarios
2. **Dynamic Mocks**: Configurable responses based on input
3. **Error Simulation**: Realistic failure scenarios
4. **Performance Simulation**: Realistic delays and timeouts

### Mock Response Examples

```javascript
// ChatGPT mock responses
export const mockChatGPTResponses = {
  spiritual: {
    question: 'What is dharma?',
    response: {
      success: true,
      response: 'Dharma is the righteous path of life...',
      guru_type: 'spiritual',
      context_used: true
    }
  }
};

// Advanced mocking with AIServiceMocker class
const mocker = new AIServiceMocker();
mocker.setResponse('chatgpt', 'What is meditation?', mockMeditationResponse);
mocker.setDelay('chatgpt', 1000); // 1 second delay
mocker.setErrorRate('chatgpt', 0.1); // 10% error rate

const mockChatGPT = mocker.createMockFunction('chatgpt');
```

### Streaming Response Mocking

```javascript
export function createMockStreamReader(chunks) {
  let index = 0;
  
  return {
    read: jest.fn(() => {
      if (index < chunks.length) {
        const chunk = chunks[index++];
        const encoded = new TextEncoder().encode(`data: ${JSON.stringify(chunk)}\n`);
        return Promise.resolve({ done: false, value: encoded });
      }
      return Promise.resolve({ done: true });
    })
  };
}
```

## Test Coverage

### Coverage Targets

- **Overall**: 80% minimum
- **Functions**: 80% minimum
- **Lines**: 80% minimum
- **Branches**: 80% minimum

### Coverage Configuration

```javascript
// jest.config.js
module.exports = {
  collectCoverageFrom: [
    'src/**/*.{js,jsx}',
    '!src/**/*.d.ts',
    '!src/**/index.js',
    '!src/reportWebVitals.js',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
};
```

### Generating Coverage Reports

```bash
npm run test:coverage
```

This generates detailed HTML coverage reports in the `coverage/` directory.

## Running Tests

### All Tests
```bash
npm test                 # Run all unit tests
npm run test:watch       # Run tests in watch mode
npm run test:coverage    # Run tests with coverage
npm run test:e2e         # Run E2E tests
npm run test:e2e:ui      # Run E2E tests with UI
```

### Specific Test Suites
```bash
npm test -- components          # Run component tests
npm test -- api                 # Run API integration tests
npm test -- AvatarSystem        # Run specific component tests
```

### Integration Tests (Python)
```bash
cd tests/integration/backend
pytest test_api_endpoints.py -v
```

### Continuous Integration

Tests run automatically on:
- Pull request creation
- Commit to main branch
- Scheduled nightly runs

## Best Practices

### Writing Effective Tests

1. **Follow AAA Pattern**: Arrange, Act, Assert
2. **Use Descriptive Names**: Tests should read like documentation
3. **Test Behavior, Not Implementation**: Focus on what the code does
4. **Keep Tests Independent**: No shared state between tests
5. **Mock External Dependencies**: Isolate units under test

### Component Testing

```javascript
// Good: Tests behavior
it('displays error message when API call fails', async () => {
  // Arrange
  const mockError = new Error('API Error');
  global.fetch = jest.fn().mockRejectedValue(mockError);
  
  // Act
  render(<ChatInterface />);
  fireEvent.click(screen.getByText('Send Message'));
  
  // Assert
  await waitFor(() => {
    expect(screen.getByText('Failed to send message')).toBeInTheDocument();
  });
});
```

### API Testing

```javascript
// Good: Tests integration points
it('should handle rate limiting gracefully', async () => {
  global.fetch = jest.fn().mockResolvedValue({
    ok: false,
    status: 429,
    json: () => Promise.resolve({ error: 'Rate limit exceeded' })
  });
  
  await expect(chatWithGPT('test')).rejects.toThrow('HTTP error! status: 429');
});
```

### E2E Testing

```javascript
// Good: Tests complete user scenarios
test('user can complete spiritual guidance session', async ({ page }) => {
  await page.goto('/');
  await page.click('[data-testid="spiritual-guru"]');
  await page.fill('[data-testid="message-input"]', 'How can I find inner peace?');
  await page.click('[data-testid="send-button"]');
  
  await expect(page.locator('[data-testid="guru-response"]')).toBeVisible();
  await expect(page.locator('text=inner peace')).toBeVisible();
});
```

### Debugging Tests

1. **Use `screen.debug()`**: Inspect rendered component state
2. **Add `waitFor()`**: Handle asynchronous operations
3. **Check Mock Calls**: `expect(mockFn).toHaveBeenCalledWith(...)`
4. **Use `act()`**: Wrap state updates in React
5. **Enable Verbose Output**: `npm test -- --verbose`

### Performance Testing

```javascript
// Measure API response times
it('should respond within acceptable time limits', async () => {
  const { result, responseTime } = await measureResponseTime(chatWithGPT)('test');
  
  expect(result.success).toBe(true);
  expect(responseTime).toBeLessThan(2000); // 2 seconds
});
```

## Conclusion

This comprehensive testing strategy ensures:

- **Reliability**: All critical paths are tested
- **Maintainability**: Tests are well-organized and documented
- **Performance**: Response times and load handling are verified
- **Accessibility**: User experience is validated across devices
- **Robustness**: Error scenarios and edge cases are covered

Regular test execution and maintenance keeps the application stable and ready for continuous deployment.