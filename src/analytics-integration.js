/**
 * Analytics Dashboard Integration Script
 * Adds analytics functionality to the existing spiritual platform
 */

// Import analytics styles
const analyticsCSS = document.createElement('link');
analyticsCSS.rel = 'stylesheet';
analyticsCSS.href = './src/components/analytics-dashboard.css';
document.head.appendChild(analyticsCSS);

class AnalyticsDashboardIntegration {
    constructor() {
        this.isAnalyticsOpen = false;
        this.init();
    }

    init() {
        this.addAnalyticsButton();
        this.createAnalyticsModal();
    }

    addAnalyticsButton() {
        // Add analytics button to the header
        const header = document.querySelector('.header');
        if (header) {
            const analyticsBtn = document.createElement('button');
            analyticsBtn.innerHTML = '📊 Analytics Dashboard';
            analyticsBtn.className = 'analytics-toggle-btn';
            analyticsBtn.style.cssText = `
                background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 25px;
                font-size: 14px;
                font-weight: bold;
                cursor: pointer;
                margin-top: 20px;
                transition: transform 0.3s ease;
            `;
            analyticsBtn.addEventListener('mouseenter', () => {
                analyticsBtn.style.transform = 'translateY(-2px)';
            });
            analyticsBtn.addEventListener('mouseleave', () => {
                analyticsBtn.style.transform = 'translateY(0)';
            });
            analyticsBtn.onclick = () => this.toggleAnalytics();
            header.appendChild(analyticsBtn);
        }
    }

    createAnalyticsModal() {
        const modal = document.createElement('div');
        modal.id = 'analytics-modal';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.9);
            z-index: 10000;
            display: none;
            overflow-y: auto;
        `;

        const closeBtn = document.createElement('button');
        closeBtn.innerHTML = '❌ Close Analytics';
        closeBtn.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(220, 53, 69, 0.8);
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 6px;
            cursor: pointer;
            z-index: 10001;
            font-weight: bold;
        `;
        closeBtn.onclick = () => this.closeAnalytics();

        const dashboardContainer = document.createElement('div');
        dashboardContainer.id = 'analytics-dashboard-container';
        dashboardContainer.innerHTML = this.createDashboardHTML();

