import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ChatInterface } from '../ChatInterface';
import { 
  createMockFetch, 
  mockChatGPTResponses, 
  AIServiceMocker,
  generateMockUser 
} from '../../__mocks__/aiServiceMocks';

// Mock the API modules
jest.mock('../api/chatgpt-integration');

describe('ChatInterface Component - Advanced Mocking Examples', () => {
  let mockUser;
  let originalFetch;

  beforeEach(() => {
    originalFetch = global.fetch;
    mockUser = generateMockUser({
      preferences: { 
        language: 'en', 
        guru_type: 'spiritual',
        voice_preference: 'calm'
      }
    });
  });

  afterEach(() => {
    global.fetch = originalFetch;
  });

  describe('Basic Chat Functionality with Mocks', () => {
    it('should handle successful chat interaction', async () => {
      // Use comprehensive mock fetch
      global.fetch = createMockFetch({
        chatgpt: mockChatGPTResponses.spiritual
      });

      render(<ChatInterface user={mockUser} />);
      
      const input = screen.getByTestId('chat-input');
      const sendButton = screen.getByTestId('send-button');
      
      fireEvent.change(input, { target: { value: 'What is dharma?' } });
      fireEvent.click(sendButton);
      
      await waitFor(() => {
        expect(screen.getByTestId('guru-response')).toBeInTheDocument();
      });
      
      expect(screen.getByText(/dharma is one of the most fundamental concepts/i)).toBeInTheDocument();
    });

    it('should handle different guru types', async () => {
      global.fetch = createMockFetch({
        chatgpt: mockChatGPTResponses.meditation
      });

      render(<ChatInterface user={mockUser} guruType="meditation" />);
      
      fireEvent.change(screen.getByTestId('chat-input'), { 
        target: { value: 'How to start meditation?' } 
      });
      fireEvent.click(screen.getByTestId('send-button'));
      
      await waitFor(() => {
        expect(screen.getByText(/to begin meditation/i)).toBeInTheDocument();
      });
    });
  });

  describe('Advanced AI Service Mocking', () => {
    it('should handle realistic response delays', async () => {
      const mocker = new AIServiceMocker();
      mocker.setResponse('chatgpt', 'test question', {
        success: true,
        response: 'Delayed wisdom response'
      });
      mocker.setDelay('chatgpt', 1500); // 1.5 second delay
      
      const mockChatFn = mocker.createMockFunction('chatgpt');
      
      const startTime = Date.now();
      const result = await mockChatFn('test question');
      const endTime = Date.now();
      
      expect(result.response).toBe('Delayed wisdom response');
      expect(endTime - startTime).toBeGreaterThan(1400);
    });

    it('should simulate intermittent service failures', async () => {
      const mocker = new AIServiceMocker();
      mocker.setErrorRate('chatgpt', 1.0); // 100% error rate for testing
      
      const mockChatFn = mocker.createMockFunction('chatgpt');
      
      await expect(mockChatFn('test')).rejects.toThrow('Simulated chatgpt error');
    });

    it('should handle context-aware responses', async () => {
      const contextualResponses = new Map();
      contextualResponses.set('What is karma?', {
        success: true,
        response: 'Karma is the law of cause and effect...'
      });
      contextualResponses.set('Tell me more about karma', {
        success: true,
        response: 'Building on the previous explanation, karma operates on multiple levels...'
      });

      const mocker = new AIServiceMocker();
      mocker.setResponse('chatgpt', 'What is karma?', contextualResponses.get('What is karma?'));
      mocker.setResponse('chatgpt', 'Tell me more about karma', contextualResponses.get('Tell me more about karma'));

      const mockChatFn = mocker.createMockFunction('chatgpt');

      // First question
      const response1 = await mockChatFn('What is karma?');
      expect(response1.response).toContain('law of cause and effect');

      // Follow-up question
      const response2 = await mockChatFn('Tell me more about karma');
      expect(response2.response).toContain('Building on the previous explanation');
    });
  });

  describe('Error Handling with Mocks', () => {
    it('should handle network errors gracefully', async () => {
      global.fetch = jest.fn().mockRejectedValue(new Error('Network error'));

      render(<ChatInterface user={mockUser} />);
      
      fireEvent.change(screen.getByTestId('chat-input'), { 
        target: { value: 'test message' } 
      });
      fireEvent.click(screen.getByTestId('send-button'));
      
      await waitFor(() => {
        expect(screen.getByTestId('error-message')).toBeInTheDocument();
      });
      
      expect(screen.getByText(/connection error/i)).toBeInTheDocument();
    });

    it('should handle rate limiting', async () => {
      global.fetch = jest.fn().mockResolvedValue({
        ok: false,
        status: 429,
        json: () => Promise.resolve({
          error: 'Rate limit exceeded',
          retry_after: 60
        })
      });

      render(<ChatInterface user={mockUser} />);
      
      fireEvent.change(screen.getByTestId('chat-input'), { 
        target: { value: 'test message' } 
      });
      fireEvent.click(screen.getByTestId('send-button'));
      
      await waitFor(() => {
        expect(screen.getByText(/rate limit exceeded/i)).toBeInTheDocument();
      });
      
      expect(screen.getByTestId('retry-timer')).toBeInTheDocument();
    });

    it('should handle malformed API responses', async () => {
      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({
          // Missing required fields
          incomplete: true
        })
      });

      render(<ChatInterface user={mockUser} />);
      
      fireEvent.change(screen.getByTestId('chat-input'), { 
        target: { value: 'test message' } 
      });
      fireEvent.click(screen.getByTestId('send-button'));
      
      await waitFor(() => {
        expect(screen.getByText(/unexpected response format/i)).toBeInTheDocument();
      });
    });
  });

  describe('Multilingual Support with Mocks', () => {
    it('should handle Hindi language responses', async () => {
      const hindiUser = generateMockUser({
        preferences: { language: 'hi', guru_type: 'spiritual' }
      });

      global.fetch = createMockFetch({
        chatgpt: {
          success: true,
          response: 'धर्म एक व्यापक अवधारणा है जो जीवन के सभी पहलुओं को शामिल करती है...',
          guru_type: 'spiritual',
          language: 'hi'
        }
      });

      render(<ChatInterface user={hindiUser} />);
      
      fireEvent.change(screen.getByTestId('chat-input'), { 
        target: { value: 'धर्म क्या है?' } 
      });
      fireEvent.click(screen.getByTestId('send-button'));
      
      await waitFor(() => {
        expect(screen.getByText(/धर्म एक व्यापक अवधारणा है/)).toBeInTheDocument();
      });
    });

    it('should fallback to English for unsupported languages', async () => {
      const unknownLangUser = generateMockUser({
        preferences: { language: 'unknown', guru_type: 'spiritual' }
      });

      global.fetch = createMockFetch({
        chatgpt: {
          success: true,
          response: 'I understand you prefer another language, but I can respond in English...',
          guru_type: 'spiritual',
          language: 'en',
          fallback_used: true
        }
      });

      render(<ChatInterface user={unknownLangUser} />);
      
      fireEvent.change(screen.getByTestId('chat-input'), { 
        target: { value: 'test question' } 
      });
      fireEvent.click(screen.getByTestId('send-button'));
      
      await waitFor(() => {
        expect(screen.getByText(/respond in english/i)).toBeInTheDocument();
      });
      
      expect(screen.getByTestId('language-fallback-notice')).toBeInTheDocument();
    });
  });

  describe('Performance and Load Testing with Mocks', () => {
    it('should handle multiple rapid requests', async () => {
      let requestCount = 0;
      global.fetch = jest.fn().mockImplementation(() => {
        requestCount++;
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            success: true,
            response: `Response ${requestCount}`,
            request_id: `req_${requestCount}`
          })
        });
      });

      render(<ChatInterface user={mockUser} />);
      
      const input = screen.getByTestId('chat-input');
      const sendButton = screen.getByTestId('send-button');
      
      // Send multiple rapid requests
      for (let i = 1; i <= 5; i++) {
        fireEvent.change(input, { target: { value: `Question ${i}` } });
        fireEvent.click(sendButton);
      }
      
      await waitFor(() => {
        expect(screen.getAllByTestId('guru-response')).toHaveLength(5);
      });
      
      expect(global.fetch).toHaveBeenCalledTimes(5);
    });

    it('should show loading states during API calls', async () => {
      global.fetch = jest.fn().mockImplementation(() => 
        new Promise(resolve => 
          setTimeout(() => resolve({
            ok: true,
            json: () => Promise.resolve({
              success: true,
              response: 'Delayed response'
            })
          }), 2000)
        )
      );

      render(<ChatInterface user={mockUser} />);
      
      fireEvent.change(screen.getByTestId('chat-input'), { 
        target: { value: 'test message' } 
      });
      fireEvent.click(screen.getByTestId('send-button'));
      
      // Should show loading immediately
      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
      expect(screen.getByTestId('send-button')).toBeDisabled();
      
      // Should hide loading after response
      await waitFor(() => {
        expect(screen.queryByTestId('loading-spinner')).not.toBeInTheDocument();
      }, { timeout: 3000 });
      
      expect(screen.getByTestId('send-button')).toBeEnabled();
    });
  });

  describe('Accessibility with Mocks', () => {
    it('should announce responses to screen readers', async () => {
      global.fetch = createMockFetch({
        chatgpt: mockChatGPTResponses.spiritual
      });

      render(<ChatInterface user={mockUser} />);
      
      fireEvent.change(screen.getByTestId('chat-input'), { 
        target: { value: 'What is meditation?' } 
      });
      fireEvent.click(screen.getByTestId('send-button'));
      
      await waitFor(() => {
        expect(screen.getByRole('status')).toHaveTextContent(/response received/i);
      });
      
      expect(screen.getByLabelText(/guru response/i)).toBeInTheDocument();
    });

    it('should support keyboard navigation', async () => {
      render(<ChatInterface user={mockUser} />);
      
      const input = screen.getByTestId('chat-input');
      const sendButton = screen.getByTestId('send-button');
      
      // Focus should move correctly with Tab
      input.focus();
      expect(document.activeElement).toBe(input);
      
      fireEvent.keyDown(input, { key: 'Tab' });
      expect(document.activeElement).toBe(sendButton);
      
      // Enter should submit from input
      input.focus();
      fireEvent.change(input, { target: { value: 'test message' } });
      fireEvent.keyDown(input, { key: 'Enter' });
      
      // Should show loading or response
      await waitFor(() => {
        expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
      });
    });
  });
});