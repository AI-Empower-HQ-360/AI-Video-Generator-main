/**
 * Voice Commands and Gesture Controls
 * Implements speech recognition and gesture detection for hands-free interaction
 */

class VoiceGestureController {
    constructor(videoPlayer) {
        this.videoPlayer = videoPlayer;
        this.recognition = null;
        this.gestureDetection = null;
        this.isListening = false;
        this.isGestureEnabled = false;
        this.commands = {};
        this.gestureCanvas = null;
        this.gestureContext = null;
        this.handPoses = [];
        
        this.init();
    }

    async init() {
        this.setupVoiceRecognition();
        this.setupGestureDetection();
        this.setupCommands();
        this.createControlsUI();
    }

    setupVoiceRecognition() {
        // Check for speech recognition support
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        
        if (SpeechRecognition) {
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = true;
            this.recognition.interimResults = true;
            this.recognition.lang = 'en-US';
            
            this.recognition.onstart = () => {
                this.isListening = true;
                this.showVoiceIndicator(true);
                console.log('Voice recognition started');
            };
            
            this.recognition.onend = () => {
                this.isListening = false;
                this.showVoiceIndicator(false);
                console.log('Voice recognition ended');
            };
            
            this.recognition.onresult = (event) => {
                this.processVoiceCommand(event);
            };
            
            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.showErrorMessage(`Voice command error: ${event.error}`);
            };
        } else {
            console.warn('Speech recognition not supported');
        }
    }

    async setupGestureDetection() {
        try {
            // Load MediaPipe Hands library
            await this.loadHandDetectionLibrary();
            
            // Setup camera for gesture detection
            this.setupGestureCamera();
            
        } catch (error) {
            console.warn('Gesture detection not available:', error);
        }
    }

    async loadHandDetectionLibrary() {
        return new Promise((resolve, reject) => {
            // Load MediaPipe Hands
            if (!window.Hands) {
                const script = document.createElement('script');
                script.src = 'https://cdn.jsdelivr.net/npm/@mediapipe/hands/hands.js';
                script.onload = () => {
                    const cameraScript = document.createElement('script');
                    cameraScript.src = 'https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js';
                    cameraScript.onload = resolve;
                    cameraScript.onerror = reject;
                    document.head.appendChild(cameraScript);
                };
                script.onerror = reject;
                document.head.appendChild(script);
            } else {
                resolve();
            }
        });
    }

    setupGestureCamera() {
        // Create hidden canvas for gesture detection
        this.gestureCanvas = document.createElement('canvas');
        this.gestureCanvas.style.display = 'none';
        this.gestureCanvas.width = 640;
        this.gestureCanvas.height = 480;
        document.body.appendChild(this.gestureCanvas);
        
        this.gestureContext = this.gestureCanvas.getContext('2d');
        
        // Setup MediaPipe Hands
        if (window.Hands) {
            this.hands = new window.Hands({
                locateFile: (file) => {
                    return `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`;
                }
            });
            
            this.hands.setOptions({
                maxNumHands: 2,
                modelComplexity: 1,
                minDetectionConfidence: 0.5,
                minTrackingConfidence: 0.5
            });
            
            this.hands.onResults((results) => {
                this.processGestureResults(results);
            });
        }
    }

    setupCommands() {
        this.commands = {
            // Video controls
            'play': () => this.videoPlayer.video.play(),
            'pause': () => this.videoPlayer.video.pause(),
            'stop': () => {
                this.videoPlayer.video.pause();
                this.videoPlayer.video.currentTime = 0;
            },
            'restart': () => {
                this.videoPlayer.video.currentTime = 0;
                this.videoPlayer.video.play();
            },
            'mute': () => this.videoPlayer.video.muted = true,
            'unmute': () => this.videoPlayer.video.muted = false,
            'volume up': () => {
                const video = this.videoPlayer.video;
                video.volume = Math.min(1, video.volume + 0.1);
            },
            'volume down': () => {
                const video = this.videoPlayer.video;
                video.volume = Math.max(0, video.volume - 0.1);
            },
            
            // Navigation
            'next scene': () => this.videoPlayer.loadScene('next'),
            'previous scene': () => this.videoPlayer.loadScene('previous'),
            'go to meditation': () => this.loadSpiritualContent('meditation'),
            'go to wisdom': () => this.loadSpiritualContent('wisdom'),
            'go to practice': () => this.loadSpiritualContent('practice'),
            
            // Interactive features
            'show achievements': () => this.videoPlayer.toggleAchievements(),
            'show chat': () => this.videoPlayer.toggleChat(),
            'show hotspots': () => this.videoPlayer.toggleHotspots(),
            
            // Immersive modes
            'enter vr': () => this.triggerVRMode(),
            'enter ar': () => this.triggerARMode(),
            'theater mode': () => this.triggerTheaterMode(),
            '360 mode': () => this.trigger360Mode(),
            
            // Spiritual commands
            'start meditation': () => this.startMeditationSession(),
            'end meditation': () => this.endMeditationSession(),
            'wisdom quote': () => this.showWisdomQuote(),
            'breathing exercise': () => this.startBreathingExercise(),
            
            // System commands
            'help': () => this.showVoiceHelp(),
            'commands': () => this.showAvailableCommands(),
            'stop listening': () => this.stopVoiceRecognition()
        };
        
        // Add gesture commands
        this.gestureCommands = {
            'thumbs_up': () => this.commands['play'](),
            'thumbs_down': () => this.commands['pause'](),
            'peace_sign': () => this.showWisdomQuote(),
            'palm_open': () => this.commands['stop'](),
            'fist': () => this.commands['mute'](),
            'point_up': () => this.commands['volume up'](),
            'point_down': () => this.commands['volume down'](),
            'wave': () => this.showAvailableCommands(),
            'namaste': () => this.startMeditationSession()
        };
    }

    createControlsUI() {
        const controlsContainer = document.createElement('div');
        controlsContainer.className = 'voice-gesture-controls';
        controlsContainer.innerHTML = `
            <div class="voice-controls">
                <button id="start-voice" class="voice-btn">🎤 Start Voice</button>
                <button id="stop-voice" class="voice-btn" disabled>🔇 Stop Voice</button>
                <div class="voice-indicator" id="voice-indicator">
                    <span class="indicator-dot"></span>
                    <span class="indicator-text">Listening...</span>
                </div>
            </div>
            
            <div class="gesture-controls">
                <button id="start-gesture" class="gesture-btn">👋 Start Gestures</button>
                <button id="stop-gesture" class="gesture-btn" disabled>✋ Stop Gestures</button>
                <div class="gesture-overlay" id="gesture-overlay"></div>
            </div>
            
            <div class="control-help">
                <button id="show-commands" class="help-btn">📋 Voice Commands</button>
                <button id="show-gestures" class="help-btn">🤚 Gesture Guide</button>
            </div>
        `;
        
        this.videoPlayer.container.appendChild(controlsContainer);
        this.setupControlEvents();
    }

    setupControlEvents() {
        document.getElementById('start-voice').addEventListener('click', () => {
            this.startVoiceRecognition();
        });
        
        document.getElementById('stop-voice').addEventListener('click', () => {
            this.stopVoiceRecognition();
        });
        
        document.getElementById('start-gesture').addEventListener('click', () => {
            this.startGestureDetection();
        });
        
        document.getElementById('stop-gesture').addEventListener('click', () => {
            this.stopGestureDetection();
        });
        
        document.getElementById('show-commands').addEventListener('click', () => {
            this.showAvailableCommands();
        });
        
        document.getElementById('show-gestures').addEventListener('click', () => {
            this.showGestureGuide();
        });
    }

    startVoiceRecognition() {
        if (this.recognition && !this.isListening) {
            this.recognition.start();
            document.getElementById('start-voice').disabled = true;
            document.getElementById('stop-voice').disabled = false;
        }
    }

    stopVoiceRecognition() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
            document.getElementById('start-voice').disabled = false;
            document.getElementById('stop-voice').disabled = true;
        }
    }

    async startGestureDetection() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                video: { width: 640, height: 480 } 
            });
            
            const video = document.createElement('video');
            video.srcObject = stream;
            video.onloadedmetadata = () => {
                video.play();
                this.processGestureVideo(video);
            };
            
            this.isGestureEnabled = true;
            document.getElementById('start-gesture').disabled = true;
            document.getElementById('stop-gesture').disabled = false;
            
            this.showGestureOverlay(true);
            
        } catch (error) {
            console.error('Failed to start gesture detection:', error);
            this.showErrorMessage('Camera access required for gesture controls');
        }
    }

    stopGestureDetection() {
        this.isGestureEnabled = false;
        document.getElementById('start-gesture').disabled = false;
        document.getElementById('stop-gesture').disabled = true;
        this.showGestureOverlay(false);
    }

    processGestureVideo(video) {
        if (!this.isGestureEnabled) return;
        
        this.gestureContext.drawImage(video, 0, 0, this.gestureCanvas.width, this.gestureCanvas.height);
        
        if (this.hands) {
            this.hands.send({ image: this.gestureCanvas });
        }
        
        requestAnimationFrame(() => this.processGestureVideo(video));
    }

    processVoiceCommand(event) {
        let transcript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
            transcript += event.results[i][0].transcript;
        }
        
        transcript = transcript.toLowerCase().trim();
        
        // Check for commands
        for (const [command, action] of Object.entries(this.commands)) {
            if (transcript.includes(command)) {
                console.log(`Executing voice command: ${command}`);
                action();
                this.showCommandFeedback(command);
                break;
            }
        }
    }

    processGestureResults(results) {
        if (!this.isGestureEnabled) return;
        
        if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
            const landmarks = results.multiHandLandmarks[0];
            const gesture = this.recognizeGesture(landmarks);
            
            if (gesture && this.gestureCommands[gesture]) {
                console.log(`Executing gesture command: ${gesture}`);
                this.gestureCommands[gesture]();
                this.showGestureFeedback(gesture);
            }
            
            this.visualizeGesture(landmarks);
        }
    }

    recognizeGesture(landmarks) {
        // Simple gesture recognition based on hand landmarks
        const fingerTips = [4, 8, 12, 16, 20]; // Thumb, Index, Middle, Ring, Pinky tips
        const fingerBases = [3, 6, 10, 14, 18]; // Finger base points
        
        // Count extended fingers
        let extendedFingers = 0;
        const fingerStates = [];
        
        for (let i = 0; i < 5; i++) {
            const tip = landmarks[fingerTips[i]];
            const base = landmarks[fingerBases[i]];
            
            // Simple check if finger is extended (tip is higher than base)
            const isExtended = tip.y < base.y;
            fingerStates.push(isExtended);
            if (isExtended) extendedFingers++;
        }
        
        // Recognize specific gestures
        if (extendedFingers === 0) return 'fist';
        if (extendedFingers === 5) return 'palm_open';
        if (extendedFingers === 1 && fingerStates[0]) return 'thumbs_up';
        if (extendedFingers === 2 && fingerStates[1] && fingerStates[2]) return 'peace_sign';
        if (extendedFingers === 1 && fingerStates[1]) return 'point_up';
        if (extendedFingers === 4 && !fingerStates[0]) return 'wave';
        
        // Check for namaste (both hands together)
        if (results.multiHandLandmarks && results.multiHandLandmarks.length === 2) {
            return 'namaste';
        }
        
        return null;
    }

    visualizeGesture(landmarks) {
        const overlay = document.getElementById('gesture-overlay');
        if (!overlay) return;
        
        overlay.innerHTML = '';
        
        // Create gesture visualization
        landmarks.forEach((landmark, index) => {
            const dot = document.createElement('div');
            dot.className = 'gesture-point';
            dot.style.position = 'absolute';
            dot.style.left = `${landmark.x * 100}%`;
            dot.style.top = `${landmark.y * 100}%`;
            dot.style.width = '4px';
            dot.style.height = '4px';
            dot.style.backgroundColor = '#FFD700';
            dot.style.borderRadius = '50%';
            dot.style.zIndex = '1000';
            
            overlay.appendChild(dot);
        });
    }

    showVoiceIndicator(show) {
        const indicator = document.getElementById('voice-indicator');
        if (indicator) {
            indicator.style.display = show ? 'flex' : 'none';
        }
    }

    showGestureOverlay(show) {
        const overlay = document.getElementById('gesture-overlay');
        if (overlay) {
            overlay.style.display = show ? 'block' : 'none';
        }
    }

    showCommandFeedback(command) {
        const feedback = document.createElement('div');
        feedback.className = 'command-feedback';
        feedback.innerHTML = `
            <div class="feedback-content">
                <span class="feedback-icon">🎤</span>
                <span class="feedback-text">Voice: ${command}</span>
            </div>
        `;
        
        document.body.appendChild(feedback);
        
        setTimeout(() => {
            feedback.remove();
        }, 2000);
    }

    showGestureFeedback(gesture) {
        const feedback = document.createElement('div');
        feedback.className = 'gesture-feedback';
        feedback.innerHTML = `
            <div class="feedback-content">
                <span class="feedback-icon">👋</span>
                <span class="feedback-text">Gesture: ${gesture.replace('_', ' ')}</span>
            </div>
        `;
        
        document.body.appendChild(feedback);
        
        setTimeout(() => {
            feedback.remove();
        }, 2000);
    }

    showAvailableCommands() {
        const modal = document.createElement('div');
        modal.className = 'commands-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Voice Commands</h3>
                    <button class="close-modal">×</button>
                </div>
                <div class="modal-body">
                    <div class="command-categories">
                        <div class="command-category">
                            <h4>Video Controls</h4>
                            <ul>
                                <li><strong>"Play"</strong> - Start video</li>
                                <li><strong>"Pause"</strong> - Pause video</li>
                                <li><strong>"Stop"</strong> - Stop and reset</li>
                                <li><strong>"Mute/Unmute"</strong> - Audio control</li>
                                <li><strong>"Volume up/down"</strong> - Adjust volume</li>
                            </ul>
                        </div>
                        
                        <div class="command-category">
                            <h4>Navigation</h4>
                            <ul>
                                <li><strong>"Next scene"</strong> - Go to next</li>
                                <li><strong>"Previous scene"</strong> - Go back</li>
                                <li><strong>"Go to meditation"</strong> - Meditation content</li>
                                <li><strong>"Go to wisdom"</strong> - Wisdom content</li>
                            </ul>
                        </div>
                        
                        <div class="command-category">
                            <h4>Spiritual Features</h4>
                            <ul>
                                <li><strong>"Start meditation"</strong> - Begin session</li>
                                <li><strong>"Wisdom quote"</strong> - Show inspiration</li>
                                <li><strong>"Breathing exercise"</strong> - Guided breathing</li>
                            </ul>
                        </div>
                        
                        <div class="command-category">
                            <h4>Immersive Modes</h4>
                            <ul>
                                <li><strong>"Enter VR"</strong> - VR mode</li>
                                <li><strong>"Enter AR"</strong> - AR mode</li>
                                <li><strong>"Theater mode"</strong> - Immersive view</li>
                                <li><strong>"360 mode"</strong> - 360° video</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        modal.querySelector('.close-modal').addEventListener('click', () => {
            modal.remove();
        });
        
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }

    showGestureGuide() {
        const modal = document.createElement('div');
        modal.className = 'gesture-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Gesture Controls</h3>
                    <button class="close-modal">×</button>
                </div>
                <div class="modal-body">
                    <div class="gesture-grid">
                        <div class="gesture-item">
                            <div class="gesture-icon">👍</div>
                            <div class="gesture-name">Thumbs Up</div>
                            <div class="gesture-action">Play Video</div>
                        </div>
                        
                        <div class="gesture-item">
                            <div class="gesture-icon">👎</div>
                            <div class="gesture-name">Thumbs Down</div>
                            <div class="gesture-action">Pause Video</div>
                        </div>
                        
                        <div class="gesture-item">
                            <div class="gesture-icon">✌️</div>
                            <div class="gesture-name">Peace Sign</div>
                            <div class="gesture-action">Show Wisdom</div>
                        </div>
                        
                        <div class="gesture-item">
                            <div class="gesture-icon">✋</div>
                            <div class="gesture-name">Open Palm</div>
                            <div class="gesture-action">Stop Video</div>
                        </div>
                        
                        <div class="gesture-item">
                            <div class="gesture-icon">✊</div>
                            <div class="gesture-name">Fist</div>
                            <div class="gesture-action">Mute/Unmute</div>
                        </div>
                        
                        <div class="gesture-item">
                            <div class="gesture-icon">👋</div>
                            <div class="gesture-name">Wave</div>
                            <div class="gesture-action">Show Commands</div>
                        </div>
                        
                        <div class="gesture-item">
                            <div class="gesture-icon">🙏</div>
                            <div class="gesture-name">Namaste</div>
                            <div class="gesture-action">Start Meditation</div>
                        </div>
                        
                        <div class="gesture-item">
                            <div class="gesture-icon">☝️</div>
                            <div class="gesture-name">Point Up</div>
                            <div class="gesture-action">Volume Up</div>
                        </div>
                    </div>
                    
                    <div class="gesture-tips">
                        <h4>Tips for Better Detection:</h4>
                        <ul>
                            <li>Keep your hand visible to the camera</li>
                            <li>Use clear, distinct gestures</li>
                            <li>Hold gestures for 1-2 seconds</li>
                            <li>Ensure good lighting</li>
                        </ul>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        modal.querySelector('.close-modal').addEventListener('click', () => {
            modal.remove();
        });
        
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }

    // Spiritual command implementations
    loadSpiritualContent(type) {
        // Implementation for loading specific spiritual content
        console.log(`Loading ${type} content`);
    }

    startMeditationSession() {
        // Create meditation overlay
        const meditationOverlay = document.createElement('div');
        meditationOverlay.className = 'meditation-overlay';
        meditationOverlay.innerHTML = `
            <div class="meditation-session">
                <h3>🧘 Meditation Session Started</h3>
                <div class="meditation-timer">5:00</div>
                <div class="breathing-guide">
                    <div class="breath-circle"></div>
                    <p>Breathe in... and out...</p>
                </div>
                <button class="end-meditation">End Session</button>
            </div>
        `;
        
        document.body.appendChild(meditationOverlay);
        
        meditationOverlay.querySelector('.end-meditation').addEventListener('click', () => {
            this.endMeditationSession();
        });
        
        this.startMeditationTimer(300); // 5 minutes
    }

    endMeditationSession() {
        const overlay = document.querySelector('.meditation-overlay');
        if (overlay) {
            overlay.remove();
        }
    }

    startMeditationTimer(seconds) {
        const timer = document.querySelector('.meditation-timer');
        if (!timer) return;
        
        const interval = setInterval(() => {
            const minutes = Math.floor(seconds / 60);
            const remainingSeconds = seconds % 60;
            timer.textContent = `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
            
            seconds--;
            
            if (seconds < 0) {
                clearInterval(interval);
                this.endMeditationSession();
            }
        }, 1000);
    }

    showWisdomQuote() {
        const quotes = [
            "The mind is everything. What you think you become. - Buddha",
            "Peace comes from within. Do not seek it without. - Buddha",
            "You yourself, as much as anybody in the entire universe, deserve your love and affection. - Buddha",
            "In the end, just three things matter: How well we have lived, How well we have loved, How well we have learned to let go. - Jack Kornfield",
            "The present moment is the only time over which we have dominion. - Thích Nhất Hạnh"
        ];
        
        const randomQuote = quotes[Math.floor(Math.random() * quotes.length)];
        
        const quoteOverlay = document.createElement('div');
        quoteOverlay.className = 'wisdom-quote-overlay';
        quoteOverlay.innerHTML = `
            <div class="wisdom-quote">
                <div class="quote-icon">🌟</div>
                <p class="quote-text">${randomQuote}</p>
                <button class="close-quote">✨ Thank you ✨</button>
            </div>
        `;
        
        document.body.appendChild(quoteOverlay);
        
        quoteOverlay.querySelector('.close-quote').addEventListener('click', () => {
            quoteOverlay.remove();
        });
        
        setTimeout(() => {
            if (quoteOverlay.parentNode) {
                quoteOverlay.remove();
            }
        }, 10000);
    }

    startBreathingExercise() {
        const breathingOverlay = document.createElement('div');
        breathingOverlay.className = 'breathing-exercise-overlay';
        breathingOverlay.innerHTML = `
            <div class="breathing-exercise">
                <h3>🌬️ Breathing Exercise</h3>
                <div class="breathing-circle-container">
                    <div class="breathing-circle"></div>
                    <div class="breathing-instruction">Breathe In</div>
                </div>
                <button class="end-breathing">End Exercise</button>
            </div>
        `;
        
        document.body.appendChild(breathingOverlay);
        
        const circle = breathingOverlay.querySelector('.breathing-circle');
        const instruction = breathingOverlay.querySelector('.breathing-instruction');
        
        let isInhaling = true;
        const breathingInterval = setInterval(() => {
            if (isInhaling) {
                circle.style.transform = 'scale(1.5)';
                instruction.textContent = 'Breathe In';
            } else {
                circle.style.transform = 'scale(1)';
                instruction.textContent = 'Breathe Out';
            }
            isInhaling = !isInhaling;
        }, 4000);
        
        breathingOverlay.querySelector('.end-breathing').addEventListener('click', () => {
            clearInterval(breathingInterval);
            breathingOverlay.remove();
        });
    }

    triggerVRMode() {
        if (this.videoPlayer.vrArManager) {
            this.videoPlayer.vrArManager.enterVRMode();
        }
    }

    triggerARMode() {
        if (this.videoPlayer.vrArManager) {
            this.videoPlayer.vrArManager.enterARMode();
        }
    }

    triggerTheaterMode() {
        if (this.videoPlayer.vrArManager) {
            this.videoPlayer.vrArManager.toggleImmersiveMode();
        }
    }

    trigger360Mode() {
        if (this.videoPlayer.vrArManager) {
            this.videoPlayer.vrArManager.toggle360Mode();
        }
    }

    showVoiceHelp() {
        this.showAvailableCommands();
    }

    showErrorMessage(message) {
        const error = document.createElement('div');
        error.className = 'error-notification';
        error.innerHTML = `
            <div class="error-content">
                <span class="error-icon">⚠️</span>
                <span class="error-text">${message}</span>
                <button class="close-error">×</button>
            </div>
        `;
        
        document.body.appendChild(error);
        
        error.querySelector('.close-error').addEventListener('click', () => {
            error.remove();
        });
        
        setTimeout(() => {
            if (error.parentNode) {
                error.remove();
            }
        }, 5000);
    }
}

// Export for use with the main video player
window.VoiceGestureController = VoiceGestureController;