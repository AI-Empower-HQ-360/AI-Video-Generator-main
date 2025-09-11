// Performance-optimized lazy loading for SlokaGuru
const loadSlokaGuru = async () => {
    const { default: SlokaGuru } = await import('./gurus/SlokaGuru.js');
    return SlokaGuru;
};

// Performance-optimized lazy loading for prompt builder
const loadPromptBuilder = async () => {
    const { buildSlokaPrompt } = await import('./gurus/promptBuilder.js');
    return buildSlokaPrompt;
};

console.log("📚 Welcome to AI Sloka Guru");

// Initialize components lazily to improve startup performance
document.addEventListener('DOMContentLoaded', async () => {
    try {
        // Only load when DOM is ready
        const buildSlokaPrompt = await loadPromptBuilder();
        console.log(buildSlokaPrompt(0)); // Show first sloka as example
    } catch (error) {
        console.warn('Could not load prompt builder:', error);
    }
});

// Export for dynamic imports in other modules
export { loadSlokaGuru, loadPromptBuilder };
