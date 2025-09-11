/**
 * Video Processing API Client
 * Handles communication with edge computing video processing backend
 */

const API_BASE_URL = '/api';

class VideoProcessingAPI {
    constructor() {
        this.baseURL = API_BASE_URL;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Handle blob responses (for file downloads)
            if (options.responseType === 'blob') {
                return await response.blob();
            }

            return await response.json();
        } catch (error) {
            console.error(`API request failed: ${endpoint}`, error);
            throw error;
        }
    }

    // Edge Computing API
    async getEdgeNodes() {
        return this.request('/edge/nodes');
    }

    async registerEdgeNode(nodeConfig) {
        return this.request('/edge/nodes/register', {
            method: 'POST',
            body: JSON.stringify(nodeConfig),
        });
    }

    async getAvailableNodes(requirements = {}) {
        const params = new URLSearchParams(requirements);
        return this.request(`/edge/nodes/available?${params}`);
    }

    async selectOptimalNode(requirements = {}) {
        return this.request('/edge/nodes/select', {
            method: 'POST',
            body: JSON.stringify({ requirements }),
        });
    }

    async getClusterStatus() {
        return this.request('/edge/cluster/status');
    }

    async sendHeartbeat(nodeId, status = 'online') {
        return this.request(`/edge/nodes/${nodeId}/heartbeat`, {
            method: 'POST',
            body: JSON.stringify({ status }),
        });
    }

    // Video Processing API
    async uploadVideo(file) {
        const formData = new FormData();
        formData.append('file', file);

        return this.request('/video/upload', {
            method: 'POST',
            headers: {}, // Remove Content-Type to let browser set boundary
            body: formData,
        });
    }

    async startProcessing(config) {
        return this.request('/video/process', {
            method: 'POST',
            body: JSON.stringify(config),
        });
    }

    async getTaskStatus(taskId) {
        return this.request(`/video/tasks/${taskId}/status`);
    }

    async cancelTask(taskId) {
        return this.request(`/video/tasks/${taskId}/cancel`, {
            method: 'POST',
        });
    }

    async getTasks() {
        return this.request('/video/tasks');
    }

    async downloadResult(taskId) {
        return this.request(`/video/download/${taskId}`, {
            responseType: 'blob',
        });
    }

    async getProcessingPresets() {
        return this.request('/video/presets');
    }

    async getSupportedFormats() {
        return this.request('/video/formats');
    }

    async getGpuStatus() {
        return this.request('/video/gpu/status');
    }

    async cleanupTasks(maxAgeHours = 24) {
        return this.request('/video/cleanup', {
            method: 'POST',
            body: JSON.stringify({ max_age_hours: maxAgeHours }),
        });
    }

    // Collaborative Editing API
    async createCollaborativeSession(config) {
        return this.request('/collaborative/sessions', {
            method: 'POST',
            body: JSON.stringify(config),
        });
    }

    async joinCollaborativeSession(sessionId, userInfo) {
        return this.request(`/collaborative/sessions/${sessionId}/join`, {
            method: 'POST',
            body: JSON.stringify(userInfo),
        });
    }

    async leaveCollaborativeSession(sessionId, userId) {
        return this.request(`/collaborative/sessions/${sessionId}/leave`, {
            method: 'POST',
            body: JSON.stringify({ user_id: userId }),
        });
    }

    async applyEditOperation(sessionId, operation) {
        return this.request(`/collaborative/sessions/${sessionId}/operations`, {
            method: 'POST',
            body: JSON.stringify(operation),
        });
    }

    async lockRegion(sessionId, lockInfo) {
        return this.request(`/collaborative/sessions/${sessionId}/lock`, {
            method: 'POST',
            body: JSON.stringify(lockInfo),
        });
    }

    async unlockRegion(sessionId, regionId, userId) {
        return this.request(`/collaborative/sessions/${sessionId}/unlock/${regionId}`, {
            method: 'POST',
            body: JSON.stringify({ user_id: userId }),
        });
    }

    async getSessionState(sessionId) {
        return this.request(`/collaborative/sessions/${sessionId}/state`);
    }

    async listCollaborativeSessions() {
        return this.request('/collaborative/sessions');
    }

    // Edge AI Inference API (to be implemented)
    async runAIInference(modelName, inputData, parameters = {}) {
        return this.request('/ai/inference', {
            method: 'POST',
            body: JSON.stringify({
                model_name: modelName,
                input_data: inputData,
                parameters,
            }),
        });
    }

    async getAvailableAIModels() {
        return this.request('/ai/models');
    }

    async getInferenceTaskStatus(taskId) {
        return this.request(`/ai/tasks/${taskId}/status`);
    }

    // P2P Streaming API (to be implemented)
    async initializeP2P(displayName) {
        return this.request('/p2p/initialize', {
            method: 'POST',
            body: JSON.stringify({ display_name: displayName }),
        });
    }

    async shareVideo(videoConfig) {
        return this.request('/p2p/share', {
            method: 'POST',
            body: JSON.stringify(videoConfig),
        });
    }

    async getAvailableVideos() {
        return this.request('/p2p/videos');
    }

    async startVideoStream(shareId, viewerPeerId, quality = 'medium') {
        return this.request('/p2p/stream/start', {
            method: 'POST',
            body: JSON.stringify({
                share_id: shareId,
                viewer_peer_id: viewerPeerId,
                quality,
            }),
        });
    }

    async requestVideoDownload(shareId, peerId) {
        return this.request('/p2p/download/request', {
            method: 'POST',
            body: JSON.stringify({
                share_id: shareId,
                peer_id: peerId,
            }),
        });
    }

    async getP2PNetworkStats() {
        return this.request('/p2p/network/stats');
    }

    // Offline Sync API (to be implemented)
    async createOfflineProject(projectConfig) {
        return this.request('/offline/projects', {
            method: 'POST',
            body: JSON.stringify(projectConfig),
        });
    }

    async addOfflineOperation(projectId, operation) {
        return this.request(`/offline/projects/${projectId}/operations`, {
            method: 'POST',
            body: JSON.stringify(operation),
        });
    }

    async syncWithServer() {
        return this.request('/offline/sync', {
            method: 'POST',
        });
    }

    async getOfflineProjects() {
        return this.request('/offline/projects');
    }

    async getOfflineProjectStatus(projectId) {
        return this.request(`/offline/projects/${projectId}/status`);
    }

    // Utility methods
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    formatDuration(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = Math.floor(seconds % 60);
        
        if (hours > 0) {
            return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        } else {
            return `${minutes}:${secs.toString().padStart(2, '0')}`;
        }
    }

    // WebSocket connection for real-time updates
    connectToUpdates(callbacks = {}) {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/updates`;
        
        const ws = new WebSocket(wsUrl);
        
        ws.onopen = () => {
            console.log('WebSocket connected');
            if (callbacks.onConnect) callbacks.onConnect();
        };
        
        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                
                switch (data.type) {
                    case 'task_update':
                        if (callbacks.onTaskUpdate) callbacks.onTaskUpdate(data.payload);
                        break;
                    case 'node_update':
                        if (callbacks.onNodeUpdate) callbacks.onNodeUpdate(data.payload);
                        break;
                    case 'collaboration_update':
                        if (callbacks.onCollaborationUpdate) callbacks.onCollaborationUpdate(data.payload);
                        break;
                    default:
                        console.log('Unknown WebSocket message type:', data.type);
                }
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };
        
        ws.onclose = (event) => {
            console.log('WebSocket disconnected:', event.code, event.reason);
            if (callbacks.onDisconnect) callbacks.onDisconnect(event);
            
            // Attempt to reconnect after 5 seconds
            if (!event.wasClean) {
                setTimeout(() => {
                    console.log('Attempting to reconnect WebSocket...');
                    this.connectToUpdates(callbacks);
                }, 5000);
            }
        };
        
        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            if (callbacks.onError) callbacks.onError(error);
        };
        
        return ws;
    }
}

// Create and export a singleton instance
export const videoProcessingAPI = new VideoProcessingAPI();
export default VideoProcessingAPI;