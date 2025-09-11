/**
 * AI Empower Heart - Main Frontend JavaScript Application
 * 
 * This module provides the core frontend functionality for the AI-powered
 * spiritual guidance platform. It handles user interactions, API communication,
 * and dynamic content updates.
 * 
 * Key Features:
 * - Smooth scrolling navigation
 * - Dynamic content loading
 * - User experience enhancements
 * - API integration utilities
 * 
 * Dependencies:
 * - Modern browser with ES6+ support
 * - DOM API for element manipulation
 * - Fetch API for backend communication
 * 
 * @author AI-Empower-HQ-360
 * @version 1.0.0
 * @license MIT
 */

/**
 * Application Configuration
 * Global configuration object for the frontend application
 */
const AppConfig = {
    // API endpoints configuration
    api: {
        baseUrl: window.location.hostname === 'localhost' 
            ? 'http://localhost:5000'  // Development environment
            : '/api',                  // Production environment (proxied)
        endpoints: {
            health: '/health',
            gurus: '/api/gurus',
            ask: '/api/gurus/ask',
            askStream: '/api/gurus/ask/stream'
        }
    },
    
    // UI configuration
    ui: {
        smoothScrollDuration: 800,
        fadeInDuration: 500,
        loadingTimeout: 10000  // 10 seconds timeout for API requests
    },
    
    // Feature flags
    features: {
        enableStreamingResponses: true,
        enableOfflineMode: false,
        enableAnalytics: true
    }
};

/**
 * Main Application Class
 * Handles initialization and coordination of application modules
 */
class AIEmpowerHeartApp {
    constructor() {
        this.isInitialized = false;
        this.currentGuru = null;
        this.conversationHistory = [];
        
        // Bind methods to maintain context
        this.handleGuruSelection = this.handleGuruSelection.bind(this);
        this.handleQuestionSubmit = this.handleQuestionSubmit.bind(this);
        this.handleApiError = this.handleApiError.bind(this);
    }
    
    /**
     * Initialize the application
     * Sets up event listeners, loads initial data, and prepares the UI
     */
    async init() {
        try {
            console.log('Initializing AI Empower Heart application...');
            
            // Setup core functionality
            this.setupSmoothScrolling();
            this.setupUIEnhancements();
            
            // Load initial data
            await this.loadGuruInformation();
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Mark as initialized
            this.isInitialized = true;
            
            console.log('AI Empower Heart application initialized successfully');
            
            // Trigger custom event for other modules
            this.dispatchEvent('app:initialized');
            
        } catch (error) {
            console.error('Failed to initialize application:', error);
            this.showErrorMessage('Application failed to load. Please refresh the page.');
        }
    }
    
    /**
     * Setup smooth scrolling for anchor links
     * Enhances user experience with smooth page navigation
     */
    setupSmoothScrolling() {
        // Find all anchor links that start with # (internal page links)
        const anchorLinks = document.querySelectorAll('a[href^="#"]');
        
        anchorLinks.forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault(); // Prevent default jump behavior
                
                // Get the target element from the href attribute
                const targetId = anchor.getAttribute('href');
                const targetElement = document.querySelector(targetId);
                
                if (targetElement) {
                    // Smooth scroll to the target element
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'  // Scroll to top of element
                    });
                    
                    // Update URL without jumping (for browser history)
                    history.pushState(null, null, targetId);
                    
