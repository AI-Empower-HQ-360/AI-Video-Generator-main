const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

/**
 * Convert text to speech using AI service
 * @param {string} text - Text to convert to speech
 * @param {Object} options - TTS configuration options
 * @param {string} options.voice - Voice type (male, female, neutral)
 * @param {string} options.language - Language code (en, hi, sa)
 * @param {number} options.speed - Speech speed (0.5-2.0)
 * @param {string} options.format - Audio format (mp3, wav, ogg)
 * @returns {Promise} Audio data or URL
 */
export async function textToSpeech(text, options = {}) {
  const {
    voice = 'neutral',
    language = 'en',
    speed = 1.0,
    format = 'mp3'
  } = options;

  try {
    const response = await fetch(`${API_BASE_URL}/api/tts/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text,
        voice,
        language,
        speed,
        format
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error generating speech:', error);
    throw error;
  }
}

/**
 * Get available TTS voices
 * @param {string} language - Language code to filter voices
 * @returns {Promise} List of available voices
 */
export async function getAvailableVoices(language = 'all') {
  try {
    const response = await fetch(`${API_BASE_URL}/api/tts/voices?language=${language}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data.voices || [];
  } catch (error) {
    console.error('Error fetching available voices:', error);
    // Return fallback voices
    return [
      { id: 'en-male', name: 'English Male', language: 'en', gender: 'male' },
      { id: 'en-female', name: 'English Female', language: 'en', gender: 'female' },
      { id: 'hi-male', name: 'Hindi Male', language: 'hi', gender: 'male' },
      { id: 'hi-female', name: 'Hindi Female', language: 'hi', gender: 'female' }
    ];
  }
}

/**
 * Stream TTS audio generation
 * @param {string} text - Text to convert
 * @param {Function} onChunk - Callback for audio chunks
 * @param {Object} options - TTS options
 */
export async function streamTextToSpeech(text, onChunk, options = {}) {
  const {
    voice = 'neutral',
    language = 'en',
    speed = 1.0,
    format = 'mp3'
  } = options;

  try {
    const response = await fetch(`${API_BASE_URL}/api/tts/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text,
        voice,
        language,
        speed,
        format
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body.getReader();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      onChunk(value);
    }
  } catch (error) {
    console.error('Error streaming TTS:', error);
    throw error;
  }
}

/**
 * Convert spiritual text to speech with appropriate voice
 * @param {string} text - Spiritual text to convert
 * @param {string} tradition - Spiritual tradition (vedic, buddhist, etc.)
 * @param {string} language - Target language
 * @returns {Promise} Audio data
 */
export async function spiritualTextToSpeech(text, tradition = 'vedic', language = 'en') {
  const voiceMapping = {
    vedic: { voice: 'sage', speed: 0.9 },
    buddhist: { voice: 'calm', speed: 0.8 },
    sufi: { voice: 'melodic', speed: 1.0 },
    general: { voice: 'neutral', speed: 1.0 }
  };

  const config = voiceMapping[tradition] || voiceMapping.general;
  
  return await textToSpeech(text, {
    ...config,
    language,
    format: 'mp3'
  });
}

/**
 * Get TTS status for a generation request
 * @param {string} requestId - Generation request ID
 * @returns {Promise} Status information
 */
export async function getTTSStatus(requestId) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/tts/status/${requestId}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error checking TTS status:', error);
    throw error;
  }
}

/**
 * Download generated audio file
 * @param {string} audioId - Audio file ID
 * @returns {Promise<Blob>} Audio file blob
 */
export async function downloadAudio(audioId) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/tts/download/${audioId}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.blob();
  } catch (error) {
    console.error('Error downloading audio:', error);
    throw error;
  }
}
