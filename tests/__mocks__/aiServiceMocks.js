/**
 * Comprehensive AI Services Mocking Utilities
 * 
 * This module provides mocking strategies for external AI services like ChatGPT, Claude,
 * and Text-to-Speech APIs to enable reliable testing without external dependencies.
 */

// ChatGPT API Mocks
export const mockChatGPTResponses = {
  spiritual: {
    question: 'What is dharma?',
    response: {
      success: true,
      response: 'Dharma is one of the most fundamental concepts in Hindu philosophy. It represents the righteous path of life, moral law, and duties that sustain the cosmic order. According to the scriptures, dharma is what upholds individual and societal well-being.',
      guru_type: 'spiritual',
      context_used: true,
      response_id: 'resp_dharma_001'
    }
  },
  meditation: {
    question: 'How to start meditation?',
    response: {
      success: true,
      response: 'To begin meditation, find a quiet space and sit comfortably with your spine straight. Start with just 5-10 minutes daily. Focus on your breath - observe the natural rhythm of inhaling and exhaling. When your mind wanders, gently bring attention back to the breath.',
      guru_type: 'meditation',
      context_used: true,
      response_id: 'resp_meditation_001'
    }
  },
  karma: {
    question: 'What is karma yoga?',
    response: {
      success: true,
      response: 'Karma Yoga is the path of selfless action as described in the Bhagavad Gita. It involves performing your duties without attachment to the results. By offering all actions to the Divine and working for the welfare of others, one purifies the mind and progresses spiritually.',
      guru_type: 'karma',
      context_used: true,
      response_id: 'resp_karma_001'
    }
  }
};

export const mockChatGPTStreamChunks = [
  { text: 'Thank you for your question.' },
  { text: ' The concept you\'re asking about' },
  { text: ' is quite profound and has been' },
  { text: ' discussed extensively in spiritual literature.' },
  { text: ' Let me explain it step by step...' }
];

// Claude API Mocks
export const mockClaudeResponses = {
  spiritual_content: {
    input: 'Generate explanation about compassion',
    response: {
      success: true,
      content: 'Compassion (Karuna) is one of the highest virtues in spiritual traditions. It is the spontaneous expression of love that arises when we recognize the suffering of others as our own. True compassion is not mere sympathy, but an active force that motivates us to alleviate suffering wherever we encounter it.',
      model: 'claude-3-sonnet',
      usage: { tokens: 145 }
    }
  },
  verse_generation: {
    input: 'Generate verse about inner peace',
    response: {
      success: true,
      content: 'शान्तिः शान्तिः शान्तिः - Peace, Peace, Peace\n\nIn the depths of silence, wisdom speaks,\nWhere thoughts dissolve and ego sleeps.\nThe heart finds rest in its true home,\nNo longer does the spirit roam.\n\nTranslation: True peace is found not in external circumstances, but in the profound silence that exists within consciousness itself.',
      model: 'claude-3-sonnet',
      usage: { tokens: 180 }
    }
  }
};

// Text-to-Speech API Mocks
export const mockTTSResponses = {
  basic_generation: {
    input: 'Om mani padme hum',
    response: {
      success: true,
      audioUrl: 'https://mock-audio-service.com/audio/sanskrit_mantra_001.mp3',
      duration: 8.5,
      audioId: 'audio_sanskrit_001',
      voice: 'sage',
      language: 'sa'
    }
  },
  spiritual_narration: {
    input: 'The path of yoga leads to union with the divine consciousness',
    response: {
      success: true,
      audioUrl: 'https://mock-audio-service.com/audio/spiritual_001.mp3',
      duration: 12.3,
      audioId: 'audio_spiritual_001',
      voice: 'calm',
      language: 'en'
    }
  }
};

export const mockVoices = [
  { id: 'en-sage', name: 'English Sage', language: 'en', gender: 'male', style: 'wise' },
  { id: 'en-calm', name: 'English Calm', language: 'en', gender: 'female', style: 'peaceful' },
  { id: 'hi-traditional', name: 'Hindi Traditional', language: 'hi', gender: 'male', style: 'classical' },
  { id: 'sa-vedic', name: 'Sanskrit Vedic', language: 'sa', gender: 'neutral', style: 'chanting' }
];

// Mock fetch utility for consistent testing
export function createMockFetch(mockResponses = {}) {
  return jest.fn((url, options) => {
    const method = options?.method || 'GET';
    const body = options?.body ? JSON.parse(options.body) : null;
    
    // ChatGPT API endpoints
    if (url.includes('/api/spiritual/guidance')) {
      const guruType = body?.guru_type || 'spiritual';
      const mockResponse = mockResponses.chatgpt || mockChatGPTResponses[guruType] || mockChatGPTResponses.spiritual;
      
      return Promise.resolve({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse.response)
      });
    }
    
    // Claude API endpoints
    if (url.includes('/api/claude/chat')) {
      const mockResponse = mockResponses.claude || mockClaudeResponses.spiritual_content;
      
      return Promise.resolve({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse.response)
      });
    }
    
    // TTS API endpoints
    if (url.includes('/api/tts/generate')) {
      const mockResponse = mockResponses.tts || mockTTSResponses.basic_generation;
      
      return Promise.resolve({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse.response)
      });
    }
    
    if (url.includes('/api/tts/voices')) {
      return Promise.resolve({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ voices: mockVoices })
      });
    }
    
    // Default response for unmatched URLs
    return Promise.resolve({
      ok: true,
      status: 200,
      json: () => Promise.resolve({ success: true, message: 'Mock response' })
    });
  });
}

