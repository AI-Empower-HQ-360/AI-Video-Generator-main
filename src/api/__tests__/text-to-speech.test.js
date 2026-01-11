import { 
  textToSpeech, 
  getAvailableVoices, 
  streamTextToSpeech, 
  spiritualTextToSpeech,
  getTTSStatus,
  downloadAudio
} from '../text-to-speech';

// Mock fetch globally
global.fetch = jest.fn();

describe('Text-to-Speech Integration', () => {
  beforeEach(() => {
    fetch.mockClear();
    process.env.REACT_APP_API_URL = 'http://localhost:5000';
  });

  afterEach(() => {
    delete process.env.REACT_APP_API_URL;
  });

  describe('textToSpeech', () => {
    it('makes successful API call with default parameters', async () => {
      const mockResponse = {
        success: true,
        audioUrl: 'http://example.com/audio.mp3',
        duration: 5.2,
        audioId: 'audio_123'
      };

      fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      });

      const result = await textToSpeech('Hello world');

      expect(fetch).toHaveBeenCalledWith('http://localhost:5000/api/tts/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: 'Hello world',
          voice: 'neutral',
          language: 'en',
          speed: 1.0,
          format: 'mp3'
        })
      });

      expect(result).toEqual(mockResponse);
    });

    it('makes API call with custom options', async () => {
      const mockResponse = { success: true, audioUrl: 'custom.wav' };
      const options = {
        voice: 'female',
        language: 'hi',
        speed: 1.5,
        format: 'wav'
      };

      fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      });

      await textToSpeech('नमस्ते', options);

      expect(fetch).toHaveBeenCalledWith('http://localhost:5000/api/tts/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: 'नमस्ते',
          voice: 'female',
          language: 'hi',
          speed: 1.5,
          format: 'wav'
        })
      });
    });

    it('handles API errors', async () => {
      fetch.mockResolvedValue({
        ok: false,
        status: 400
      });

      await expect(textToSpeech('Test text')).rejects.toThrow('HTTP error! status: 400');
    });

    it('handles network errors', async () => {
      fetch.mockRejectedValue(new Error('Network error'));

      await expect(textToSpeech('Test text')).rejects.toThrow('Network error');
    });

    it('logs errors to console', async () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
      
      fetch.mockRejectedValue(new Error('TTS error'));

      try {
        await textToSpeech('Test text');
      } catch (error) {
        // Expected to throw
      }

      expect(consoleSpy).toHaveBeenCalledWith('Error generating speech:', expect.any(Error));
      
      consoleSpy.mockRestore();
    });
  });

  describe('getAvailableVoices', () => {
    it('fetches available voices successfully', async () => {
      const mockVoices = {
        voices: [
          { id: 'en-male-1', name: 'English Male', language: 'en', gender: 'male' },
          { id: 'en-female-1', name: 'English Female', language: 'en', gender: 'female' }
        ]
      };

      fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockVoices)
      });

      const result = await getAvailableVoices('en');

      expect(fetch).toHaveBeenCalledWith('http://localhost:5000/api/tts/voices?language=en');
      expect(result).toEqual(mockVoices.voices);
    });

    it('returns fallback voices on API error', async () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
      
      fetch.mockRejectedValue(new Error('API error'));

      const result = await getAvailableVoices('en');

      expect(result).toEqual([
        { id: 'en-male', name: 'English Male', language: 'en', gender: 'male' },
        { id: 'en-female', name: 'English Female', language: 'en', gender: 'female' },
        { id: 'hi-male', name: 'Hindi Male', language: 'hi', gender: 'male' },
        { id: 'hi-female', name: 'Hindi Female', language: 'hi', gender: 'female' }
      ]);

      consoleSpy.mockRestore();
    });

    it('handles empty voices response', async () => {
      fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({})
      });

      const result = await getAvailableVoices();

      expect(result).toEqual([]);
    });

    it('uses default language parameter', async () => {
      fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ voices: [] })
      });

      await getAvailableVoices();

      expect(fetch).toHaveBeenCalledWith('http://localhost:5000/api/tts/voices?language=all');
    });
  });

  describe('streamTextToSpeech', () => {
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

    it('streams audio data successfully', async () => {
      const onChunk = jest.fn();
      const audioChunk1 = new Uint8Array([1, 2, 3]);
      const audioChunk2 = new Uint8Array([4, 5, 6]);

      mockReader.read
        .mockResolvedValueOnce({ done: false, value: audioChunk1 })
        .mockResolvedValueOnce({ done: false, value: audioChunk2 })
        .mockResolvedValueOnce({ done: true });

      fetch.mockResolvedValue(mockResponse);

      await streamTextToSpeech('Hello world', onChunk);

      expect(fetch).toHaveBeenCalledWith('http://localhost:5000/api/tts/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: 'Hello world',
          voice: 'neutral',
          language: 'en',
          speed: 1.0,
          format: 'mp3'
        })
      });

      expect(onChunk).toHaveBeenCalledTimes(2);
      expect(onChunk).toHaveBeenNthCalledWith(1, audioChunk1);
      expect(onChunk).toHaveBeenNthCalledWith(2, audioChunk2);
    });

    it('uses custom options for streaming', async () => {
      const onChunk = jest.fn();
      const options = { voice: 'female', language: 'hi', speed: 0.8 };

      mockReader.read.mockResolvedValueOnce({ done: true });
      fetch.mockResolvedValue(mockResponse);

      await streamTextToSpeech('Test text', onChunk, options);

      expect(fetch).toHaveBeenCalledWith('http://localhost:5000/api/tts/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: 'Test text',
          voice: 'female',
          language: 'hi',
          speed: 0.8,
          format: 'mp3'
        })
      });
    });

    it('handles streaming API errors', async () => {
      fetch.mockResolvedValue({
        ok: false,
        status: 500
      });

      await expect(
        streamTextToSpeech('Test text', jest.fn())
      ).rejects.toThrow('HTTP error! status: 500');
    });

    it('logs streaming errors', async () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
      
      fetch.mockRejectedValue(new Error('Stream error'));

      try {
        await streamTextToSpeech('Test text', jest.fn());
      } catch (error) {
        // Expected to throw
      }

      expect(consoleSpy).toHaveBeenCalledWith('Error streaming TTS:', expect.any(Error));
      
      consoleSpy.mockRestore();
    });
  });

  describe('spiritualTextToSpeech', () => {
    it('converts vedic text with appropriate settings', async () => {
      const mockResponse = { success: true, audioUrl: 'vedic.mp3' };

      fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      });

      await spiritualTextToSpeech('Om mani padme hum', 'vedic', 'sa');

      expect(fetch).toHaveBeenCalledWith('http://localhost:5000/api/tts/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: 'Om mani padme hum',
          voice: 'sage',
          language: 'sa',
          speed: 0.9,
          format: 'mp3'
        })
      });
    });

    it('uses different voice settings for different traditions', async () => {
      fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ success: true })
      });

      // Test buddhist tradition
      await spiritualTextToSpeech('Dharma text', 'buddhist', 'en');

      expect(fetch).toHaveBeenCalledWith('http://localhost:5000/api/tts/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: 'Dharma text',
          voice: 'calm',
          language: 'en',
          speed: 0.8,
          format: 'mp3'
        })
      });

      // Test sufi tradition
      await spiritualTextToSpeech('Sufi poetry', 'sufi', 'en');

      expect(fetch).toHaveBeenLastCalledWith('http://localhost:5000/api/tts/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: 'Sufi poetry',
          voice: 'melodic',
          language: 'en',
          speed: 1.0,
          format: 'mp3'
        })
      });
    });

    it('falls back to general settings for unknown tradition', async () => {
      fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ success: true })
      });

      await spiritualTextToSpeech('General text', 'unknown', 'en');

      expect(fetch).toHaveBeenCalledWith('http://localhost:5000/api/tts/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: 'General text',
          voice: 'neutral',
          language: 'en',
          speed: 1.0,
          format: 'mp3'
        })
      });
    });
  });

  describe('getTTSStatus', () => {
    it('fetches TTS status successfully', async () => {
      const mockStatus = {
        requestId: 'req_123',
        status: 'completed',
        progress: 100,
        audioUrl: 'http://example.com/audio.mp3'
      };

      fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockStatus)
      });

      const result = await getTTSStatus('req_123');

      expect(fetch).toHaveBeenCalledWith('http://localhost:5000/api/tts/status/req_123');
      expect(result).toEqual(mockStatus);
    });

    it('handles status check errors', async () => {
      fetch.mockResolvedValue({
        ok: false,
        status: 404
      });

      await expect(getTTSStatus('invalid_id')).rejects.toThrow('HTTP error! status: 404');
    });
  });

  describe('downloadAudio', () => {
    it('downloads audio file successfully', async () => {
      const mockBlob = new Blob(['audio data'], { type: 'audio/mpeg' });

      fetch.mockResolvedValue({
        ok: true,
        blob: () => Promise.resolve(mockBlob)
      });

      const result = await downloadAudio('audio_123');

      expect(fetch).toHaveBeenCalledWith('http://localhost:5000/api/tts/download/audio_123');
      expect(result).toBeInstanceOf(Blob);
    });

    it('handles download errors', async () => {
      fetch.mockResolvedValue({
        ok: false,
        status: 404
      });

      await expect(downloadAudio('invalid_id')).rejects.toThrow('HTTP error! status: 404');
    });

    it('logs download errors', async () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
      
      fetch.mockRejectedValue(new Error('Download failed'));

      try {
        await downloadAudio('audio_123');
      } catch (error) {
        // Expected to throw
      }

      expect(consoleSpy).toHaveBeenCalledWith('Error downloading audio:', expect.any(Error));
      
      consoleSpy.mockRestore();
    });
  });
});