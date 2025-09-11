/**
 * Live Streaming and Real-time Chat Integration
 * Uses Socket.IO for real-time communication
 */

class LiveStreamingManager {
    constructor(videoPlayer) {
        this.videoPlayer = videoPlayer;
        this.socket = null;
        this.isLive = false;
        this.viewerCount = 0;
        this.chatMessages = [];
        this.streamUrl = null;
        
        this.init();
    }

    init() {
        this.setupSocketConnection();
        this.setupChatSystem();
        this.setupStreamingControls();
    }

    setupSocketConnection() {
        // Initialize Socket.IO connection
        if (typeof io !== 'undefined') {
            this.socket = io();
            
            this.socket.on('connect', () => {
                console.log('Connected to streaming server');
                this.joinStreamingRoom();
            });
            
            this.socket.on('viewer_count_update', (count) => {
                this.updateViewerCount(count);
            });
            
            this.socket.on('chat_message', (message) => {
                this.addChatMessage(message);
            });
            
            this.socket.on('stream_status', (status) => {
                this.updateStreamStatus(status);
            });
            
            this.socket.on('interactive_event', (event) => {
                this.handleInteractiveEvent(event);
            });
        }
    }

    setupChatSystem() {
        const chatPanel = document.getElementById('chat-panel');
        if (!chatPanel) return;
        
        chatPanel.innerHTML = `
            <h3>Live Chat</h3>
            <div class="chat-messages" id="chat-messages"></div>
            <div class="chat-input-container">
                <input type="text" 
                       id="chat-input" 
                       class="chat-input" 
                       placeholder="Type your message..."
                       maxlength="200">
                <button id="chat-send" class="chat-send">Send</button>
            </div>
            <div class="chat-controls">
                <button id="toggle-emoji" class="chat-control-btn">😊</button>
                <button id="toggle-voice-chat" class="chat-control-btn">🎤</button>
            </div>
        `;
        
        this.setupChatEvents();
    }

