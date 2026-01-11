/**
 * Viewer Behavior Analysis Widget
 * Shows drop-off points, engagement patterns, and device breakdown
 */

import React, { useState, useEffect } from 'react';

const ViewerBehaviorWidget = ({ data, expanded = false }) => {
  const [selectedMetric, setSelectedMetric] = useState('completion');
  const [timeFilter, setTimeFilter] = useState('all');

  if (!data) {
    return (
      <div className="viewer-behavior-widget loading">
        <div className="widget-header">
          <h3>👥 Viewer Behavior</h3>
        </div>
        <div className="loading-content">
          <div className="skeleton-bars">
            <div className="skeleton-bar"></div>
            <div className="skeleton-bar"></div>
            <div className="skeleton-bar"></div>
          </div>
        </div>
      </div>
    );
  }

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const formatPercentage = (value) => `${(value * 100).toFixed(1)}%`;

  const getDropOffColor = (percentage) => {
    if (percentage > 0.2) return '#ff4757'; // Red for high drop-off
    if (percentage > 0.1) return '#ffa502'; // Orange for medium drop-off
    return '#2ed573'; // Green for low drop-off
  };

  const metrics = [
    { id: 'completion', label: 'Completion Rate', icon: '✅' },
    { id: 'dropoff', label: 'Drop-off Points', icon: '📉' },
    { id: 'engagement', label: 'Engagement Events', icon: '💫' },
    { id: 'devices', label: 'Device Breakdown', icon: '📱' }
  ];

  return (
    <div className={`viewer-behavior-widget ${expanded ? 'expanded' : ''}`}>
      <div className="widget-header">
        <h3>👥 Viewer Behavior Analysis</h3>
        {expanded && (
          <div className="metric-selector">
            {metrics.map(metric => (
              <button
                key={metric.id}
                className={`metric-btn ${selectedMetric === metric.id ? 'active' : ''}`}
                onClick={() => setSelectedMetric(metric.id)}
              >
                <span>{metric.icon}</span>
                {metric.label}
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="behavior-content">
        {/* Key Metrics Summary */}
        <div className="metrics-summary">
          <div className="metric-card">
            <div className="metric-icon">👥</div>
            <div className="metric-info">
              <div className="metric-value">{data.total_viewers.toLocaleString()}</div>
              <div className="metric-label">Total Viewers</div>
            </div>
          </div>
          <div className="metric-card">
            <div className="metric-icon">⏱️</div>
            <div className="metric-info">
              <div className="metric-value">{formatTime(Math.round(data.average_watch_time))}</div>
              <div className="metric-label">Avg Watch Time</div>
            </div>
          </div>
          <div className="metric-card">
            <div className="metric-icon">✅</div>
            <div className="metric-info">
              <div className="metric-value">{formatPercentage(data.completion_rate)}</div>
              <div className="metric-label">Completion Rate</div>
            </div>
          </div>
        </div>

        {/* Drop-off Points Analysis */}
        {(selectedMetric === 'dropoff' || !expanded) && (
          <div className="dropoff-analysis">
            <h4>📉 Drop-off Points</h4>
            <div className="dropoff-chart">
              {data.drop_off_points.map((point, index) => (
                <div key={index} className="dropoff-point">
                  <div className="dropoff-bar">
                    <div 
                      className="dropoff-fill"
                      style={{ 
                        width: `${point.percentage * 100}%`,
                        backgroundColor: getDropOffColor(point.percentage)
                      }}
                    ></div>
                  </div>
                  <div className="dropoff-info">
                    <span className="dropoff-time">{formatTime(point.time)}</span>
                    <span className="dropoff-percentage">{formatPercentage(point.percentage)}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Engagement Events */}
        {(selectedMetric === 'engagement' || (!expanded && selectedMetric === 'completion')) && (
          <div className="engagement-events">
            <h4>💫 Engagement Events</h4>
            <div className="events-grid">
              <div className="event-item">
                <span className="event-icon">👍</span>
                <span className="event-label">Likes</span>
                <span className="event-value">{data.engagement_events.likes}</span>
              </div>
              <div className="event-item">
                <span className="event-icon">📤</span>
                <span className="event-label">Shares</span>
                <span className="event-value">{data.engagement_events.shares}</span>
              </div>
              <div className="event-item">
                <span className="event-icon">💬</span>
                <span className="event-label">Comments</span>
                <span className="event-value">{data.engagement_events.comments}</span>
              </div>
              <div className="event-item">
                <span className="event-icon">🔄</span>
                <span className="event-label">Replays</span>
                <span className="event-value">{data.engagement_events.replays}</span>
              </div>
            </div>
          </div>
        )}

        {/* Device Breakdown */}
        {(selectedMetric === 'devices' || expanded) && (
          <div className="device-breakdown">
            <h4>📱 Device Breakdown</h4>
            <div className="device-chart">
              {Object.entries(data.device_breakdown).map(([device, percentage]) => (
                <div key={device} className="device-item">
                  <div className="device-info">
                    <span className="device-icon">
                      {device === 'mobile' ? '📱' : device === 'desktop' ? '💻' : '📱'}
                    </span>
                    <span className="device-label">{device.charAt(0).toUpperCase() + device.slice(1)}</span>
                  </div>
                  <div className="device-bar">
                    <div 
                      className="device-fill"
                      style={{ width: `${percentage * 100}%` }}
                    ></div>
                  </div>
                  <span className="device-percentage">{formatPercentage(percentage)}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Completion Rate Visualization */}
        {selectedMetric === 'completion' && expanded && (
          <div className="completion-analysis">
            <h4>✅ Completion Rate Analysis</h4>
            <div className="completion-circle">
              <svg width="120" height="120" viewBox="0 0 120 120">
                <circle
                  cx="60"
                  cy="60"
                  r="50"
                  stroke="#e9ecef"
                  strokeWidth="10"
                  fill="transparent"
                />
                <circle
                  cx="60"
                  cy="60"
                  r="50"
                  stroke="#28a745"
                  strokeWidth="10"
                  fill="transparent"
                  strokeDasharray={`${2 * Math.PI * 50}`}
                  strokeDashoffset={`${2 * Math.PI * 50 * (1 - data.completion_rate)}`}
                  strokeLinecap="round"
                  transform="rotate(-90 60 60)"
                />
                <text x="60" y="65" textAnchor="middle" className="completion-text">
                  {formatPercentage(data.completion_rate)}
                </text>
              </svg>
            </div>
            <div className="completion-insights">
              <p>
                {data.completion_rate > 0.7 ? 
                  '🎉 Excellent completion rate! Your content is highly engaging.' :
                  data.completion_rate > 0.5 ?
                  '👍 Good completion rate. Consider optimizing content structure.' :
                  '⚠️ Low completion rate. Review content quality and engagement hooks.'
                }
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ViewerBehaviorWidget;