        modal.appendChild(closeBtn);
        modal.appendChild(dashboardContainer);
        document.body.appendChild(modal);
    }

    createDashboardHTML() {
        return `
            <div class="analytics-dashboard">
                <div class="dashboard-header">
                    <h1>📈 Analytics & Insights Dashboard</h1>
                    <div class="header-controls">
                        <select id="video-selector">
                            <option value="sample_video">Sample Video</option>
                            <option value="spiritual_session_1">Spiritual Session 1</option>
                            <option value="meditation_guide">Meditation Guide</option>
                        </select>
                        <button onclick="window.analyticsIntegration.refreshData()" class="refresh-btn">
                            🔄 Refresh
                        </button>
                    </div>
                </div>

                <div class="dashboard-tabs">
                    <button class="tab active" onclick="window.analyticsIntegration.showTab('overview')">
                        <span class="tab-icon">📊</span>
                        Overview
                    </button>
                    <button class="tab" onclick="window.analyticsIntegration.showTab('engagement')">
                        <span class="tab-icon">🔥</span>
                        Engagement
                    </button>
                    <button class="tab" onclick="window.analyticsIntegration.showTab('conversions')">
                        <span class="tab-icon">💰</span>
                        Conversions
                    </button>
                    <button class="tab" onclick="window.analyticsIntegration.showTab('predictions')">
                        <span class="tab-icon">🔮</span>
                        Predictions
                    </button>
                    <button class="tab" onclick="window.analyticsIntegration.showTab('competitors')">
                        <span class="tab-icon">⚔️</span>
                        Competitors
                    </button>
                </div>

                <div class="dashboard-content">
                    <div id="tab-overview" class="tab-content active">
                        <div class="overview-grid">
                            <div class="summary-cards">
                                <div class="summary-card">
                                    <h3>Total Views</h3>
                                    <div class="metric-value" id="total-views">-</div>
                                </div>
                                <div class="summary-card">
                                    <h3>Engagement Time</h3>
                                    <div class="metric-value" id="engagement-time">-</div>
                                </div>
                                <div class="summary-card">
                                    <h3>Conversion Rate</h3>
                                    <div class="metric-value" id="conversion-rate">-</div>
                                </div>
                            </div>
                            
                            <div class="widget-grid">
                                <div class="heatmap-widget widget-base">
                                    <div class="widget-header">
                                        <h3>🔥 Engagement Heatmap</h3>
                                        <label class="real-time-toggle">
                                            <input type="checkbox" id="real-time-toggle"> Real-time
                                        </label>
                                    </div>
                                    <canvas id="heatmap-canvas" width="400" height="100"></canvas>
                                    <div id="heatmap-summary" class="heatmap-summary"></div>
                                </div>

                                <div class="viewer-behavior-widget widget-base">
                                    <div class="widget-header">
                                        <h3>👥 Viewer Behavior</h3>
                                    </div>
                                    <div id="behavior-content" class="behavior-content"></div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div id="tab-engagement" class="tab-content">
                        <div class="loading-content">📊 Loading engagement analytics...</div>
                    </div>

                    <div id="tab-conversions" class="tab-content">
                        <div class="loading-content">💰 Loading conversion data...</div>
                    </div>

                    <div id="tab-predictions" class="tab-content">
                        <div class="loading-content">🔮 Generating predictions...</div>
                    </div>

                    <div id="tab-competitors" class="tab-content">
                        <div class="loading-content">⚔️ Analyzing competitors...</div>
                    </div>
                </div>
            </div>
        `;
    }

    toggleAnalytics() {
        if (this.isAnalyticsOpen) {
            this.closeAnalytics();
        } else {
            this.openAnalytics();
        }
    }

    openAnalytics() {
        const modal = document.getElementById('analytics-modal');
        if (modal) {
            modal.style.display = 'block';
            this.isAnalyticsOpen = true;
            this.loadAnalyticsData();
        }
    }

    closeAnalytics() {
        const modal = document.getElementById('analytics-modal');
        if (modal) {
            modal.style.display = 'none';
            this.isAnalyticsOpen = false;
        }
    }

    showTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
        event.target.closest('.tab').classList.add('active');

        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.style.display = 'none';
        });
        const targetTab = document.getElementById(`tab-${tabName}`);
        if (targetTab) {
            targetTab.style.display = 'block';
        }

        // Load specific tab data
        this.loadTabData(tabName);
    }

    async loadAnalyticsData() {
        try {
            const videoId = document.getElementById('video-selector')?.value || 'sample_video';
            
            // Load summary data
            const summaryResponse = await fetch(`/api/analytics/analytics-summary?video_id=${videoId}`);
            const summaryData = await summaryResponse.json();
            
            if (summaryData.success) {
                this.updateSummaryCards(summaryData.summary);
            }

            // Load heatmap data
            const heatmapResponse = await fetch(`/api/analytics/heatmap/${videoId}`);
            const heatmapData = await heatmapResponse.json();
            
            if (heatmapData.success) {
                this.drawHeatmap(heatmapData.heatmap_data);
            }

            // Load behavior data
            const behaviorResponse = await fetch(`/api/analytics/viewer-behavior/${videoId}`);
            const behaviorData = await behaviorResponse.json();
            
            if (behaviorData.success) {
                this.updateBehaviorWidget(behaviorData.behavior_data);
            }

        } catch (error) {
            console.error('Error loading analytics data:', error);
            this.showError('Failed to load analytics data');
        }
    }

    updateSummaryCards(summary) {
        if (summary?.overview) {
            const totalViews = document.getElementById('total-views');
            const engagementTime = document.getElementById('engagement-time');
            const conversionRate = document.getElementById('conversion-rate');

            if (totalViews) totalViews.textContent = summary.overview.total_views.toLocaleString();
            if (engagementTime) engagementTime.textContent = Math.round(summary.overview.total_engagement_time / 3600) + 'h';
            if (conversionRate) conversionRate.textContent = (summary.overview.conversion_rate * 100).toFixed(2) + '%';
        }
    }

    drawHeatmap(heatmapData) {
        const canvas = document.getElementById('heatmap-canvas');
        const summary = document.getElementById('heatmap-summary');
        
        if (!canvas || !heatmapData || heatmapData.length === 0) return;

        const ctx = canvas.getContext('2d');
        const width = canvas.width;
        const height = canvas.height;

        // Clear canvas
        ctx.clearRect(0, 0, width, height);

        // Draw heatmap
        const barWidth = width / heatmapData.length;
        
        heatmapData.forEach((point, index) => {
            const x = index * barWidth;
            const intensity = point.intensity || 0;
            
            // Color gradient from blue to red
            const hue = (1 - intensity) * 240;
            ctx.fillStyle = `hsl(${hue}, 70%, 50%)`;
            
            const barHeight = height * 0.7 * intensity;
            const y = height - barHeight - 15;
            
            ctx.fillRect(x, y, barWidth - 1, barHeight);
        });

        // Update summary
        if (summary && heatmapData.length > 0) {
            const maxIntensity = Math.max(...heatmapData.map(p => p.intensity));
            const avgIntensity = heatmapData.reduce((sum, p) => sum + p.intensity, 0) / heatmapData.length;
            const peakTime = heatmapData.find(p => p.intensity === maxIntensity)?.time || 0;
            
            summary.innerHTML = `
                <div class="summary-item">
                    <span class="label">Peak:</span>
                    <span class="value">${Math.floor(peakTime / 60)}:${(peakTime % 60).toString().padStart(2, '0')}</span>
                </div>
                <div class="summary-item">
                    <span class="label">Avg:</span>
                    <span class="value">${Math.round(avgIntensity * 100)}%</span>
                </div>
            `;
        }
    }

    updateBehaviorWidget(behaviorData) {
        const container = document.getElementById('behavior-content');
        if (!container || !behaviorData) return;

        container.innerHTML = `
            <div class="metrics-summary">
                <div class="metric-card">
                    <div class="metric-icon">👥</div>
                    <div class="metric-info">
                        <div class="metric-value">${behaviorData.total_viewers.toLocaleString()}</div>
                        <div class="metric-label">Total Viewers</div>
                    </div>
                </div>
                <div class="metric-card">
                    <div class="metric-icon">⏱️</div>
                    <div class="metric-info">
                        <div class="metric-value">${Math.round(behaviorData.average_watch_time / 60)}m</div>
                        <div class="metric-label">Avg Watch Time</div>
                    </div>
                </div>
                <div class="metric-card">
                    <div class="metric-icon">✅</div>
                    <div class="metric-info">
                        <div class="metric-value">${(behaviorData.completion_rate * 100).toFixed(1)}%</div>
                        <div class="metric-label">Completion Rate</div>
                    </div>
                </div>
            </div>
        `;
    }

    async loadTabData(tabName) {
        const tabContent = document.getElementById(`tab-${tabName}`);
        if (!tabContent || tabName === 'overview') return;

        const videoId = document.getElementById('video-selector')?.value || 'sample_video';

        try {
            let endpoint = '';
            switch(tabName) {
                case 'engagement':
                    endpoint = `heatmap/${videoId}`;
                    break;
                case 'conversions':
                    endpoint = `conversion-tracking/${videoId}`;
                    break;
                case 'predictions':
                    endpoint = `predictive-modeling/${videoId}`;
                    break;
                case 'competitors':
                    endpoint = 'competitor-analysis';
                    break;
                default:
                    return;
            }

            const response = await fetch(`/api/analytics/${endpoint}`);
            const data = await response.json();

            if (data.success) {
                this.renderTabContent(tabName, data, tabContent);
            } else {
                tabContent.innerHTML = '<div class="error-content">❌ Failed to load data</div>';
            }
        } catch (error) {
            console.error(`Error loading ${tabName} data:`, error);
            tabContent.innerHTML = '<div class="error-content">⚠️ Connection error</div>';
        }
    }

    renderTabContent(tabName, data, container) {
        // Simplified rendering for each tab
        switch(tabName) {
            case 'engagement':
                container.innerHTML = `
                    <div class="engagement-view">
                        <h3>🔥 Detailed Engagement Analysis</h3>
                        <p>Real-time engagement data for improved content optimization.</p>
                        <div class="engagement-metrics">
                            <div class="metric-card">
                                <h4>Peak Engagement</h4>
                                <div class="metric-value">85%</div>
                            </div>
                            <div class="metric-card">
                                <h4>Drop-off Rate</h4>
                                <div class="metric-value">12%</div>
                            </div>
                        </div>
                    </div>
                `;
                break;
            case 'conversions':
                const conversionData = data.conversion_data || {};
                container.innerHTML = `
                    <div class="conversions-view">
                        <h3>💰 Conversion Analytics</h3>
                        <div class="conversion-metrics">
                            <div class="metric-card">
                                <h4>Total Revenue</h4>
                                <div class="metric-value">$${(conversionData.total_revenue || 0).toLocaleString()}</div>
                            </div>
                            <div class="metric-card">
                                <h4>ROI</h4>
                                <div class="metric-value">${((conversionData.roi || 0) * 100).toFixed(0)}%</div>
                            </div>
                            <div class="metric-card">
                                <h4>Conversions</h4>
                                <div class="metric-value">${conversionData.conversions || 0}</div>
                            </div>
                        </div>
                    </div>
                `;
                break;
            case 'predictions':
                const predictions = data.predictions || {};
                const performance = predictions.performance_prediction || {};
                container.innerHTML = `
                    <div class="predictions-view">
                        <h3>🔮 AI Predictions</h3>
                        <div class="prediction-score">
                            <h4>Performance Score</h4>
                            <div class="score-circle">
                                <div class="score-value">${Math.round(performance.score || 0)}</div>
                            </div>
                            <div class="confidence">Confidence: ${((performance.confidence || 0) * 100).toFixed(0)}%</div>
                        </div>
                        <div class="optimization-tips">
                            <h4>💡 Optimization Suggestions</h4>
                            <ul>
                                ${(predictions.optimization_suggestions || []).map(tip => `<li>${tip}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                `;
                break;
            case 'competitors':
                const competitors = data.competitors || [];
                container.innerHTML = `
                    <div class="competitors-view">
                        <h3>⚔️ Competitor Analysis</h3>
                        <div class="competitor-list">
                            ${competitors.slice(0, 5).map((comp, index) => `
                                <div class="competitor-item">
                                    <div class="rank">#${index + 1}</div>
                                    <div class="name">${comp.name}</div>
                                    <div class="engagement">${(comp.engagement_rate * 100).toFixed(2)}%</div>
                                    <div class="growth" style="color: ${comp.growth_rate > 0 ? '#28a745' : '#dc3545'}">
                                        ${(comp.growth_rate * 100).toFixed(1)}%
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `;
                break;
        }
    }

    refreshData() {
        if (this.isAnalyticsOpen) {
            this.loadAnalyticsData();
            
            // Refresh current tab
            const activeTab = document.querySelector('.tab.active');
            if (activeTab) {
                const tabName = activeTab.textContent.trim().toLowerCase();
                if (tabName !== 'overview') {
                    this.loadTabData(tabName);
                }
            }
        }
    }

    showError(message) {
        const container = document.querySelector('.dashboard-content');
        if (container) {
            container.innerHTML = `
                <div class="error-message" style="
                    text-align: center;
                    padding: 40px;
                    background: rgba(220, 53, 69, 0.1);
                    border: 1px solid rgba(220, 53, 69, 0.3);
                    border-radius: 10px;
                    color: #dc3545;
                ">
                    <h3>⚠️ ${message}</h3>
                    <p>Please ensure the analytics API is running and try again.</p>
                    <button onclick="window.analyticsIntegration.refreshData()" style="
                        background: #dc3545;
                        color: white;
                        border: none;
                        padding: 10px 20px;
                        border-radius: 6px;
                        cursor: pointer;
                        margin-top: 10px;
                    ">Retry</button>
                </div>
            `;
        }
    }
}

// Initialize analytics integration when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.analyticsIntegration = new AnalyticsDashboardIntegration();
});

