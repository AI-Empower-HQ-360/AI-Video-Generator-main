/**
 * Analytics API service for frontend integration
 */

const API_BASE_URL = '/api/analytics';

class AnalyticsAPI {
  
  async getVideoHeatmap(videoId, duration = 300) {
    try {
      const response = await fetch(`${API_BASE_URL}/heatmap/${videoId}?duration=${duration}`);
      const data = await response.json();
      return data.success ? data.heatmap_data : [];
    } catch (error) {
      console.error('Error fetching heatmap data:', error);
      return [];
    }
  }

  async getViewerBehavior(videoId) {
    try {
      const response = await fetch(`${API_BASE_URL}/viewer-behavior/${videoId}`);
      const data = await response.json();
      return data.success ? data.behavior_data : null;
    } catch (error) {
      console.error('Error fetching viewer behavior:', error);
      return null;
    }
  }

  async getConversionMetrics(videoId) {
    try {
      const response = await fetch(`${API_BASE_URL}/conversion-tracking/${videoId}`);
      const data = await response.json();
      return data.success ? data.conversion_data : null;
    } catch (error) {
      console.error('Error fetching conversion metrics:', error);
      return null;
    }
  }

  async getPredictiveInsights(videoId) {
    try {
      const response = await fetch(`${API_BASE_URL}/predictive-modeling/${videoId}`);
      const data = await response.json();
      return data.success ? data.predictions : null;
    } catch (error) {
      console.error('Error fetching predictive insights:', error);
      return null;
    }
  }

  async getCompetitorAnalysis() {
    try {
      const response = await fetch(`${API_BASE_URL}/competitor-analysis`);
      const data = await response.json();
      return data.success ? {
        competitors: data.competitors,
        benchmarks: data.benchmark_metrics
      } : null;
    } catch (error) {
      console.error('Error fetching competitor analysis:', error);
      return null;
    }
  }

  async getDashboardWidgets(userId = 'default') {
    try {
      const response = await fetch(`${API_BASE_URL}/dashboard/widgets?user_id=${userId}`);
      const data = await response.json();
      return data.success ? data.widgets : [];
    } catch (error) {
      console.error('Error fetching dashboard widgets:', error);
      return [];
    }
  }

  async saveWidgetConfiguration(userId, widgetConfig) {
    try {
      const response = await fetch(`${API_BASE_URL}/dashboard/widgets`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          user_id: userId,
          widget_config: widgetConfig
        })
      });
      const data = await response.json();
      return data.success ? data : null;
    } catch (error) {
      console.error('Error saving widget configuration:', error);
      return null;
    }
  }

  async trackEngagementEvent(eventData) {
    try {
      const response = await fetch(`${API_BASE_URL}/engagement/track`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(eventData)
      });
      const data = await response.json();
      return data.success;
    } catch (error) {
      console.error('Error tracking engagement event:', error);
      return false;
    }
  }

  async getAnalyticsSummary(videoId = null, timeRange = '7d') {
    try {
      const params = new URLSearchParams({ time_range: timeRange });
      if (videoId) params.append('video_id', videoId);
      
      const response = await fetch(`${API_BASE_URL}/analytics-summary?${params}`);
      const data = await response.json();
      return data.success ? data.summary : null;
    } catch (error) {
      console.error('Error fetching analytics summary:', error);
      return null;
    }
  }

}

// Create and export singleton instance
export const analyticsAPI = new AnalyticsAPI();
export default analyticsAPI;