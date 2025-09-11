/**
 * Interactive Video Features
 * Handles hotspots, branching narratives, and interactive elements
 */

class InteractiveVideoPlayer {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.currentVideo = null;
        this.hotspots = [];
        this.currentScene = null;
        this.branchingData = {};
        this.userProgress = {
            achievements: [],
            decisions: [],
            completedScenes: []
        };
        this.options = {
            enableHotspots: true,
            enableBranching: true,
            enableGamification: true,
            ...options
        };
        
        this.init();
    }

    init() {
        this.setupVideoContainer();
        this.setupControls();
        this.setupHotspotSystem();
        this.setupBranchingSystem();
        this.setupGamificationSystem();
        this.loadUserProgress();
    }

    setupVideoContainer() {
        this.container.innerHTML = `
            <div class="interactive-video-wrapper">
                <div class="video-container" id="video-player-container">
                    <video id="main-video" controls>
                        <source src="" type="video/mp4">
                        Your browser does not support the video tag.
                    </video>
                    <div class="video-overlay" id="video-overlay"></div>
                    <div class="hotspot-container" id="hotspot-container"></div>
                    <div class="decision-overlay" id="decision-overlay" style="display: none;"></div>
                </div>
                <div class="video-sidebar">
                    <div class="achievement-panel" id="achievement-panel"></div>
                    <div class="progress-panel" id="progress-panel"></div>
                    <div class="chat-panel" id="chat-panel" style="display: none;"></div>
                </div>
            </div>
        `;

        this.video = document.getElementById('main-video');
        this.overlay = document.getElementById('video-overlay');
        this.hotspotContainer = document.getElementById('hotspot-container');
        this.decisionOverlay = document.getElementById('decision-overlay');
        
        this.setupVideoEvents();
    }

    setupVideoEvents() {
        this.video.addEventListener('timeupdate', () => {
            this.updateHotspots();
            this.checkBranchingPoints();
        });

        this.video.addEventListener('ended', () => {
            this.handleVideoEnd();
        });

        this.video.addEventListener('loadstart', () => {
            this.resetHotspots();
        });
    }

    setupControls() {
        const controlsHTML = `
            <div class="interactive-controls">
                <div class="scene-navigation">
                    <button id="prev-scene" class="nav-btn">← Previous</button>
                    <span id="scene-info">Scene 1 of 1</span>
                    <button id="next-scene" class="nav-btn">Next →</button>
                </div>
                <div class="interactive-options">
                    <button id="toggle-hotspots" class="option-btn active">Hotspots</button>
                    <button id="toggle-chat" class="option-btn">Chat</button>
                    <button id="toggle-achievements" class="option-btn">Achievements</button>
                </div>
            </div>
        `;
        
        this.container.appendChild(document.createElement('div'));
        this.container.lastChild.innerHTML = controlsHTML;
        
        this.setupControlEvents();
    }

    setupControlEvents() {
        document.getElementById('toggle-hotspots').addEventListener('click', () => {
            this.toggleHotspots();
        });

        document.getElementById('toggle-chat').addEventListener('click', () => {
            this.toggleChat();
        });

        document.getElementById('toggle-achievements').addEventListener('click', () => {
            this.toggleAchievements();
        });
    }

    setupHotspotSystem() {
        this.hotspotStyles = `
            <style>
                .hotspot {
                    position: absolute;
                    background: rgba(255, 215, 0, 0.8);
                    border: 2px solid #FFD700;
                    border-radius: 50%;
                    width: 40px;
                    height: 40px;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: #000;
                    font-weight: bold;
                    font-size: 18px;
                    transition: all 0.3s ease;
                    animation: pulse 2s infinite;
                }
                
                .hotspot:hover {
                    transform: scale(1.2);
                    background: rgba(255, 215, 0, 1);
                }
                
                @keyframes pulse {
                    0% { box-shadow: 0 0 0 0 rgba(255, 215, 0, 0.7); }
                    70% { box-shadow: 0 0 0 10px rgba(255, 215, 0, 0); }
                    100% { box-shadow: 0 0 0 0 rgba(255, 215, 0, 0); }
                }
                
                .hotspot-tooltip {
                    position: absolute;
                    background: rgba(0, 0, 0, 0.8);
                    color: white;
                    padding: 8px 12px;
                    border-radius: 4px;
                    font-size: 14px;
                    white-space: nowrap;
                    z-index: 1000;
                    display: none;
                }
                
                .decision-overlay {
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(0, 0, 0, 0.7);
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    z-index: 100;
                }
                
                .decision-box {
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    max-width: 500px;
                    text-align: center;
                }
                
                .decision-options {
                    display: flex;
                    flex-direction: column;
                    gap: 15px;
                    margin-top: 20px;
                }
                
                .decision-btn {
                    padding: 15px 25px;
                    background: #FFD700;
                    border: none;
                    border-radius: 8px;
                    cursor: pointer;
                    font-size: 16px;
                    font-weight: bold;
                    transition: all 0.3s ease;
                }
                
                .decision-btn:hover {
                    background: #FFA500;
                    transform: translateY(-2px);
                }
            </style>
        `;
        
        document.head.insertAdjacentHTML('beforeend', this.hotspotStyles);
    }

    setupBranchingSystem() {
        this.branchingData = {
            scenes: {},
            currentScene: 'intro',
            decisions: []
        };
    }

    setupGamificationSystem() {
        this.achievements = [
            { id: 'first_interaction', name: 'First Steps', description: 'Made your first interaction', icon: '🌟' },
            { id: 'decision_maker', name: 'Decision Maker', description: 'Made 5 decisions', icon: '🎯' },
            { id: 'explorer', name: 'Explorer', description: 'Found all hotspots in a scene', icon: '🔍' },
            { id: 'wisdom_seeker', name: 'Wisdom Seeker', description: 'Completed spiritual journey', icon: '🧘' }
        ];
        
        this.updateAchievementPanel();
    }

    // Hotspot Management
    addHotspot(timeStart, timeEnd, x, y, content, action) {
        const hotspot = {
            id: `hotspot_${Date.now()}`,
            timeStart,
            timeEnd,
            x,
            y,
            content,
            action,
            element: null
        };
        
        this.hotspots.push(hotspot);
        return hotspot.id;
    }

    createHotspotElement(hotspot) {
        const element = document.createElement('div');
        element.className = 'hotspot';
        element.style.left = `${hotspot.x}%`;
        element.style.top = `${hotspot.y}%`;
        element.innerHTML = '💫';
        element.title = hotspot.content;
        
        element.addEventListener('click', () => {
            this.handleHotspotClick(hotspot);
        });
        
        element.addEventListener('mouseenter', () => {
            this.showHotspotTooltip(element, hotspot.content);
        });
        
        element.addEventListener('mouseleave', () => {
            this.hideHotspotTooltip();
        });
        
        return element;
    }

    updateHotspots() {
        const currentTime = this.video.currentTime;
        
        this.hotspots.forEach(hotspot => {
            const shouldShow = currentTime >= hotspot.timeStart && currentTime <= hotspot.timeEnd;
            
            if (shouldShow && !hotspot.element) {
                hotspot.element = this.createHotspotElement(hotspot);
                this.hotspotContainer.appendChild(hotspot.element);
            } else if (!shouldShow && hotspot.element) {
                hotspot.element.remove();
                hotspot.element = null;
            }
        });
    }

    handleHotspotClick(hotspot) {
        if (hotspot.action) {
            hotspot.action();
        }
        
        this.recordInteraction('hotspot_click', hotspot.id);
        this.checkAchievements();
    }

    showHotspotTooltip(element, content) {
        const tooltip = document.createElement('div');
        tooltip.className = 'hotspot-tooltip';
        tooltip.textContent = content;
        
        const rect = element.getBoundingClientRect();
        tooltip.style.left = `${rect.left + 50}px`;
        tooltip.style.top = `${rect.top - 40}px`;
        tooltip.style.display = 'block';
        
        document.body.appendChild(tooltip);
        this.currentTooltip = tooltip;
    }

    hideHotspotTooltip() {
        if (this.currentTooltip) {
            this.currentTooltip.remove();
            this.currentTooltip = null;
        }
    }

    // Branching System
    addBranchingPoint(time, question, options) {
        const branchPoint = {
            time,
            question,
            options,
            triggered: false
        };
        
        if (!this.branchingData.scenes[this.currentScene]) {
            this.branchingData.scenes[this.currentScene] = {
                branches: []
            };
        }
        
        this.branchingData.scenes[this.currentScene].branches.push(branchPoint);
    }

    checkBranchingPoints() {
        const currentTime = this.video.currentTime;
        const scene = this.branchingData.scenes[this.currentScene];
        
        if (!scene) return;
        
        scene.branches.forEach(branch => {
            if (!branch.triggered && Math.abs(currentTime - branch.time) < 0.5) {
                this.showDecisionOverlay(branch);
                branch.triggered = true;
            }
        });
    }

    showDecisionOverlay(branch) {
        this.video.pause();
        
        this.decisionOverlay.innerHTML = `
            <div class="decision-box">
                <h3>${branch.question}</h3>
                <div class="decision-options">
                    ${branch.options.map((option, index) => 
                        `<button class="decision-btn" onclick="interactivePlayer.makeDecision(${index}, '${branch.question}')">${option.text}</button>`
                    ).join('')}
                </div>
            </div>
        `;
        
        this.decisionOverlay.style.display = 'flex';
    }

    makeDecision(optionIndex, question) {
        const scene = this.branchingData.scenes[this.currentScene];
        const branch = scene.branches.find(b => b.question === question);
        const selectedOption = branch.options[optionIndex];
        
        this.userProgress.decisions.push({
            scene: this.currentScene,
            question,
            choice: selectedOption.text,
            timestamp: Date.now()
        });
        
        this.decisionOverlay.style.display = 'none';
        
        if (selectedOption.action) {
            selectedOption.action();
        }
        
        if (selectedOption.nextScene) {
            this.loadScene(selectedOption.nextScene);
        } else {
            this.video.play();
        }
        
        this.recordInteraction('decision_made', optionIndex);
        this.checkAchievements();
    }

    // Gamification
    recordInteraction(type, data) {
        const interaction = {
            type,
            data,
            timestamp: Date.now(),
            scene: this.currentScene
        };
        
        if (!this.userProgress.interactions) {
            this.userProgress.interactions = [];
        }
        
        this.userProgress.interactions.push(interaction);
        this.saveUserProgress();
    }

    checkAchievements() {
        this.achievements.forEach(achievement => {
            if (this.userProgress.achievements.includes(achievement.id)) return;
            
            let unlocked = false;
            
            switch (achievement.id) {
                case 'first_interaction':
                    unlocked = this.userProgress.interactions && this.userProgress.interactions.length >= 1;
                    break;
                case 'decision_maker':
                    unlocked = this.userProgress.decisions.length >= 5;
                    break;
                case 'explorer':
                    unlocked = this.countHotspotsFound() >= 3;
                    break;
                case 'wisdom_seeker':
                    unlocked = this.userProgress.completedScenes.length >= 5;
                    break;
            }
            
            if (unlocked) {
                this.unlockAchievement(achievement);
            }
        });
    }

    unlockAchievement(achievement) {
        this.userProgress.achievements.push(achievement.id);
        this.showAchievementNotification(achievement);
        this.updateAchievementPanel();
        this.saveUserProgress();
    }

    showAchievementNotification(achievement) {
        const notification = document.createElement('div');
        notification.className = 'achievement-notification';
        notification.innerHTML = `
            <div class="achievement-content">
                <span class="achievement-icon">${achievement.icon}</span>
                <div class="achievement-text">
                    <h4>Achievement Unlocked!</h4>
                    <p>${achievement.name}: ${achievement.description}</p>
                </div>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    updateAchievementPanel() {
        const panel = document.getElementById('achievement-panel');
        if (!panel) return;
        
        const achievementHTML = this.achievements.map(achievement => {
            const unlocked = this.userProgress.achievements.includes(achievement.id);
            return `
                <div class="achievement-item ${unlocked ? 'unlocked' : 'locked'}">
                    <span class="achievement-icon">${achievement.icon}</span>
                    <div class="achievement-info">
                        <h4>${achievement.name}</h4>
                        <p>${achievement.description}</p>
                    </div>
                </div>
            `;
        }).join('');
        
        panel.innerHTML = `
            <h3>Achievements</h3>
            <div class="achievement-list">${achievementHTML}</div>
        `;
    }

    // Utility Methods
    loadScene(sceneId) {
        this.currentScene = sceneId;
        // Implementation for loading different video scenes
        this.userProgress.completedScenes.push(sceneId);
        this.checkAchievements();
    }

    loadUserProgress() {
        const saved = localStorage.getItem('interactiveVideoProgress');
        if (saved) {
            this.userProgress = { ...this.userProgress, ...JSON.parse(saved) };
        }
    }

    saveUserProgress() {
        localStorage.setItem('interactiveVideoProgress', JSON.stringify(this.userProgress));
    }

    countHotspotsFound() {
        if (!this.userProgress.interactions) return 0;
        return this.userProgress.interactions.filter(i => i.type === 'hotspot_click').length;
    }

    resetHotspots() {
        this.hotspots.forEach(hotspot => {
            if (hotspot.element) {
                hotspot.element.remove();
                hotspot.element = null;
            }
        });
    }

    toggleHotspots() {
        this.options.enableHotspots = !this.options.enableHotspots;
        this.hotspotContainer.style.display = this.options.enableHotspots ? 'block' : 'none';
    }

    toggleChat() {
        const chatPanel = document.getElementById('chat-panel');
        chatPanel.style.display = chatPanel.style.display === 'none' ? 'block' : 'none';
    }

    toggleAchievements() {
        const achievementPanel = document.getElementById('achievement-panel');
        achievementPanel.style.display = achievementPanel.style.display === 'none' ? 'block' : 'none';
    }

    handleVideoEnd() {
        this.recordInteraction('video_completed', this.currentScene);
        this.checkAchievements();
    }
}

// Global instance for easy access
let interactivePlayer = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('interactive-video-player')) {
        interactivePlayer = new InteractiveVideoPlayer('interactive-video-player');
    }
});