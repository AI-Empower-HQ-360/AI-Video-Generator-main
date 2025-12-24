const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

/**
 * Chat with Claude AI through the backend API
 * @param {string} input - User's message
 * @param {string} model - Claude model version (claude-3-sonnet, claude-3-haiku, etc.)
 * @param {Object} options - Optional configuration
 * @param {number} options.maxTokens - Maximum tokens in response
 * @param {number} options.temperature - Response creativity (0-1)
 * @param {Array} options.systemPrompts - System prompts for context
 * @returns {Promise} Response from Claude
 */
export async function chatWithClaude(
  input, 
  model = 'claude-3-sonnet', 
  options = {}
) {
  const {
    maxTokens = 1000,
    temperature = 0.7,
    systemPrompts = []
  } = options;

  try {
    const response = await fetch(`${API_BASE_URL}/api/claude/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: input,
        model,
        max_tokens: maxTokens,
        temperature,
        system_prompts: systemPrompts
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error communicating with Claude:', error);
    throw error;
  }
}

/**
 * Get available Claude models
 * @returns {Array} List of available Claude models
 */
export function getAvailableClaudeModels() {
  return [
    'claude-3-opus',
    'claude-3-sonnet', 
    'claude-3-haiku',
    'claude-2.1',
    'claude-2.0'
  ];
}

/**
 * Stream chat with Claude AI
 * @param {string} input - User's message
 * @param {Function} onChunk - Callback for each chunk of data
 * @param {string} model - Claude model version
 * @param {Object} options - Optional configuration
 */
export async function streamChatWithClaude(input, onChunk, model = 'claude-3-sonnet', options = {}) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/claude/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: input,
        model,
        ...options
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data === '[DONE]') {
            return;
          }
          try {
            const parsed = JSON.parse(data);
            onChunk(parsed);
          } catch (e) {
            console.warn('Malformed JSON in Claude stream:', data);
          }
        }
      }
    }
  } catch (error) {
    console.error('Error streaming with Claude:', error);
    throw error;
  }
}

/**
 * Generate spiritual content using Claude
 * @param {string} topic - Topic for content generation
 * @param {string} type - Type of content (verse, story, explanation)
 * @param {string} language - Target language
 * @returns {Promise} Generated content
 */
export async function generateSpiritualContent(topic, type = 'explanation', language = 'en') {
  try {
    const systemPrompts = [
      'You are a wise spiritual teacher with deep knowledge of various traditions.',
      'Provide authentic, respectful, and insightful spiritual guidance.',
      'Draw from various traditions while being inclusive and non-dogmatic.'
    ];

    const article = ['a', 'e', 'i', 'o', 'u'].includes(type[0].toLowerCase()) ? 'an' : 'a';
    const prompt = `Generate ${article} ${type} about ${topic} in ${language} language. 
                   Make it authentic, inspirational, and accessible to modern readers.`;

    return await chatWithClaude(prompt, 'claude-3-sonnet', {
      systemPrompts,
      temperature: 0.8,
      maxTokens: 1500
    });
  } catch (error) {
    console.error('Error generating spiritual content with Claude:', error);
    throw error;
  }
}
