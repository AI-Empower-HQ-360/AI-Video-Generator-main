/**
 * Main Analytics Dashboard Component
 * Provides comprehensive video analytics and insights
 */

import React, { useState, useEffect } from 'react';
import analyticsAPI from '../api/analytics-integration.js';
import HeatmapWidget from './HeatmapWidget.js';
import ViewerBehaviorWidget from './ViewerBehaviorWidget.js';
import ConversionWidget from './ConversionWidget.js';
import PredictiveWidget from './PredictiveWidget.js';
import CompetitorWidget from './CompetitorWidget.js';
import DashboardBuilder from './DashboardBuilder.js';

const AnalyticsDashboard = ({ videoId = 'sample_video' }) => {
  const [dashboardData, setDashboardData] = useState({
    heatmap: [],
    viewerBehavior: null,
    conversions: null,
    predictions: null,
    competitors: null,
    summary: null
  });
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [widgets, setWidgets] = useState([]);
  const [customMode, setCustomMode] = useState(false);

  useEffect(() => {
    loadAnalyticsData();
    loadWidgets();
  }, [videoId]);

  const loadAnalyticsData = async () => {
    setLoading(true);
    try {
      const [heatmap, behavior, conversions, predictions, competitors, summary] = await Promise.all([
        analyticsAPI.getVideoHeatmap(videoId),
        analyticsAPI.getViewerBehavior(videoId),
        analyticsAPI.getConversionMetrics(videoId),
        analyticsAPI.getPredictiveInsights(videoId),
        analyticsAPI.getCompetitorAnalysis(),
        analyticsAPI.getAnalyticsSummary(videoId)
      ]);

      setDashboardData({
        heatmap,
        viewerBehavior: behavior,
        conversions,
        predictions,
        competitors,
        summary
      });
    } catch (error) {
      console.error('Error loading analytics data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadWidgets = async () => {
    try {
      const availableWidgets = await analyticsAPI.getDashboardWidgets();
      setWidgets(availableWidgets);
    } catch (error) {
      console.error('Error loading widgets:', error);
    }
  };

  const refreshData = () => {
    loadAnalyticsData();
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'engagement', label: 'Engagement', icon: '🔥' },
    { id: 'conversions', label: 'Conversions', icon: '💰' },
    { id: 'predictions', label: 'Predictions', icon: '🔮' },
    { id: 'competitors', label: 'Competitors', icon: '⚔️' },
    { id: 'custom', label: 'Custom', icon: '🛠️' }
  ];

  if (loading) {
    return (
      <div className="analytics-dashboard loading">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading analytics data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="analytics-dashboard">
      <div className="dashboard-header">
        <h1>📈 Analytics & Insights Dashboard</h1>
        <div className="header-controls">
          <select onChange={(e) => setVideoId && setVideoId(e.target.value)}>
            <option value="sample_video">Sample Video</option>
            <option value="video_2">Video 2</option>
            <option value="video_3">Video 3</option>
          </select>
          <button onClick={refreshData} className="refresh-btn">
            🔄 Refresh
          </button>
        </div>
      </div>

      <div className="dashboard-tabs">
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`tab ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <span className="tab-icon">{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      <div className="dashboard-content">
        {activeTab === 'overview' && (
          <div className="overview-grid">
            <div className="summary-cards">
              {dashboardData.summary && (
                <>
                  <div className="summary-card">
                    <h3>Total Views</h3>
                    <div className="metric-value">{dashboardData.summary.overview.total_views.toLocaleString()}</div>
                  </div>
                  <div className="summary-card">
                    <h3>Engagement Time</h3>
                    <div className="metric-value">{Math.round(dashboardData.summary.overview.total_engagement_time / 3600)}h</div>
                  </div>
                  <div className="summary-card">
                    <h3>Conversion Rate</h3>
                    <div className="metric-value">{(dashboardData.summary.overview.conversion_rate * 100).toFixed(2)}%</div>
                  </div>
                </>
              )}
            </div>
            
            <div className="widget-grid">
              <HeatmapWidget data={dashboardData.heatmap} videoId={videoId} />
              <ViewerBehaviorWidget data={dashboardData.viewerBehavior} />
            </div>
          </div>
        )}

        {activeTab === 'engagement' && (
          <div className="engagement-view">
            <HeatmapWidget data={dashboardData.heatmap} videoId={videoId} expanded={true} />
            <ViewerBehaviorWidget data={dashboardData.viewerBehavior} expanded={true} />
          </div>
        )}

        {activeTab === 'conversions' && (
          <div className="conversions-view">
            <ConversionWidget data={dashboardData.conversions} />
          </div>
        )}

        {activeTab === 'predictions' && (
          <div className="predictions-view">
            <PredictiveWidget data={dashboardData.predictions} />
          </div>
        )}

        {activeTab === 'competitors' && (
          <div className="competitors-view">
            <CompetitorWidget data={dashboardData.competitors} />
          </div>
        )}

        {activeTab === 'custom' && (
          <div className="custom-view">
            <DashboardBuilder widgets={widgets} onSave={loadWidgets} />
          </div>
        )}
      </div>
    </div>
  );
};

export default AnalyticsDashboard;