require('@testing-library/jest-dom');

// Mock fetch globally
global.fetch = jest.fn();

// Add TextEncoder and TextDecoder polyfills for Node.js
const { TextEncoder, TextDecoder } = require('util');
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;

// Add Blob polyfill for Node.js
global.Blob = class Blob {
  constructor(parts, options = {}) {
    this.parts = parts || [];
    this.type = options.type || '';
  }
};

// Reset all mocks before each test
beforeEach(() => {
  jest.clearAllMocks();
  fetch.mockClear();
});

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {
    this.observe = jest.fn();
    this.disconnect = jest.fn();
    this.unobserve = jest.fn();
  }
};
