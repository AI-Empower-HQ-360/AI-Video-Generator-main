import { chatWithGPT, getAvailableGuruTypes, streamChatWithGPT } from '../chatgpt-integration';

// Mock fetch globally
global.fetch = jest.fn();

describe('ChatGPT Integration', () => {
  beforeEach(() => {
    fetch.mockClear();
    process.env.REACT_APP_API_URL = 'http://localhost:5000';
  });

  afterEach(() => {
    delete process.env.REACT_APP_API_URL;
  });

  describe('chatWithGPT', () => {
    it('makes successful API call with default parameters', async () => {
      const mockResponse = {
        success: true,
        response: 'This is spiritual guidance from the AI guru.',
        guruType: 'spiritual'
      };

      fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      });

      const result = await chatWithGPT('What is the meaning of life?');

      expect(fetch).toHaveBeenCalledWith('http://localhost:5000/api/spiritual/guidance', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          guru_type: 'spiritual',
          question: 'What is the meaning of life?',
          user_context: null,
          stream: false
        })
      });

      expect(result).toEqual(mockResponse);
    });

    it('makes API call with custom parameters', async () => {
      const mockResponse = { success: true, response: 'Meditation guidance' };
      const userContext = { userId: '123', preferences: { language: 'en' } };

      fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      });

      await chatWithGPT(
        'How to meditate?', 
        'meditation', 
        userContext, 
        true
      );

      expect(fetch).toHaveBeenCalledWith('http://localhost:5000/api/spiritual/guidance', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          guru_type: 'meditation',
          question: 'How to meditate?',
          user_context: userContext,
          stream: true
        })
      });
    });

    it('handles API errors', async () => {
      fetch.mockResolvedValue({
        ok: false,
        status: 500
      });

      await expect(chatWithGPT('Test question')).rejects.toThrow('HTTP error! status: 500');
    });

    it('handles network errors', async () => {
      fetch.mockRejectedValue(new Error('Network error'));

      await expect(chatWithGPT('Test question')).rejects.toThrow('Network error');
    });

    it('uses fallback API URL when env var is not set', async () => {
      delete process.env.REACT_APP_API_URL;
      
      fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ success: true })
      });

      await chatWithGPT('Test question');

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:5000/api/spiritual/guidance',
        expect.any(Object)
      );
    });

    it('logs errors to console', async () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
      
      fetch.mockRejectedValue(new Error('Test error'));

      try {
        await chatWithGPT('Test question');
      } catch (error) {
        // Expected to throw
      }

      expect(consoleSpy).toHaveBeenCalledWith('Error communicating with ChatGPT:', expect.any(Error));
      
      consoleSpy.mockRestore();
    });
  });

  describe('getAvailableGuruTypes', () => {
    it('returns correct list of guru types', () => {
      const guruTypes = getAvailableGuruTypes();
      
      expect(guruTypes).toEqual([
        'spiritual',
        'sloka', 
        'meditation',
        'bhakti',
        'karma',
        'yoga'
      ]);
    });

    it('returns array type', () => {
      const guruTypes = getAvailableGuruTypes();
      expect(Array.isArray(guruTypes)).toBe(true);
    });
  });

  describe('streamChatWithGPT', () => {
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
      const userContext = { userId: '123' };

      // Mock streaming response
      mockReader.read
        .mockResolvedValueOnce({ done: false, value: new TextEncoder().encode('data: {"text": "Hello"}\n') })
        .mockResolvedValueOnce({ done: false, value: new TextEncoder().encode('data: [DONE]\n') })
        .mockResolvedValueOnce({ done: true });

      fetch.mockResolvedValue(mockResponse);

      await streamChatWithGPT('Test question', 'spiritual', onChunk, userContext);

      expect(fetch).toHaveBeenCalledWith('http://localhost:5000/api/spiritual/guidance/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          guru_type: 'spiritual',
          question: 'Test question',
          user_context: userContext
        })
      });

      expect(onChunk).toHaveBeenCalledWith({ text: 'Hello' });
    });

    it('handles malformed JSON in stream gracefully', async () => {
      const onChunk = jest.fn();
      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation(() => {});

      // Mock streaming response with malformed JSON
      mockReader.read
        .mockResolvedValueOnce({ done: false, value: new TextEncoder().encode('data: {malformed json}\n') })
        .mockResolvedValueOnce({ done: true });

      fetch.mockResolvedValue(mockResponse);

      await streamChatWithGPT('Test question', 'spiritual', onChunk);

      expect(consoleSpy).toHaveBeenCalledWith('Malformed JSON in stream:', '{malformed json}');
      expect(onChunk).not.toHaveBeenCalled();
      
      consoleSpy.mockRestore();
    });

    it('handles multiple chunks in single read', async () => {
      const onChunk = jest.fn();

      // Mock streaming response with multiple data lines
      mockReader.read
        .mockResolvedValueOnce({ 
          done: false, 
          value: new TextEncoder().encode('data: {"text": "First"}\ndata: {"text": "Second"}\n') 
        })
        .mockResolvedValueOnce({ done: false, value: new TextEncoder().encode('data: [DONE]\n') })
        .mockResolvedValueOnce({ done: true });

      fetch.mockResolvedValue(mockResponse);

      await streamChatWithGPT('Test question', 'spiritual', onChunk);

      expect(onChunk).toHaveBeenCalledTimes(2);
      expect(onChunk).toHaveBeenNthCalledWith(1, { text: 'First' });
      expect(onChunk).toHaveBeenNthCalledWith(2, { text: 'Second' });
    });

    it('stops processing when [DONE] is received', async () => {
      const onChunk = jest.fn();

      mockReader.read
        .mockResolvedValueOnce({ done: false, value: new TextEncoder().encode('data: [DONE]\n') });

      fetch.mockResolvedValue(mockResponse);

      await streamChatWithGPT('Test question', 'spiritual', onChunk);

      expect(onChunk).not.toHaveBeenCalled();
    });

    it('handles streaming API errors', async () => {
      fetch.mockResolvedValue({
        ok: false,
        status: 500
      });

      await expect(
        streamChatWithGPT('Test question', 'spiritual', jest.fn())
      ).rejects.toThrow('HTTP error! status: 500');
    });

    it('handles network errors during streaming', async () => {
      fetch.mockRejectedValue(new Error('Network error'));

      await expect(
        streamChatWithGPT('Test question', 'spiritual', jest.fn())
      ).rejects.toThrow('Network error');
    });

    it('logs streaming errors to console', async () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
      
      fetch.mockRejectedValue(new Error('Stream error'));

      try {
        await streamChatWithGPT('Test question', 'spiritual', jest.fn());
      } catch (error) {
        // Expected to throw
      }

      expect(consoleSpy).toHaveBeenCalledWith('Error streaming with ChatGPT:', expect.any(Error));
      
      consoleSpy.mockRestore();
    });

    it('uses default parameters when not provided', async () => {
      const onChunk = jest.fn();

      mockReader.read.mockResolvedValueOnce({ done: true });
      fetch.mockResolvedValue(mockResponse);

      await streamChatWithGPT('Test question', undefined, onChunk);

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:5000/api/spiritual/guidance/stream',
        expect.objectContaining({
          body: JSON.stringify({
            guru_type: 'spiritual',
            question: 'Test question',
            user_context: null
          })
        })
      );
    });
  });
});