import { 
  chatWithClaude, 
  getAvailableClaudeModels, 
  streamChatWithClaude, 
  generateSpiritualContent 
} from '../claude-integration';

// Mock fetch globally
global.fetch = jest.fn();

describe('Claude Integration', () => {
  beforeEach(() => {
    fetch.mockClear();
    process.env.REACT_APP_API_URL = 'http://localhost:5000';
  });

  afterEach(() => {
    delete process.env.REACT_APP_API_URL;
  });

  describe('chatWithClaude', () => {
    it('makes successful API call with default parameters', async () => {
      const mockResponse = {
        success: true,
        response: 'This is Claude\'s response.',
        model: 'claude-3-sonnet',
        usage: { tokens: 150 }
      };

      fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      });

      const result = await chatWithClaude('Hello Claude');

      expect(fetch).toHaveBeenCalledWith('http://localhost:5000/api/claude/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: 'Hello Claude',
          model: 'claude-3-sonnet',
          max_tokens: 1000,
          temperature: 0.7,
          system_prompts: []
        })
      });

      expect(result).toEqual(mockResponse);
    });

    it('makes API call with custom options', async () => {
      const mockResponse = { success: true, response: 'Custom response' };
      const options = {
        maxTokens: 2000,
        temperature: 0.9,
        systemPrompts: ['You are a helpful assistant', 'Be creative']
      };

      fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      });

      await chatWithClaude('Creative request', 'claude-3-opus', options);

      expect(fetch).toHaveBeenCalledWith('http://localhost:5000/api/claude/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: 'Creative request',
          model: 'claude-3-opus',
          max_tokens: 2000,
          temperature: 0.9,
          system_prompts: ['You are a helpful assistant', 'Be creative']
        })
      });
    });

    it('handles API errors', async () => {
      fetch.mockResolvedValue({
        ok: false,
        status: 429
      });

      await expect(chatWithClaude('Test message')).rejects.toThrow('HTTP error! status: 429');
    });

    it('handles network errors', async () => {
      fetch.mockRejectedValue(new Error('Network failure'));

      await expect(chatWithClaude('Test message')).rejects.toThrow('Network failure');
    });

    it('logs errors to console', async () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
      
      fetch.mockRejectedValue(new Error('Test error'));

      try {
        await chatWithClaude('Test message');
      } catch (error) {
        // Expected to throw
      }

      expect(consoleSpy).toHaveBeenCalledWith('Error communicating with Claude:', expect.any(Error));
      
      consoleSpy.mockRestore();
    });
  });

  describe('getAvailableClaudeModels', () => {
    it('returns correct list of Claude models', () => {
      const models = getAvailableClaudeModels();
      
      expect(models).toEqual([
        'claude-3-opus',
        'claude-3-sonnet', 
        'claude-3-haiku',
        'claude-2.1',
        'claude-2.0'
      ]);
    });

    it('returns array type', () => {
      const models = getAvailableClaudeModels();
      expect(Array.isArray(models)).toBe(true);
    });
  });

  describe('streamChatWithClaude', () => {
    let mockReader;
    let mockResponse;

    beforeEach(() => {
      mockReader = {
        read: jest.fn()
      };

      mockResponse = {
        ok: true,
        body: {
          getReader: () => mockReader
        }
      };
    });

    it('makes successful streaming API call', async () => {
      const onChunk = jest.fn();
      const options = { temperature: 0.8 };

      mockReader.read
        .mockResolvedValueOnce({ done: false, value: new TextEncoder().encode('data: {"text": "Hello"}\n') })
        .mockResolvedValueOnce({ done: false, value: new TextEncoder().encode('data: [DONE]\n') })
        .mockResolvedValueOnce({ done: true });

      fetch.mockResolvedValue(mockResponse);

      await streamChatWithClaude('Test message', onChunk, 'claude-3-haiku', options);

      expect(fetch).toHaveBeenCalledWith('http://localhost:5000/api/claude/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: 'Test message',
          model: 'claude-3-haiku',
          temperature: 0.8
        })
      });

      expect(onChunk).toHaveBeenCalledWith({ text: 'Hello' });
    });

    it('handles malformed JSON in stream gracefully', async () => {
      const onChunk = jest.fn();
      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation(() => {});

      mockReader.read
        .mockResolvedValueOnce({ done: false, value: new TextEncoder().encode('data: {invalid json}\n') })
        .mockResolvedValueOnce({ done: true });

      fetch.mockResolvedValue(mockResponse);

      await streamChatWithClaude('Test message', onChunk);

      expect(consoleSpy).toHaveBeenCalledWith('Malformed JSON in Claude stream:', '{invalid json}');
      expect(onChunk).not.toHaveBeenCalled();
      
      consoleSpy.mockRestore();
    });

    it('stops processing when [DONE] is received', async () => {
      const onChunk = jest.fn();

      mockReader.read
        .mockResolvedValueOnce({ done: false, value: new TextEncoder().encode('data: [DONE]\n') });

      fetch.mockResolvedValue(mockResponse);

      await streamChatWithClaude('Test message', onChunk);

      expect(onChunk).not.toHaveBeenCalled();
    });

    it('handles streaming API errors', async () => {
      fetch.mockResolvedValue({
        ok: false,
        status: 500
      });

      await expect(
        streamChatWithClaude('Test message', jest.fn())
      ).rejects.toThrow('HTTP error! status: 500');
    });
  });

  describe('generateSpiritualContent', () => {
    it('generates spiritual content with correct parameters', async () => {
      const mockResponse = {
        success: true,
        content: 'Generated spiritual explanation about karma'
      };

      fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      });

      const result = await generateSpiritualContent('karma', 'explanation', 'en');

      expect(fetch).toHaveBeenCalledWith('http://localhost:5000/api/claude/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: expect.stringContaining('Generate a explanation about karma in en language'),
          model: 'claude-3-sonnet',
          max_tokens: 1500,
          temperature: 0.8,
          system_prompts: expect.arrayContaining([
            expect.stringContaining('wise spiritual teacher'),
            expect.stringContaining('authentic, respectful'),
            expect.stringContaining('inclusive and non-dogmatic')
          ])
        })
      });

      expect(result).toEqual(mockResponse);
    });

    it('uses default parameters when not provided', async () => {
      fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ success: true })
      });

      await generateSpiritualContent('meditation');

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:5000/api/claude/chat',
        expect.objectContaining({
          body: expect.stringContaining('explanation about meditation in en language')
        })
      );
    });

    it('handles content generation errors', async () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
      
      fetch.mockRejectedValue(new Error('Content generation failed'));

      await expect(
        generateSpiritualContent('karma')
      ).rejects.toThrow('Content generation failed');

      expect(consoleSpy).toHaveBeenCalledWith(
        'Error generating spiritual content with Claude:', 
        expect.any(Error)
      );
      
      consoleSpy.mockRestore();
    });

    it('generates different types of content', async () => {
      fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ success: true })
      });

      await generateSpiritualContent('compassion', 'verse', 'hi');

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:5000/api/claude/chat',
        expect.objectContaining({
          body: expect.stringContaining('Generate a verse about compassion in hi language')
        })
      );
    });
  });
});