// Streaming mock utilities
export function createMockStreamReader(chunks) {
  let index = 0;
  
  return {
    read: jest.fn(() => {
      if (index < chunks.length) {
        const chunk = chunks[index++];
        const encoded = new TextEncoder().encode(`data: ${JSON.stringify(chunk)}\n`);
        return Promise.resolve({ done: false, value: encoded });
      } else if (index === chunks.length) {
        index++;
        const encoded = new TextEncoder().encode('data: [DONE]\n');
        return Promise.resolve({ done: false, value: encoded });
      } else {
        return Promise.resolve({ done: true });
      }
    })
  };
}

// Error simulation utilities
export const errorScenarios = {
  networkError: () => Promise.reject(new Error('Network connection failed')),
  serverError: () => Promise.resolve({
    ok: false,
    status: 500,
    json: () => Promise.resolve({ error: 'Internal server error' })
  }),
  timeoutError: () => new Promise((_, reject) => {
    setTimeout(() => reject(new Error('Request timeout')), 1000);
  }),
  rateLimitError: () => Promise.resolve({
    ok: false,
    status: 429,
    json: () => Promise.resolve({ error: 'Rate limit exceeded' })
  }),
  unauthorizedError: () => Promise.resolve({
    ok: false,
    status: 401,
    json: () => Promise.resolve({ error: 'Unauthorized access' })
  })
};

// Test data generators
export function generateMockUser(overrides = {}) {
  return {
    id: 'user_123',
    username: 'testuser',
    email: 'test@example.com',
    preferences: {
      language: 'en',
      guru_type: 'spiritual',
      voice_preference: 'calm',
      session_reminders: true
    },
    stats: {
      total_sessions: 45,
      total_duration: 2700, // 45 minutes
      favorite_guru: 'meditation',
      streak_days: 7
    },
    created_at: '2024-01-01T00:00:00Z',
    last_active: '2024-01-15T10:30:00Z',
    ...overrides
  };
}

export function generateMockSession(overrides = {}) {
  return {
    id: 'session_456',
    user_id: 'user_123',
    guru_type: 'meditation',
    session_type: 'guided_meditation',
    duration: 600, // 10 minutes
    status: 'completed',
    rating: 5,
    notes: 'Very peaceful session',
    started_at: '2024-01-15T10:00:00Z',
    completed_at: '2024-01-15T10:10:00Z',
    ...overrides
  };
}

export function generateMockVerse(overrides = {}) {
  return {
    id: 'verse_789',
    text: 'योगस्थः कुरु कर्माणि सङ्गं त्यक्त्वा धनञ्जय',
    translation: 'Established in yoga, perform actions, abandoning attachment, O Arjuna',
    source: 'bhagavad-gita',
    chapter: 2,
    verse: 48,
    meaning: 'This verse teaches the principle of performing duties while maintaining inner equilibrium',
    audio_url: 'https://mock-audio.com/verse_789.mp3',
    tags: ['karma-yoga', 'detachment', 'duty'],
    difficulty_level: 'intermediate',
    ...overrides
  };
}

// Performance testing utilities
export function measureResponseTime(fn) {
  return async (...args) => {
    const start = performance.now();
    const result = await fn(...args);
    const end = performance.now();
    return {
      result,
      responseTime: end - start
    };
  };
}

// Mock localStorage for user preferences
export function mockLocalStorage() {
  const store = {};
  
  return {
    getItem: jest.fn((key) => store[key] || null),
    setItem: jest.fn((key, value) => {
      store[key] = value.toString();
    }),
    removeItem: jest.fn((key) => {
      delete store[key];
    }),
    clear: jest.fn(() => {
      for (const key in store) {
        delete store[key];
      }
    })
  };
}

// WebSocket mocking for real-time features
export function createMockWebSocket() {
  const listeners = {};
  
  return {
    addEventListener: jest.fn((event, handler) => {
      if (!listeners[event]) listeners[event] = [];
      listeners[event].push(handler);
    }),
    removeEventListener: jest.fn((event, handler) => {
      if (listeners[event]) {
        listeners[event] = listeners[event].filter(l => l !== handler);
      }
    }),
    send: jest.fn(),
    close: jest.fn(),
    readyState: 1, // OPEN
    
    // Utility to trigger events in tests
    triggerEvent: (event, data) => {
      if (listeners[event]) {
        listeners[event].forEach(handler => handler(data));
      }
    }
  };
}

// Advanced mocking patterns
export class AIServiceMocker {
  constructor() {
    this.responses = new Map();
    this.delays = new Map();
    this.errorRates = new Map();
  }
  
  // Set up specific responses for different inputs
  setResponse(service, input, response) {
    if (!this.responses.has(service)) {
      this.responses.set(service, new Map());
    }
    this.responses.get(service).set(input, response);
  }
  
  // Add realistic delays to API responses
  setDelay(service, delay) {
    this.delays.set(service, delay);
  }
  
  // Simulate intermittent failures
  setErrorRate(service, rate) {
    this.errorRates.set(service, rate);
  }
  
  // Create mock function with configured behavior
  createMockFunction(service) {
    return async (input, ...args) => {
      // Simulate delay
      const delay = this.delays.get(service) || 0;
      if (delay > 0) {
        await new Promise(resolve => setTimeout(resolve, delay));
      }
      
      // Simulate errors
      const errorRate = this.errorRates.get(service) || 0;
      if (Math.random() < errorRate) {
        throw new Error(`Simulated ${service} error`);
      }
      
      // Return configured response
      const serviceResponses = this.responses.get(service);
      if (serviceResponses && serviceResponses.has(input)) {
        return serviceResponses.get(input);
      }
      
      // Default response
      return { success: true, message: `Mock ${service} response for: ${input}` };
    };
  }
}