                    // Log navigation for analytics
                    this.trackEvent('navigation', {
                        action: 'smooth_scroll',
                        target: targetId
                    });
                } else {
                    console.warn(`Target element not found for anchor: ${targetId}`);
                }
            });
        });
    }
    
    /**
     * Setup general UI enhancements
     * Adds progressive enhancement features for better user experience
     */
    setupUIEnhancements() {
        // Add loading states for buttons
        this.setupLoadingStates();
        
        // Setup form validation
        this.setupFormValidation();
        
        // Add keyboard shortcuts
        this.setupKeyboardShortcuts();
        
        // Setup responsive image loading
        this.setupLazyLoading();
    }
    
    /**
     * Setup loading states for interactive elements
     * Provides visual feedback during async operations
     */
    setupLoadingStates() {
        const buttons = document.querySelectorAll('button[data-loading]');
        
        buttons.forEach(button => {
            // Store original text for restoration
            const originalText = button.textContent;
            
            // Add loading state methods
            button.showLoading = () => {
                button.disabled = true;
                button.classList.add('loading');
                button.innerHTML = '<span class="spinner"></span> Loading...';
            };
            
            button.hideLoading = () => {
                button.disabled = false;
                button.classList.remove('loading');
                button.textContent = originalText;
            };
        });
    }
    
    /**
     * Setup form validation
     * Provides real-time validation feedback for user inputs
     */
    setupFormValidation() {
        const forms = document.querySelectorAll('form[data-validate]');
        
        forms.forEach(form => {
            const inputs = form.querySelectorAll('input, textarea, select');
            
            inputs.forEach(input => {
                // Real-time validation on input change
                input.addEventListener('input', () => {
                    this.validateField(input);
                });
                
                // Validation on blur (when user leaves field)
                input.addEventListener('blur', () => {
                    this.validateField(input);
                });
            });
            
            // Form submission validation
            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    e.preventDefault(); // Prevent submission if invalid
                }
            });
        });
    }
    
    /**
     * Validate individual form field
     * @param {HTMLElement} field - The form field to validate
     * @returns {boolean} - Whether the field is valid
     */
    validateField(field) {
        const value = field.value.trim();
        const fieldName = field.name || field.id;
        let isValid = true;
        let errorMessage = '';
        
        // Required field validation
        if (field.hasAttribute('required') && !value) {
            isValid = false;
            errorMessage = `${fieldName} is required`;
        }
        
        // Email validation
        if (field.type === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                isValid = false;
                errorMessage = 'Please enter a valid email address';
            }
        }
        
        // Question length validation (for spiritual guidance)
        if (field.name === 'question' && value.length > 1000) {
            isValid = false;
            errorMessage = 'Question must be less than 1000 characters';
        }
        
        // Update field visual state
        this.updateFieldValidation(field, isValid, errorMessage);
        
        return isValid;
    }
    
    /**
     * Update field validation visual state
     * @param {HTMLElement} field - The form field
     * @param {boolean} isValid - Whether the field is valid
     * @param {string} errorMessage - Error message to display
     */
    updateFieldValidation(field, isValid, errorMessage) {
        // Remove existing validation classes
        field.classList.remove('valid', 'invalid');
        
        // Add appropriate validation class
        field.classList.add(isValid ? 'valid' : 'invalid');
        
        // Find or create error message element
        let errorElement = field.parentNode.querySelector('.error-message');
        
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'error-message';
            field.parentNode.appendChild(errorElement);
        }
        
        // Update error message
        errorElement.textContent = isValid ? '' : errorMessage;
        errorElement.style.display = isValid ? 'none' : 'block';
    }
    
    /**
     * Validate entire form
     * @param {HTMLElement} form - The form to validate
     * @returns {boolean} - Whether the form is valid
     */
    validateForm(form) {
        const fields = form.querySelectorAll('input, textarea, select');
        let isFormValid = true;
        
        fields.forEach(field => {
            if (!this.validateField(field)) {
                isFormValid = false;
            }
        });
        
        return isFormValid;
    }
    
    /**
     * Setup keyboard shortcuts for enhanced accessibility
     */
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Escape key to close modals or cancel operations
            if (e.key === 'Escape') {
                this.handleEscapeKey();
            }
            
            // Ctrl/Cmd + Enter to submit forms
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                this.handleQuickSubmit();
            }
            
            // Accessibility: Skip to main content (Alt + S)
            if (e.altKey && e.key === 's') {
                const mainContent = document.querySelector('main');
                if (mainContent) {
                    mainContent.focus();
                    mainContent.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });
    }
    
    /**
     * Handle escape key press
     */
    handleEscapeKey() {
        // Close any open modals
        const modals = document.querySelectorAll('.modal.active');
        modals.forEach(modal => {
            this.closeModal(modal);
        });
        
        // Cancel any ongoing streaming responses
        if (this.currentStreamController) {
            this.currentStreamController.abort();
        }
    }
    
    /**
     * Handle quick submit (Ctrl/Cmd + Enter)
     */
    handleQuickSubmit() {
        const activeForm = document.querySelector('form:focus-within');
        if (activeForm) {
            const submitButton = activeForm.querySelector('button[type="submit"]');
            if (submitButton && !submitButton.disabled) {
                submitButton.click();
            }
        }
    }
    
    /**
     * Setup lazy loading for images
     * Improves page load performance by loading images only when needed
     */
    setupLazyLoading() {
        // Use Intersection Observer for efficient lazy loading
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        
                        // Load the actual image
                        if (img.dataset.src) {
                            img.src = img.dataset.src;
                            img.removeAttribute('data-src');
                        }
                        
                        // Remove loading placeholder
                        img.classList.remove('lazy-loading');
                        img.classList.add('lazy-loaded');
                        
                        // Stop observing this image
                        observer.unobserve(img);
                    }
                });
            });
            
            // Observe all images with data-src attribute
            const lazyImages = document.querySelectorAll('img[data-src]');
            lazyImages.forEach(img => {
                img.classList.add('lazy-loading');
                imageObserver.observe(img);
            });
        }
    }
    
    /**
     * Load guru information from the API
     * Fetches available gurus and their specializations
     */
    async loadGuruInformation() {
        try {
            console.log('Loading guru information...');
            
            const response = await fetch(`${AppConfig.api.baseUrl}${AppConfig.api.endpoints.gurus}`);
            
            if (!response.ok) {
                throw new Error(`Failed to load gurus: ${response.status} ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.gurus = data.gurus;
                this.populateGuruSelection();
                console.log(`Loaded ${Object.keys(this.gurus).length} gurus`);
            } else {
                throw new Error('Invalid response format from gurus API');
            }
            
        } catch (error) {
            console.error('Failed to load guru information:', error);
            this.handleApiError(error, 'Failed to load spiritual gurus');
        }
    }
    
    /**
     * Populate guru selection UI elements
     * Creates interactive elements for guru selection
     */
    populateGuruSelection() {
        const guruContainer = document.getElementById('guru-selection');
        
        if (!guruContainer || !this.gurus) {
            return;
        }
        
        // Clear existing content
        guruContainer.innerHTML = '';
        
        // Create guru selection elements
        Object.entries(this.gurus).forEach(([guruType, guruInfo]) => {
            const guruCard = this.createGuruCard(guruType, guruInfo);
            guruContainer.appendChild(guruCard);
        });
    }
    
    /**
     * Create guru selection card element
     * @param {string} guruType - The type/ID of the guru
     * @param {Object} guruInfo - Information about the guru
     * @returns {HTMLElement} - The created guru card element
     */
    createGuruCard(guruType, guruInfo) {
        const card = document.createElement('div');
        card.className = 'guru-card';
        card.dataset.guruType = guruType;
        
        card.innerHTML = `
            <div class="guru-icon">${guruInfo.name.charAt(0)}</div>
            <h3 class="guru-name">${guruInfo.name}</h3>
            <p class="guru-specialization">${guruInfo.specialization}</p>
            <button class="guru-select-btn" data-guru="${guruType}">
                Select ${guruInfo.name}
            </button>
        `;
        
        // Add click handler for guru selection
        const selectButton = card.querySelector('.guru-select-btn');
        selectButton.addEventListener('click', () => {
            this.handleGuruSelection(guruType, guruInfo);
        });
        
        // Add hover effects
        card.addEventListener('mouseenter', () => {
            this.trackEvent('guru_card_hover', { guru: guruType });
        });
        
        return card;
    }
    
    /**
     * Handle guru selection
     * @param {string} guruType - The selected guru type
     * @param {Object} guruInfo - Information about the selected guru
     */
    handleGuruSelection(guruType, guruInfo) {
        console.log(`Selected guru: ${guruType}`);
        
        // Update current guru
        this.currentGuru = { type: guruType, info: guruInfo };
        
        // Update UI to reflect selection
        this.updateGuruSelectionUI(guruType);
        
        // Show question interface
        this.showQuestionInterface();
        
        // Track selection for analytics
        this.trackEvent('guru_selected', { 
            guru: guruType, 
            name: guruInfo.name 
        });
    }
    
    /**
     * Update UI to reflect guru selection
     * @param {string} selectedGuruType - The type of the selected guru
     */
    updateGuruSelectionUI(selectedGuruType) {
        // Remove previous selections
        document.querySelectorAll('.guru-card.selected').forEach(card => {
            card.classList.remove('selected');
        });
        
        // Add selected state to chosen guru
        const selectedCard = document.querySelector(`[data-guru-type="${selectedGuruType}"]`);
        if (selectedCard) {
            selectedCard.classList.add('selected');
        }
        
        // Update selected guru display
        const selectedGuruDisplay = document.getElementById('selected-guru-display');
        if (selectedGuruDisplay && this.currentGuru) {
            selectedGuruDisplay.innerHTML = `
                <div class="selected-guru-info">
                    <span class="guru-icon">${this.currentGuru.info.name}</span>
                    <div class="guru-details">
                        <h4>${this.currentGuru.info.name}</h4>
                        <p>${this.currentGuru.info.specialization}</p>
                    </div>
                </div>
            `;
            selectedGuruDisplay.style.display = 'block';
        }
    }
    
    /**
     * Show question interface for user input
     */
    showQuestionInterface() {
        const questionInterface = document.getElementById('question-interface');
        
        if (questionInterface) {
            // Fade in the question interface
            questionInterface.style.opacity = '0';
            questionInterface.style.display = 'block';
            
            // Animate fade in
            setTimeout(() => {
                questionInterface.style.transition = `opacity ${AppConfig.ui.fadeInDuration}ms ease`;
                questionInterface.style.opacity = '1';
            }, 10);
            
            // Focus on the question input
            const questionInput = questionInterface.querySelector('#question-input');
            if (questionInput) {
                setTimeout(() => {
                    questionInput.focus();
                }, AppConfig.ui.fadeInDuration);
            }
            
            // Scroll to question interface
            questionInterface.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'start' 
            });
        }
    }
    
    /**
     * Setup event listeners for the application
     */
    setupEventListeners() {
        // Question form submission
        const questionForm = document.getElementById('question-form');
        if (questionForm) {
            questionForm.addEventListener('submit', this.handleQuestionSubmit);
        }
        
        // Streaming toggle
        const streamingToggle = document.getElementById('streaming-toggle');
        if (streamingToggle) {
            streamingToggle.addEventListener('change', (e) => {
                this.isStreamingEnabled = e.target.checked;
                this.trackEvent('streaming_toggle', { enabled: this.isStreamingEnabled });
            });
        }
        
        // Clear conversation button
        const clearButton = document.getElementById('clear-conversation');
        if (clearButton) {
            clearButton.addEventListener('click', () => {
                this.clearConversation();
            });
        }
        
        // Window resize handler for responsive adjustments
        window.addEventListener('resize', this.handleWindowResize.bind(this));
        
        // Online/offline status
        window.addEventListener('online', () => {
            this.showNotification('Connection restored', 'success');
        });
        
        window.addEventListener('offline', () => {
            this.showNotification('Connection lost. Some features may be unavailable.', 'warning');
        });
    }
    
    /**
     * Handle question form submission
     * @param {Event} event - The form submission event
     */
    async handleQuestionSubmit(event) {
        event.preventDefault();
        
        if (!this.currentGuru) {
            this.showErrorMessage('Please select a spiritual guru first.');
            return;
        }
        
        const formData = new FormData(event.target);
        const question = formData.get('question')?.trim();
        
        if (!question) {
            this.showErrorMessage('Please enter your question.');
            return;
        }
        
        // Validate question length
        if (question.length > 1000) {
            this.showErrorMessage('Please keep your question under 1000 characters.');
            return;
        }
        
        try {
            // Update UI to show loading state
            this.showLoadingState();
            
            // Track question submission
            this.trackEvent('question_submitted', {
                guru: this.currentGuru.type,
                questionLength: question.length,
                streaming: this.isStreamingEnabled
            });
            
            // Get response from AI
            if (this.isStreamingEnabled && AppConfig.features.enableStreamingResponses) {
                await this.getStreamingResponse(question);
            } else {
                await this.getStandardResponse(question);
            }
            
            // Add to conversation history
            this.addToConversationHistory(question, this.lastResponse);
            
            // Clear the question input
            event.target.reset();
            
        } catch (error) {
            console.error('Question submission failed:', error);
            this.handleApiError(error, 'Failed to get spiritual guidance');
        } finally {
            this.hideLoadingState();
        }
    }
    
    /**
     * Get standard (non-streaming) response from AI
     * @param {string} question - The user's question
     */
    async getStandardResponse(question) {
        const requestBody = {
            guru_type: this.currentGuru.type,
            question: question,
            user_context: this.getUserContext()
        };
        
        const response = await fetch(`${AppConfig.api.baseUrl}${AppConfig.api.endpoints.ask}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
            throw new Error(`API request failed: ${response.status} ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            this.lastResponse = data.response;
            this.displayResponse(data);
        } else {
            throw new Error(data.error || 'Unknown API error');
        }
    }
    
    /**
     * Get streaming response from AI
     * @param {string} question - The user's question
     */
    async getStreamingResponse(question) {
        const requestBody = {
            guru_type: this.currentGuru.type,
            question: question,
            user_context: this.getUserContext()
        };
        
        // Create abort controller for cancelling stream
        this.currentStreamController = new AbortController();
        
        try {
            const response = await fetch(`${AppConfig.api.baseUrl}${AppConfig.api.endpoints.askStream}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'text/event-stream'
                },
                body: JSON.stringify(requestBody),
                signal: this.currentStreamController.signal
            });
            
            if (!response.ok) {
                throw new Error(`Streaming request failed: ${response.status} ${response.statusText}`);
            }
            
            // Setup response display area
            const responseArea = this.prepareResponseArea();
            let fullResponse = '';
            
            // Process streaming response
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            
            while (true) {
                const { done, value } = await reader.read();
                
                if (done) break;
                
                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');
                
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = line.substring(6);
                        
                        if (data === '[DONE]') {
                            this.finalizeStreamingResponse(fullResponse);
                            return;
                        }
                        
                        try {
                            const parsed = JSON.parse(data);
                            if (parsed.chunk) {
                                fullResponse += parsed.chunk;
                                this.appendToResponse(responseArea, parsed.chunk);
                            } else if (parsed.error) {
                                throw new Error(parsed.error);
                            }
                        } catch (parseError) {
                            console.warn('Failed to parse streaming data:', parseError);
                        }
                    }
                }
            }
            
            this.lastResponse = fullResponse;
            
        } finally {
            this.currentStreamController = null;
        }
    }
    
    /**
     * Prepare response area for displaying AI response
     * @returns {HTMLElement} - The response area element
     */
    prepareResponseArea() {
        let responseArea = document.getElementById('response-area');
        
        if (!responseArea) {
            responseArea = document.createElement('div');
            responseArea.id = 'response-area';
            responseArea.className = 'ai-response';
            
            const responseContainer = document.getElementById('response-container') || 
                                    document.querySelector('.question-interface');
            responseContainer.appendChild(responseArea);
        }
        
        // Clear previous response
        responseArea.innerHTML = `
            <div class="response-header">
                <span class="guru-name">${this.currentGuru.info.name}</span>
                <span class="response-time">${new Date().toLocaleTimeString()}</span>
            </div>
            <div class="response-content"></div>
        `;
        
        return responseArea.querySelector('.response-content');
    }
    
    /**
     * Append text to streaming response
     * @param {HTMLElement} responseArea - The response content area
     * @param {string} text - Text to append
     */
    appendToResponse(responseArea, text) {
        responseArea.textContent += text;
        
        // Auto-scroll to keep up with streaming content
        responseArea.scrollTop = responseArea.scrollHeight;
    }
    
    /**
     * Finalize streaming response
     * @param {string} fullResponse - The complete response text
     */
    finalizeStreamingResponse(fullResponse) {
        // Add any final formatting or processing
        const responseArea = document.getElementById('response-area');
        if (responseArea) {
            responseArea.classList.add('response-complete');
        }
        
        // Track completion
        this.trackEvent('streaming_response_complete', {
            guru: this.currentGuru.type,
            responseLength: fullResponse.length
        });
    }
    
    /**
     * Display standard AI response
     * @param {Object} responseData - Response data from API
     */
    displayResponse(responseData) {
        const responseArea = this.prepareResponseArea();
        responseArea.innerHTML = this.formatResponse(responseData.response);
        
        // Add metadata display
        if (responseData.tokens_used || responseData.model) {
            const metadata = document.createElement('div');
            metadata.className = 'response-metadata';
            metadata.innerHTML = `
                ${responseData.model ? `<span>Model: ${responseData.model}</span>` : ''}
                ${responseData.tokens_used ? `<span>Tokens: ${responseData.tokens_used}</span>` : ''}
            `;
            responseArea.parentNode.appendChild(metadata);
        }
        
        // Scroll to response
        responseArea.scrollIntoView({ behavior: 'smooth' });
    }
    
    /**
     * Format response text for display
     * @param {string} text - Raw response text
     * @returns {string} - Formatted HTML
     */
    formatResponse(text) {
        // Basic formatting: convert line breaks to paragraphs
        return text.split('\n\n')
                  .map(paragraph => `<p>${paragraph}</p>`)
                  .join('');
    }
    
    /**
     * Get user context for personalized responses
     * @returns {Object} - User context object
     */
    getUserContext() {
        return {
            experience_level: this.getUserExperienceLevel(),
            previous_topics: this.getPreviousTopics(),
            session_length: this.conversationHistory.length,
            preferred_style: this.getPreferredStyle()
        };
    }
    
    /**
     * Determine user experience level based on conversation history
     * @returns {string} - Experience level
     */
    getUserExperienceLevel() {
        if (this.conversationHistory.length === 0) {
            return 'beginner';
        } else if (this.conversationHistory.length < 5) {
            return 'intermediate';
        } else {
            return 'advanced';
        }
    }
    
    /**
     * Extract previous topics from conversation history
     * @returns {Array} - Array of previous topics
     */
    getPreviousTopics() {
        return this.conversationHistory
            .map(entry => entry.question)
            .slice(-3) // Last 3 questions
            .flatMap(question => this.extractTopics(question));
    }
    
    /**
     * Extract topics from question text
     * @param {string} question - The question text
     * @returns {Array} - Extracted topics
     */
    extractTopics(question) {
        const topicKeywords = [
            'meditation', 'peace', 'anxiety', 'stress', 'love', 'purpose',
            'dharma', 'karma', 'yoga', 'mindfulness', 'spiritual', 'divine'
        ];
        
        return topicKeywords.filter(topic => 
            question.toLowerCase().includes(topic)
        );
    }
    
    /**
     * Get user's preferred response style
     * @returns {string} - Preferred style
     */
    getPreferredStyle() {
        // Could be determined from user settings or conversation analysis
        return 'practical'; // Default to practical guidance
    }
    
    /**
     * Add entry to conversation history
     * @param {string} question - User's question
     * @param {string} response - AI's response
     */
    addToConversationHistory(question, response) {
        this.conversationHistory.push({
            timestamp: new Date(),
            guru: this.currentGuru.type,
            question: question,
            response: response
        });
        
        // Limit history size to prevent memory issues
        if (this.conversationHistory.length > 20) {
            this.conversationHistory = this.conversationHistory.slice(-15);
        }
        
        // Update conversation display
        this.updateConversationDisplay();
    }
    
    /**
     * Update conversation history display
     */
    updateConversationDisplay() {
        const historyContainer = document.getElementById('conversation-history');
        
        if (!historyContainer) return;
        
        // Clear existing history
        historyContainer.innerHTML = '';
        
        // Display recent conversation entries
        this.conversationHistory.slice(-5).forEach((entry, index) => {
            const entryElement = document.createElement('div');
            entryElement.className = 'conversation-entry';
            entryElement.innerHTML = `
                <div class="entry-header">
                    <span class="guru-name">${this.gurus[entry.guru]?.name || entry.guru}</span>
                    <span class="timestamp">${entry.timestamp.toLocaleTimeString()}</span>
                </div>
                <div class="question">${entry.question}</div>
                <div class="response">${this.formatResponse(entry.response)}</div>
            `;
            
            historyContainer.appendChild(entryElement);
        });
    }
    
    /**
     * Clear conversation history
     */
    clearConversation() {
        if (confirm('Clear conversation history?')) {
            this.conversationHistory = [];
            this.updateConversationDisplay();
            
            // Clear response area
            const responseArea = document.getElementById('response-area');
            if (responseArea) {
                responseArea.innerHTML = '';
            }
            
            this.trackEvent('conversation_cleared');
        }
    }
    
    /**
     * Show loading state in UI
     */
    showLoadingState() {
        const submitButton = document.querySelector('#question-form button[type="submit"]');
        if (submitButton && submitButton.showLoading) {
            submitButton.showLoading();
        }
        
        // Show loading indicator
        this.showNotification('Getting spiritual guidance...', 'info', false);
    }
    
    /**
     * Hide loading state in UI
     */
    hideLoadingState() {
        const submitButton = document.querySelector('#question-form button[type="submit"]');
        if (submitButton && submitButton.hideLoading) {
            submitButton.hideLoading();
        }
        
        // Hide loading notification
        this.hideNotification();
    }
    
    /**
     * Handle API errors gracefully
     * @param {Error} error - The error object
     * @param {string} userMessage - User-friendly error message
     */
    handleApiError(error, userMessage) {
        console.error('API Error:', error);
        
        // Show user-friendly error message
        this.showErrorMessage(userMessage);
        
        // Track error for analytics
        this.trackEvent('api_error', {
            error: error.message,
            endpoint: error.endpoint || 'unknown'
        });
        
        // Attempt graceful degradation
        this.enableOfflineMode();
    }
    
    /**
     * Show error message to user
     * @param {string} message - Error message to display
     */
    showErrorMessage(message) {
        this.showNotification(message, 'error');
    }
    
    /**
     * Show notification to user
     * @param {string} message - Notification message
     * @param {string} type - Notification type (success, error, warning, info)
     * @param {boolean} autoHide - Whether to auto-hide the notification
     */
    showNotification(message, type = 'info', autoHide = true) {
        // Implementation depends on your notification system
        console.log(`${type.toUpperCase()}: ${message}`);
        
        // You can integrate with a toast library or custom notification system
        if (autoHide && type !== 'error') {
            setTimeout(() => this.hideNotification(), 5000);
        }
    }
    
    /**
     * Hide notification
     */
    hideNotification() {
        // Implementation depends on your notification system
    }
    
    /**
     * Enable offline mode when API is unavailable
     */
    enableOfflineMode() {
        if (AppConfig.features.enableOfflineMode) {
            // Show offline message
            this.showNotification(
                'Working in offline mode. Some features may be limited.',
                'warning',
                false
            );
            
            // Enable offline features
            this.setupOfflineFeatures();
        }
    }
    
    /**
     * Setup offline features
     */
    setupOfflineFeatures() {
        // Implement offline features like cached responses, local guidance, etc.
        console.log('Offline mode enabled');
    }
    
    /**
     * Handle window resize for responsive adjustments
     */
    handleWindowResize() {
        // Adjust layout for mobile/desktop
        const isMobile = window.innerWidth < 768;
        document.body.classList.toggle('mobile-layout', isMobile);
    }
    
    /**
     * Track events for analytics
     * @param {string} eventName - Name of the event
     * @param {Object} eventData - Additional event data
     */
    trackEvent(eventName, eventData = {}) {
        if (AppConfig.features.enableAnalytics) {
            // Integration with analytics service (Google Analytics, etc.)
            console.log('Analytics Event:', eventName, eventData);
            
            // Example integration with gtag (Google Analytics)
            if (typeof gtag !== 'undefined') {
                gtag('event', eventName, eventData);
            }
        }
    }
    
    /**
     * Dispatch custom event
     * @param {string} eventName - Name of the event
     * @param {Object} eventData - Event data
     */
    dispatchEvent(eventName, eventData = {}) {
        const customEvent = new CustomEvent(eventName, {
            detail: eventData
        });
        document.dispatchEvent(customEvent);
    }
}

/**
 * Initialize application when DOM is loaded
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('AI Empower Heart application loading...');
    
    // Create and initialize the main application
    const app = new AIEmpowerHeartApp();
    
    // Make app globally accessible for debugging
    window.AIEmpowerHeartApp = app;
    
    // Initialize the application
    app.init().catch(error => {
        console.error('Failed to initialize application:', error);
    });
    
    // Legacy smooth scrolling for backward compatibility
    // Add smooth scrolling for anchor links (legacy support)
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
});