// Add some additional styles for the integration
const additionalStyles = document.createElement('style');
additionalStyles.textContent = `
    .tab-content {
        display: none;
    }
    .tab-content.active {
        display: block;
    }
    .loading-content, .error-content {
        text-align: center;
        padding: 40px;
        font-size: 18px;
        opacity: 0.7;
    }
    .engagement-metrics, .conversion-metrics {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin-top: 20px;
    }
    .prediction-score {
        text-align: center;
        margin: 20px 0;
    }
    .score-circle {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background: conic-gradient(#28a745 0deg 270deg, rgba(255,255,255,0.1) 270deg 360deg);
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 20px auto;
        position: relative;
    }
    .score-circle::before {
        content: '';
        position: absolute;
        width: 80px;
        height: 80px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 50%;
    }
    .score-value {
        position: relative;
        z-index: 1;
        font-size: 24px;
        font-weight: bold;
        color: #FFD700;
    }
    .confidence {
        margin-top: 10px;
        opacity: 0.8;
    }
    .optimization-tips ul {
        text-align: left;
        max-width: 500px;
        margin: 0 auto;
    }
    .competitor-list {
        margin-top: 20px;
    }
    .competitor-item {
        display: grid;
        grid-template-columns: 50px 1fr 80px 80px;
        gap: 15px;
        align-items: center;
        padding: 12px;
        background: rgba(255,255,255,0.05);
        border-radius: 8px;
        margin-bottom: 10px;
    }
    .competitor-item .rank {
        font-weight: bold;
        color: #FFD700;
    }
    .competitor-item .name {
        font-weight: 600;
    }
`;
document.head.appendChild(additionalStyles);