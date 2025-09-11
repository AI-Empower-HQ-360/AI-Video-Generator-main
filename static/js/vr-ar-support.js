/**
 * VR/AR Video Support
 * Implements WebXR and AR.js for immersive video experiences
 */

class VRARManager {
    constructor(videoPlayer) {
        this.videoPlayer = videoPlayer;
        this.vrSession = null;
        this.arSession = null;
        this.vrSupported = false;
        this.arSupported = false;
        this.vrDisplay = null;
        this.arDisplay = null;
        
        this.init();
    }

    async init() {
        await this.checkVRSupport();
        await this.checkARSupport();
        this.setupVRARControls();
        this.setupImmersiveEnvironment();
    }

    async checkVRSupport() {
        if ('xr' in navigator) {
            try {
                this.vrSupported = await navigator.xr.isSessionSupported('immersive-vr');
                console.log('VR Support:', this.vrSupported);
            } catch (error) {
                console.warn('VR not supported:', error);
            }
        }
    }

    async checkARSupport() {
        if ('xr' in navigator) {
            try {
                this.arSupported = await navigator.xr.isSessionSupported('immersive-ar');
                console.log('AR Support:', this.arSupported);
            } catch (error) {
                console.warn('AR not supported:', error);
            }
        }
    }

    setupVRARControls() {
        const videoContainer = this.videoPlayer.container.querySelector('.video-container');
        
        const vrArControls = document.createElement('div');
        vrArControls.className = 'vr-ar-controls';
        vrArControls.innerHTML = `
            <button id="vr-btn" class="vr-btn" ${!this.vrSupported ? 'disabled' : ''}>
                🥽 VR
            </button>
            <button id="ar-btn" class="ar-btn" ${!this.arSupported ? 'disabled' : ''}>
                🌐 AR
            </button>
            <button id="360-btn" class="mode-btn">
                🔄 360°
            </button>
            <button id="immersive-mode-btn" class="mode-btn">
                📺 Theater
            </button>
        `;
        
        videoContainer.appendChild(vrArControls);
        
        this.setupVRAREvents();
    }

    setupVRAREvents() {
        document.getElementById('vr-btn').addEventListener('click', () => {
            if (this.vrSupported) {
                this.enterVRMode();
            } else {
                this.showUnsupportedMessage('VR');
            }
        });

        document.getElementById('ar-btn').addEventListener('click', () => {
            if (this.arSupported) {
                this.enterARMode();
            } else {
                this.showUnsupportedMessage('AR');
            }
        });

        document.getElementById('360-btn').addEventListener('click', () => {
            this.toggle360Mode();
        });

        document.getElementById('immersive-mode-btn').addEventListener('click', () => {
            this.toggleImmersiveMode();
        });
    }

    async enterVRMode() {
        try {
            if (!navigator.xr) {
                throw new Error('WebXR not supported');
            }

            this.vrSession = await navigator.xr.requestSession('immersive-vr', {
                requiredFeatures: ['local-floor']
            });

            await this.setupVRScene();
            
            this.vrSession.addEventListener('end', () => {
                this.exitVRMode();
            });

            // Hide normal video controls
            this.videoPlayer.video.style.display = 'none';
            
        } catch (error) {
            console.error('Failed to enter VR mode:', error);
            this.showErrorMessage('Failed to start VR mode. Make sure your VR headset is connected.');
        }
    }

