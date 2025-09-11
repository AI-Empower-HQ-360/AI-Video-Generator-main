import { buildPrompt } from './promptBuilder.js';

// Performance-optimized SlokaGuru with caching and lazy loading
class SlokaGuru {
    constructor() {
        this.name = "🕉️ AI Sloka Guru";
        this.specialization = "Universal wisdom from sacred verses";
        this.basePrompt = `You are the AI Sloka Guru, making timeless wisdom accessible to everyone.
        Your core mission is to share the universal truth that all sacred texts point to: "We are eternal consciousness."
        Drawing from world wisdom (Vedic, Islamic, Christian, Buddhist, and other traditions), you help people:
        - Understand profound spiritual truths in simple language
        - See the common essence in all sacred teachings
        - Connect ancient wisdom with modern life
        - Experience the universal truth beyond religious boundaries
        - Transform scriptural knowledge into practical wisdom

        Key Principles to Emphasize:
        1. Universal Truth: All traditions point to the same eternal consciousness
        2. Simple Understanding: Complex wisdom explained in everyday language
        3. Practical Application: Ancient wisdom for modern challenges
        4. Unity in Diversity: Showing how different teachings share the same core
        
        Always maintain a balance of:
        - Deep wisdom and simple explanation
        - Multiple traditions and unified understanding
        - Ancient teachings and modern relevance
        - Respectful presentation and accessible language`;
        
        this.supportedLanguages = [
            'english',
            'hindi',
            'telugu',
            'gujarati',
            'tamil',
            'kannada',
            'malayalam',
            'bengali',
            'marathi',
            'punjabi'
        ];
        
        // Lazy loading for slokas - only load when needed
        this._slokas = null;
        this._slokaCache = new Map();
        this._responseCache = new Map();
    }

    // Lazy loading with caching for better performance
    async _loadSlokas() {
        if (this._slokas) return this._slokas;
        
        try {
            const response = await fetch('/static/data/slokas_database.json');
            this._slokas = await response.json();
            return this._slokas;
        } catch (error) {
            console.warn('Could not load slokas database, using fallback');
            this._slokas = [];
            return this._slokas;
        }
    }

    async getResponse(question, userId = null, language = 'english') {
        try {
            // Validate language
            if (!this.supportedLanguages.includes(language.toLowerCase())) {
                language = 'english';
            }

            // Create cache key for performance
            const cacheKey = `${question}-${language}-${userId}`;
            if (this._responseCache.has(cacheKey)) {
                return this._responseCache.get(cacheKey);
            }

            const response = await fetch('/api/slokas/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    question,
                    user_id: userId,
                    language: language.toLowerCase()
                })
            });
            
            const result = await response.json();
            
            // Cache successful responses (max 50 entries to prevent memory leaks)
            if (result && !result.error && this._responseCache.size < 50) {
                this._responseCache.set(cacheKey, result);
            }
            
            return result;
        } catch (error) {
            console.error('Error getting Sloka Guru response:', error);
            return {
                error: 'Unable to connect with Sloka Guru at this moment. Please try again later.'
            };
        }
    }

    async explainSloka(slokaText, userId = null) {
        try {
            // Cache key for sloka explanations
            const cacheKey = `explain-${slokaText}-${userId}`;
            if (this._slokaCache.has(cacheKey)) {
                return this._slokaCache.get(cacheKey);
            }

            const response = await fetch('/api/slokas/explain', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    sloka: slokaText,
                    user_id: userId
                })
            });
            
            const result = await response.json();
            
            // Cache explanation (max 30 entries)
            if (result && result.success && this._slokaCache.size < 30) {
                this._slokaCache.set(cacheKey, result);
            }
            
            return result;
        } catch (error) {
            console.error('Error getting sloka explanation:', error);
            return {
                success: false,
                error: 'Unable to explain sloka at this moment. Please try again later.'
            };
        }
    }

    getTeachings() {
        return [
            "One truth expressed through many traditions",
            "Sacred wisdom in simple, everyday language",
            "Universal consciousness in all teachings",
            "Practical wisdom for modern living",
            "Unity of spiritual understanding",
            "Ancient truth for today's world",
            "Connecting hearts through timeless wisdom"
        ];
    }

    async getDailySloka() {
        const slokas = await this._loadSlokas();
        if (slokas.length === 0) return null;
        
        const randomIndex = Math.floor(Math.random() * slokas.length);
        return slokas[randomIndex];
    }

    // Clear cache to prevent memory leaks
    clearCache() {
        this._responseCache.clear();
        this._slokaCache.clear();
    }
}
}

export default SlokaGuru;