    setupChatEvents() {
        const chatInput = document.getElementById('chat-input');
        const chatSend = document.getElementById('chat-send');
        
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendChatMessage();
            }
        });
        
        chatSend.addEventListener('click', () => {
            this.sendChatMessage();
        });
    }

    setupStreamingControls() {
        const videoContainer = this.videoPlayer.container.querySelector('.video-container');
        
        const streamingControls = document.createElement('div');
        streamingControls.className = 'streaming-controls';
        streamingControls.innerHTML = `
            <div class="live-indicator" id="live-indicator" style="display: none;">
                LIVE
            </div>
            <div class="viewer-count" id="viewer-count" style="display: none;">
                👥 0 viewers
            </div>
            <div class="stream-quality-selector">
                <select id="quality-selector">
                    <option value="720p">720p</option>
                    <option value="1080p">1080p</option>
                    <option value="auto">Auto</option>
                </select>
            </div>
        `;
        
        videoContainer.appendChild(streamingControls);
    }

    joinStreamingRoom() {
        if (this.socket) {
            this.socket.emit('join_stream', {
                userId: this.generateUserId(),
                userAgent: navigator.userAgent
            });
        }
    }

    sendChatMessage() {
        const chatInput = document.getElementById('chat-input');
        const message = chatInput.value.trim();
        
        if (!message) return;
        
        const chatMessage = {
            id: Date.now(),
            userId: this.generateUserId(),
            username: this.getUsername(),
            message: message,
            timestamp: new Date().toISOString(),
            type: 'user'
        };
        
        if (this.socket) {
            this.socket.emit('chat_message', chatMessage);
        }
        
        chatInput.value = '';
    }

    addChatMessage(message) {
        const chatMessages = document.getElementById('chat-messages');
        if (!chatMessages) return;
        
        const messageElement = document.createElement('div');
        messageElement.className = `chat-message ${message.type}`;
        
        const time = new Date(message.timestamp).toLocaleTimeString();
        
        messageElement.innerHTML = `
            <div class="message-header">
                <span class="username">${message.username}</span>
                <span class="timestamp">${time}</span>
            </div>
            <div class="message-content">${this.sanitizeMessage(message.message)}</div>
        `;
        
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Add message to local array
        this.chatMessages.push(message);
        
        // Limit chat messages to prevent memory issues
        if (this.chatMessages.length > 100) {
            this.chatMessages.shift();
            const firstMessage = chatMessages.firstChild;
            if (firstMessage) {
                firstMessage.remove();
            }
        }
    }

    updateViewerCount(count) {
        this.viewerCount = count;
        const viewerCountElement = document.getElementById('viewer-count');
        if (viewerCountElement) {
            viewerCountElement.textContent = `👥 ${count} viewers`;
            viewerCountElement.style.display = this.isLive ? 'block' : 'none';
        }
    }

    updateStreamStatus(status) {
        this.isLive = status.isLive;
        const liveIndicator = document.getElementById('live-indicator');
        
        if (liveIndicator) {
            liveIndicator.style.display = this.isLive ? 'block' : 'none';
        }
        
        if (this.isLive && status.streamUrl) {
            this.streamUrl = status.streamUrl;
            this.switchToLiveStream();
        }
    }

    switchToLiveStream() {
        if (this.streamUrl && this.videoPlayer.video) {
            this.videoPlayer.video.src = this.streamUrl;
            this.videoPlayer.video.load();
            
            // Add system message to chat
            this.addChatMessage({
                id: Date.now(),
                username: 'System',
                message: 'Switched to live stream',
                timestamp: new Date().toISOString(),
                type: 'system'
            });
        }
    }

    handleInteractiveEvent(event) {
        switch (event.type) {
            case 'poll_start':
                this.showPoll(event.data);
                break;
            case 'shared_hotspot':
                this.addSharedHotspot(event.data);
                break;
            case 'instructor_message':
                this.showInstructorMessage(event.data);
                break;
        }
    }

    showPoll(pollData) {
        const pollOverlay = document.createElement('div');
        pollOverlay.className = 'poll-overlay';
        pollOverlay.innerHTML = `
            <div class="poll-container">
                <h3>${pollData.question}</h3>
                <div class="poll-options">
                    ${pollData.options.map((option, index) => `
                        <button class="poll-option" data-option="${index}">
                            ${option}
                        </button>
                    `).join('')}
                </div>
                <div class="poll-timer">Time remaining: <span id="poll-timer">${pollData.duration || 30}</span>s</div>
            </div>
        `;
        
        document.body.appendChild(pollOverlay);
        
        // Add event listeners to poll options
        pollOverlay.querySelectorAll('.poll-option').forEach(button => {
            button.addEventListener('click', (e) => {
                this.submitPollVote(pollData.id, parseInt(e.target.dataset.option));
                pollOverlay.remove();
            });
        });
        
        // Start countdown timer
        this.startPollTimer(pollData.duration || 30, pollOverlay);
    }

    submitPollVote(pollId, optionIndex) {
        if (this.socket) {
            this.socket.emit('poll_vote', {
                pollId,
                optionIndex,
                userId: this.generateUserId()
            });
        }
    }

    startPollTimer(duration, pollOverlay) {
        let timeLeft = duration;
        const timerElement = pollOverlay.querySelector('#poll-timer');
        
        const timer = setInterval(() => {
            timeLeft--;
            if (timerElement) {
                timerElement.textContent = timeLeft;
            }
            
            if (timeLeft <= 0) {
                clearInterval(timer);
                pollOverlay.remove();
            }
        }, 1000);
    }

    addSharedHotspot(hotspotData) {
        if (this.videoPlayer.addHotspot) {
            this.videoPlayer.addHotspot(
                hotspotData.timeStart,
                hotspotData.timeEnd,
                hotspotData.x,
                hotspotData.y,
                hotspotData.content,
                () => {
                    this.addChatMessage({
                        id: Date.now(),
                        username: 'Instructor',
                        message: hotspotData.message || 'Check out this interactive element!',
                        timestamp: new Date().toISOString(),
                        type: 'system'
                    });
                }
            );
        }
    }

    showInstructorMessage(messageData) {
        const instructorOverlay = document.createElement('div');
        instructorOverlay.className = 'instructor-message-overlay';
        instructorOverlay.innerHTML = `
            <div class="instructor-message">
                <div class="instructor-avatar">👨‍🏫</div>
                <div class="instructor-content">
                    <h4>Instructor Message</h4>
                    <p>${messageData.message}</p>
                </div>
                <button class="close-instructor-message">×</button>
            </div>
        `;
        
        document.body.appendChild(instructorOverlay);
        
        instructorOverlay.querySelector('.close-instructor-message').addEventListener('click', () => {
            instructorOverlay.remove();
        });
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (instructorOverlay.parentNode) {
                instructorOverlay.remove();
            }
        }, 10000);
    }

    generateUserId() {
        let userId = localStorage.getItem('streaming_user_id');
        if (!userId) {
            userId = 'user_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('streaming_user_id', userId);
        }
        return userId;
    }

    getUsername() {
        let username = localStorage.getItem('streaming_username');
        if (!username) {
            username = 'Guest_' + Math.random().toString(36).substr(2, 5);
            localStorage.setItem('streaming_username', username);
        }
        return username;
    }

    sanitizeMessage(message) {
        // Basic HTML sanitization
        const div = document.createElement('div');
        div.textContent = message;
        return div.innerHTML;
    }

    // Stream quality management
    changeStreamQuality(quality) {
        if (this.socket) {
            this.socket.emit('change_quality', {
                quality,
                userId: this.generateUserId()
            });
        }
    }

    // Moderator controls (if user has permissions)
    banUser(userId) {
        if (this.socket) {
            this.socket.emit('ban_user', { userId });
        }
    }

    clearChat() {
        const chatMessages = document.getElementById('chat-messages');
        if (chatMessages) {
            chatMessages.innerHTML = '';
        }
        this.chatMessages = [];
    }

    // Voice chat integration
    setupVoiceChat() {
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                this.voiceStream = stream;
                // Implement voice chat using WebRTC
                this.setupWebRTCConnection();
            })
            .catch(err => {
                console.error('Voice chat not available:', err);
            });
    }

    setupWebRTCConnection() {
        // Basic WebRTC setup for voice chat
        this.peerConnection = new RTCPeerConnection({
            iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
        });
        
        if (this.voiceStream) {
            this.voiceStream.getTracks().forEach(track => {
                this.peerConnection.addTrack(track, this.voiceStream);
            });
        }
        
        this.peerConnection.onicecandidate = (event) => {
            if (event.candidate && this.socket) {
                this.socket.emit('ice_candidate', event.candidate);
            }
        };
        
        this.peerConnection.ontrack = (event) => {
            const remoteAudio = document.createElement('audio');
            remoteAudio.srcObject = event.streams[0];
            remoteAudio.autoplay = true;
            document.body.appendChild(remoteAudio);
        };
    }

    // Screen sharing for instructor
    startScreenShare() {
        navigator.mediaDevices.getDisplayMedia({ video: true, audio: true })
            .then(stream => {
                // Replace video source with screen share
                this.videoPlayer.video.srcObject = stream;
                
                if (this.socket) {
                    this.socket.emit('start_screen_share', {
                        userId: this.generateUserId()
                    });
                }
            })
            .catch(err => {
                console.error('Screen sharing not available:', err);
            });
    }

    stopScreenShare() {
        if (this.videoPlayer.video.srcObject) {
            this.videoPlayer.video.srcObject.getTracks().forEach(track => track.stop());
            this.videoPlayer.video.srcObject = null;
        }
        
        if (this.socket) {
            this.socket.emit('stop_screen_share', {
                userId: this.generateUserId()
            });
        }
    }
}

// Export for use with the main video player
window.LiveStreamingManager = LiveStreamingManager;