    async setupVRScene() {
        // Create VR-specific video environment
        const vrContainer = document.createElement('div');
        vrContainer.id = 'vr-scene';
        vrContainer.innerHTML = `
            <a-scene embedded style="height: 100vh; width: 100vw;">
                <a-assets>
                    <video id="vr-video" 
                           src="${this.videoPlayer.video.src}" 
                           autoplay 
                           loop="true"
                           crossorigin="anonymous">
                    </video>
                </a-assets>
                
                <!-- VR Video Dome -->
                <a-videosphere src="#vr-video" rotation="0 180 0"></a-videosphere>
                
                <!-- Interactive Elements in VR -->
                <a-sphere position="2 2 -5" radius="0.3" color="#FFD700" 
                          class="vr-hotspot" 
                          animation="property: rotation; to: 0 360 0; loop: true; dur: 10000">
                </a-sphere>
                
                <!-- VR UI Panel -->
                <a-plane position="0 1 -3" rotation="-15 0 0" width="4" height="2" 
                         color="#000" opacity="0.7" class="vr-ui-panel">
                    <a-text value="Spiritual VR Experience" position="0 0.5 0.01" 
                            align="center" color="#FFD700"></a-text>
                    
                    <!-- VR Controls -->
                    <a-box position="-1 -0.3 0.01" depth="0.1" height="0.3" width="0.8" 
                           color="#FFD700" class="vr-control-btn" 
                           text="value: Play/Pause; align: center; color: black">
                    </a-box>
                    
                    <a-box position="0 -0.3 0.01" depth="0.1" height="0.3" width="0.8" 
                           color="#FFA500" class="vr-control-btn"
                           text="value: Menu; align: center; color: black">
                    </a-box>
                    
                    <a-box position="1 -0.3 0.01" depth="0.1" height="0.3" width="0.8" 
                           color="#FF6B6B" class="vr-control-btn"
                           text="value: Exit VR; align: center; color: black">
                    </a-box>
                </a-plane>
                
                <!-- Hand Controllers -->
                <a-entity laser-controls="hand: right" raycaster="objects: .vr-hotspot, .vr-control-btn"></a-entity>
                <a-entity laser-controls="hand: left"></a-entity>
                
                <!-- VR Camera -->
                <a-camera position="0 1.6 0" look-controls wasd-controls></a-camera>
                
                <!-- Lighting -->
                <a-light type="ambient" color="#404040"></a-light>
                <a-light type="point" position="0 5 0" color="#FFD700"></a-light>
            </a-scene>
        `;
        
        document.body.appendChild(vrContainer);
        
        // Setup VR interactions
        this.setupVRInteractions();
    }

    setupVRInteractions() {
        // VR-specific event handlers
        document.querySelectorAll('.vr-control-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const text = e.target.getAttribute('text').value;
                this.handleVRControl(text);
            });
        });
        
        document.querySelectorAll('.vr-hotspot').forEach(hotspot => {
            hotspot.addEventListener('click', () => {
                this.handleVRHotspotClick(hotspot);
            });
        });
    }

    handleVRControl(action) {
        const vrVideo = document.getElementById('vr-video');
        
        switch (action) {
            case 'Play/Pause':
                if (vrVideo.paused) {
                    vrVideo.play();
                } else {
                    vrVideo.pause();
                }
                break;
            case 'Menu':
                this.showVRMenu();
                break;
            case 'Exit VR':
                this.exitVRMode();
                break;
        }
    }

    handleVRHotspotClick(hotspot) {
        // Create VR feedback
        const feedback = document.createElement('a-text');
        feedback.setAttribute('value', 'Spiritual Insight Unlocked!');
        feedback.setAttribute('position', '0 3 -2');
        feedback.setAttribute('align', 'center');
        feedback.setAttribute('color', '#FFD700');
        feedback.setAttribute('animation', 'property: opacity; to: 0; dur: 3000');
        
        document.querySelector('a-scene').appendChild(feedback);
        
        setTimeout(() => {
            feedback.remove();
        }, 3000);
    }

    showVRMenu() {
        // Implement VR menu system
        const vrMenu = document.createElement('a-entity');
        vrMenu.innerHTML = `
            <a-plane position="0 2 -2" width="3" height="2" color="#000" opacity="0.8">
                <a-text value="VR Menu" position="0 0.7 0.01" align="center" color="#FFD700"></a-text>
                
                <a-box position="-0.7 0.2 0.01" width="1.2" height="0.3" depth="0.1" 
                       color="#FFD700" class="vr-menu-btn"
                       text="value: Meditation Mode; align: center; color: black">
                </a-box>
                
                <a-box position="0.7 0.2 0.01" width="1.2" height="0.3" depth="0.1" 
                       color="#FFA500" class="vr-menu-btn"
                       text="value: Wisdom Mode; align: center; color: black">
                </a-box>
                
                <a-box position="0 -0.3 0.01" width="1.2" height="0.3" depth="0.1" 
                       color="#FF6B6B" class="vr-menu-btn"
                       text="value: Close Menu; align: center; color: black">
                </a-box>
            </a-plane>
        `;
        
        document.querySelector('a-scene').appendChild(vrMenu);
        
        // Add menu interactions
        vrMenu.querySelectorAll('.vr-menu-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.target.getAttribute('text').value;
                this.handleVRMenuAction(action);
                vrMenu.remove();
            });
        });
    }

    handleVRMenuAction(action) {
        switch (action) {
            case 'Meditation Mode':
                this.switchVREnvironment('meditation');
                break;
            case 'Wisdom Mode':
                this.switchVREnvironment('wisdom');
                break;
            case 'Close Menu':
                // Menu already closed
                break;
        }
    }

    switchVREnvironment(mode) {
        const scene = document.querySelector('a-scene');
        const sky = scene.querySelector('a-sky') || document.createElement('a-sky');
        
        switch (mode) {
            case 'meditation':
                sky.setAttribute('color', '#87CEEB');
                sky.setAttribute('material', 'shader: gradient; topColor: #87CEEB; bottomColor: #98FB98');
                break;
            case 'wisdom':
                sky.setAttribute('color', '#191970');
                sky.setAttribute('material', 'shader: gradient; topColor: #191970; bottomColor: #4B0082');
                break;
        }
        
        if (!scene.querySelector('a-sky')) {
            scene.appendChild(sky);
        }
    }

    exitVRMode() {
        if (this.vrSession) {
            this.vrSession.end();
            this.vrSession = null;
        }
        
        // Remove VR scene
        const vrScene = document.getElementById('vr-scene');
        if (vrScene) {
            vrScene.remove();
        }
        
        // Restore normal video
        this.videoPlayer.video.style.display = 'block';
    }

    async enterARMode() {
        try {
            if (!navigator.xr) {
                throw new Error('WebXR not supported');
            }

            this.arSession = await navigator.xr.requestSession('immersive-ar', {
                requiredFeatures: ['local-floor', 'hit-test']
            });

            await this.setupARScene();
            
            this.arSession.addEventListener('end', () => {
                this.exitARMode();
            });

        } catch (error) {
            console.error('Failed to enter AR mode:', error);
            this.showErrorMessage('Failed to start AR mode. Make sure your device supports AR.');
        }
    }

    async setupARScene() {
        // Create AR overlay
        const arContainer = document.createElement('div');
        arContainer.id = 'ar-scene';
        arContainer.innerHTML = `
            <a-scene embedded 
                     arjs="sourceType: webcam; debugUIEnabled: false;" 
                     renderer="logarithmicDepthBuffer: true;"
                     vr-mode-ui="enabled: false">
                
                <a-assets>
                    <video id="ar-video" 
                           src="${this.videoPlayer.video.src}" 
                           autoplay 
                           muted
                           playsinline>
                    </video>
                </a-assets>
                
                <!-- AR Marker -->
                <a-marker preset="hiro" raycaster="objects: .ar-clickable" emitevents="true" cursor="fuse: false; rayOrigin: mouse;">
                    <!-- AR Video Screen -->
                    <a-plane src="#ar-video" 
                             position="0 0 0" 
                             rotation="-90 0 0" 
                             width="4" 
                             height="3"
                             class="ar-video-screen">
                    </a-plane>
                    
                    <!-- AR Controls -->
                    <a-box position="-2 0.1 1.5" 
                           depth="0.5" height="0.5" width="0.5" 
                           color="#FFD700" 
                           class="ar-clickable ar-play-btn"
                           text="value: ⏯️; align: center; color: black; width: 20">
                    </a-box>
                    
                    <a-box position="0 0.1 1.5" 
                           depth="0.5" height="0.5" width="0.5" 
                           color="#FFA500" 
                           class="ar-clickable ar-menu-btn"
                           text="value: 📱; align: center; color: black; width: 20">
                    </a-box>
                    
                    <a-box position="2 0.1 1.5" 
                           depth="0.5" height="0.5" width="0.5" 
                           color="#FF6B6B" 
                           class="ar-clickable ar-exit-btn"
                           text="value: ❌; align: center; color: black; width: 20">
                    </a-box>
                    
                    <!-- Floating Spiritual Elements -->
                    <a-sphere position="3 2 0" 
                              radius="0.3" 
                              color="#FFD700" 
                              opacity="0.7"
                              animation="property: rotation; to: 0 360 0; loop: true; dur: 5000"
                              class="ar-spiritual-orb">
                    </a-sphere>
                    
                    <a-text value="🕉️ Om Mani Padme Hum 🕉️" 
                            position="0 3 0" 
                            align="center" 
                            color="#FFD700"
                            animation="property: position; to: 0 4 0; dir: alternate; dur: 2000; loop: true">
                    </a-text>
                </a-marker>
                
                <a-entity camera></a-entity>
            </a-scene>
        `;
        
        document.body.appendChild(arContainer);
        this.setupARInteractions();
    }

    setupARInteractions() {
        document.querySelectorAll('.ar-clickable').forEach(element => {
            element.addEventListener('click', (e) => {
                if (e.target.classList.contains('ar-play-btn')) {
                    this.toggleARVideo();
                } else if (e.target.classList.contains('ar-menu-btn')) {
                    this.showARMenu();
                } else if (e.target.classList.contains('ar-exit-btn')) {
                    this.exitARMode();
                }
            });
        });
    }

    toggleARVideo() {
        const arVideo = document.getElementById('ar-video');
        if (arVideo.paused) {
            arVideo.play();
        } else {
            arVideo.pause();
        }
    }

    showARMenu() {
        // Create AR floating menu
        const arMenu = document.createElement('a-entity');
        arMenu.innerHTML = `
            <a-plane position="0 2 2" 
                     rotation="-20 0 0" 
                     width="3" 
                     height="2" 
                     color="#000" 
                     opacity="0.8">
                
                <a-text value="AR Spiritual Menu" 
                        position="0 0.7 0.01" 
                        align="center" 
                        color="#FFD700">
                </a-text>
                
                <a-box position="-0.7 0.2 0.01" 
                       width="1.2" height="0.3" depth="0.1" 
                       color="#FFD700" 
                       class="ar-menu-option"
                       text="value: Meditation; align: center; color: black">
                </a-box>
                
                <a-box position="0.7 0.2 0.01" 
                       width="1.2" height="0.3" depth="0.1" 
                       color="#FFA500" 
                       class="ar-menu-option"
                       text="value: Guidance; align: center; color: black">
                </a-box>
            </a-plane>
        `;
        
        const marker = document.querySelector('a-marker');
        marker.appendChild(arMenu);
        
        // Auto-remove menu after 5 seconds
        setTimeout(() => {
            arMenu.remove();
        }, 5000);
    }

    exitARMode() {
        if (this.arSession) {
            this.arSession.end();
            this.arSession = null;
        }
        
        const arScene = document.getElementById('ar-scene');
        if (arScene) {
            arScene.remove();
        }
    }

    toggle360Mode() {
        const video = this.videoPlayer.video;
        
        if (!this.is360Mode) {
            // Convert to 360 video view
            video.style.filter = 'brightness(1.1) contrast(1.1)';
            video.style.transform = 'perspective(1000px) rotateY(10deg)';
            
            // Add 360 controls
            this.add360Controls();
            this.is360Mode = true;
        } else {
            // Return to normal view
            video.style.filter = '';
            video.style.transform = '';
            this.remove360Controls();
            this.is360Mode = false;
        }
    }

    add360Controls() {
        const controls360 = document.createElement('div');
        controls360.className = 'controls-360';
        controls360.innerHTML = `
            <div class="rotation-controls">
                <button class="rotate-btn" data-direction="up">↑</button>
                <div class="horizontal-controls">
                    <button class="rotate-btn" data-direction="left">←</button>
                    <button class="rotate-btn" data-direction="center">⊙</button>
                    <button class="rotate-btn" data-direction="right">→</button>
                </div>
                <button class="rotate-btn" data-direction="down">↓</button>
            </div>
        `;
        
        this.videoPlayer.container.appendChild(controls360);
        
        controls360.addEventListener('click', (e) => {
            if (e.target.classList.contains('rotate-btn')) {
                this.handle360Rotation(e.target.dataset.direction);
            }
        });
    }

    handle360Rotation(direction) {
        const video = this.videoPlayer.video;
        let currentTransform = video.style.transform || '';
        
        switch (direction) {
            case 'left':
                video.style.transform = currentTransform + ' rotateY(-15deg)';
                break;
            case 'right':
                video.style.transform = currentTransform + ' rotateY(15deg)';
                break;
            case 'up':
                video.style.transform = currentTransform + ' rotateX(15deg)';
                break;
            case 'down':
                video.style.transform = currentTransform + ' rotateX(-15deg)';
                break;
            case 'center':
                video.style.transform = 'perspective(1000px)';
                break;
        }
    }

    remove360Controls() {
        const controls360 = this.videoPlayer.container.querySelector('.controls-360');
        if (controls360) {
            controls360.remove();
        }
    }

    toggleImmersiveMode() {
        if (!this.isImmersiveMode) {
            // Enter theater mode
            this.enterTheaterMode();
            this.isImmersiveMode = true;
        } else {
            // Exit theater mode
            this.exitTheaterMode();
            this.isImmersiveMode = false;
        }
    }

    enterTheaterMode() {
        const body = document.body;
        const videoWrapper = this.videoPlayer.container;
        
        // Create fullscreen overlay
        const theaterOverlay = document.createElement('div');
        theaterOverlay.className = 'theater-overlay';
        theaterOverlay.innerHTML = `
            <div class="theater-environment">
                <div class="theater-screen">
                    ${videoWrapper.innerHTML}
                </div>
                <div class="theater-seats"></div>
                <button class="exit-theater-btn">Exit Theater</button>
            </div>
        `;
        
        body.appendChild(theaterOverlay);
        
        theaterOverlay.querySelector('.exit-theater-btn').addEventListener('click', () => {
            this.exitTheaterMode();
        });
    }

    exitTheaterMode() {
        const theaterOverlay = document.querySelector('.theater-overlay');
        if (theaterOverlay) {
            theaterOverlay.remove();
        }
        this.isImmersiveMode = false;
    }

    showUnsupportedMessage(type) {
        const message = document.createElement('div');
        message.className = 'unsupported-message';
        message.innerHTML = `
            <div class="message-content">
                <h3>${type} Not Supported</h3>
                <p>Your device doesn't support ${type} experiences. Please try on a compatible device.</p>
                <button onclick="this.parentElement.parentElement.remove()">OK</button>
            </div>
        `;
        
        document.body.appendChild(message);
    }

    showErrorMessage(text) {
        const error = document.createElement('div');
        error.className = 'error-message';
        error.innerHTML = `
            <div class="error-content">
                <h3>Error</h3>
                <p>${text}</p>
                <button onclick="this.parentElement.parentElement.remove()">OK</button>
            </div>
        `;
        
        document.body.appendChild(error);
    }
}

// Include A-Frame and AR.js libraries
function loadVRARLibraries() {
    // Load A-Frame
    if (!document.querySelector('script[src*="aframe"]')) {
        const aframeScript = document.createElement('script');
        aframeScript.src = 'https://aframe.io/releases/1.4.0/aframe.min.js';
        document.head.appendChild(aframeScript);
    }
    
    // Load AR.js
    if (!document.querySelector('script[src*="ar.js"]')) {
        const arScript = document.createElement('script');
        arScript.src = 'https://cdn.jsdelivr.net/gh/aframevr/ar.js@master/aframe/build/aframe-ar.js';
        document.head.appendChild(arScript);
    }
}

// Load libraries when needed
document.addEventListener('DOMContentLoaded', loadVRARLibraries);

// Export for use with the main video player
window.VRARManager = VRARManager;