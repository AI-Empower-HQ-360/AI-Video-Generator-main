/**
 * Conversion Tracking and ROI Analytics Widget
 */

import React, { useState, useEffect } from 'react';

const ConversionWidget = ({ data, expanded = false }) => {
  const [selectedTimeframe, setSelectedTimeframe] = useState('7d');
  const [selectedMetric, setSelectedMetric] = useState('roi');

  if (!data) {
    return (
      <div className="conversion-widget loading">
        <div className="widget-header">
          <h3>💰 Conversion & ROI</h3>
        </div>
        <div className="loading-content">Loading conversion data...</div>
      </div>
    );
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatPercentage = (value) => `${(value * 100).toFixed(1)}%`;

  const getROIColor = (roi) => {
    if (roi > 2) return '#28a745'; // Green for high ROI
    if (roi > 0) return '#ffc107'; // Yellow for positive ROI
    return '#dc3545'; // Red for negative ROI
  };

  const getROIStatus = (roi) => {
    if (roi > 2) return { text: 'Excellent', icon: '🚀' };
    if (roi > 1) return { text: 'Good', icon: '👍' };
    if (roi > 0) return { text: 'Positive', icon: '📈' };
    return { text: 'Needs Attention', icon: '⚠️' };
  };

  const roiStatus = getROIStatus(data.roi);

  return (
    <div className={`conversion-widget ${expanded ? 'expanded' : ''}`}>
      <div className="widget-header">
        <h3>💰 Conversion & ROI Analytics</h3>
        {expanded && (
          <div className="widget-controls">
            <select 
              value={selectedTimeframe} 
              onChange={(e) => setSelectedTimeframe(e.target.value)}
              className="timeframe-selector"
            >
              <option value="1d">Last 24 Hours</option>
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
              <option value="90d">Last 90 Days</option>
            </select>
          </div>
        )}
      </div>

      <div className="conversion-content">
        {/* Key Metrics Cards */}
        <div className="metrics-cards">
          <div className="metric-card roi-card">
            <div className="metric-header">
              <span className="metric-icon">📊</span>
              <span className="metric-title">ROI</span>
            </div>
            <div className="metric-value" style={{ color: getROIColor(data.roi) }}>
              {(data.roi * 100).toFixed(0)}%
            </div>
            <div className="metric-status">
              <span>{roiStatus.icon}</span>
              <span>{roiStatus.text}</span>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-header">
              <span className="metric-icon">💵</span>
              <span className="metric-title">Revenue</span>
            </div>
            <div className="metric-value">{formatCurrency(data.total_revenue)}</div>
            <div className="metric-subtitle">Total Revenue</div>
          </div>

          <div className="metric-card">
            <div className="metric-header">
              <span className="metric-icon">🎯</span>
              <span className="metric-title">Conversions</span>
            </div>
            <div className="metric-value">{data.conversions}</div>
            <div className="metric-subtitle">{formatPercentage(data.conversion_rate)} rate</div>
          </div>

          <div className="metric-card">
            <div className="metric-header">
              <span className="metric-icon">💸</span>
              <span className="metric-title">Cost</span>
            </div>
            <div className="metric-value">{formatCurrency(data.cost)}</div>
            <div className="metric-subtitle">Total Investment</div>
          </div>
        </div>

        {/* Detailed Analytics */}
        {expanded && (
          <>
            {/* ROI Breakdown */}
            <div className="roi-breakdown">
              <h4>📈 ROI Breakdown</h4>
              <div className="roi-chart">
                <div className="roi-bar-container">
                  <div className="roi-label">Revenue</div>
                  <div className="roi-bar revenue-bar">
                    <div 
                      className="roi-fill"
                      style={{ width: '100%', backgroundColor: '#28a745' }}
                    ></div>
                    <span className="roi-amount">{formatCurrency(data.total_revenue)}</span>
                  </div>
                </div>
                <div className="roi-bar-container">
                  <div className="roi-label">Cost</div>
                  <div className="roi-bar cost-bar">
                    <div 
                      className="roi-fill"
                      style={{ 
                        width: `${(data.cost / data.total_revenue) * 100}%`,
                        backgroundColor: '#dc3545'
                      }}
                    ></div>
                    <span className="roi-amount">{formatCurrency(data.cost)}</span>
                  </div>
                </div>
                <div className="roi-summary">
                  <strong>Net Profit: {formatCurrency(data.total_revenue - data.cost)}</strong>
                </div>
              </div>
            </div>

            {/* Conversion Timeline */}
            <div className="conversion-timeline">
              <h4>⏱️ Conversion Timeline</h4>
              <div className="timeline-chart">
                {data.conversion_timeline.map((point, index) => (
                  <div key={index} className="timeline-point">
                    <div className="timeline-bar">
                      <div 
                        className="timeline-fill"
                        style={{ 
                          height: `${(point.conversions / Math.max(...data.conversion_timeline.map(p => p.conversions))) * 100}%`
                        }}
                      ></div>
                    </div>
                    <div className="timeline-label">
                      <span className="time">{Math.floor(point.time / 60)}m</span>
                      <span className="conversions">{point.conversions}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Performance Metrics */}
            <div className="performance-metrics">
              <h4>🎯 Performance Metrics</h4>
              <div className="metrics-grid">
                <div className="performance-item">
                  <span className="perf-label">Cost per Conversion</span>
                  <span className="perf-value">{formatCurrency(data.cost_per_conversion)}</span>
                </div>
                <div className="performance-item">
                  <span className="perf-label">Revenue per View</span>
                  <span className="perf-value">{formatCurrency(data.revenue_per_view)}</span>
                </div>
                <div className="performance-item">
                  <span className="perf-label">Total Views</span>
                  <span className="perf-value">{data.total_views.toLocaleString()}</span>
                </div>
                <div className="performance-item">
                  <span className="perf-label">Conversion Rate</span>
                  <span className="perf-value">{formatPercentage(data.conversion_rate)}</span>
                </div>
              </div>
            </div>
          </>
        )}

        {/* Compact Summary for non-expanded view */}
        {!expanded && (
          <div className="conversion-summary">
            <div className="summary-row">
              <span className="summary-label">Revenue:</span>
              <span className="summary-value">{formatCurrency(data.total_revenue)}</span>
            </div>
            <div className="summary-row">
              <span className="summary-label">Conversions:</span>
              <span className="summary-value">{data.conversions} ({formatPercentage(data.conversion_rate)})</span>
            </div>
            <div className="summary-row">
              <span className="summary-label">ROI:</span>
              <span className="summary-value" style={{ color: getROIColor(data.roi) }}>
                {(data.roi * 100).toFixed(0)}% {roiStatus.icon}
              </span>
            </div>
          </div>
        )}

        {/* Optimization Suggestions */}
        {expanded && (
          <div className="optimization-suggestions">
            <h4>💡 Optimization Suggestions</h4>
            <div className="suggestions-list">
              {data.roi < 1 && (
                <div className="suggestion warning">
                  <span className="suggestion-icon">⚠️</span>
                  <span>ROI is below break-even. Consider optimizing targeting or reducing costs.</span>
                </div>
              )}
              {data.conversion_rate < 0.02 && (
                <div className="suggestion info">
                  <span className="suggestion-icon">🎯</span>
                  <span>Low conversion rate. Test different call-to-actions or landing pages.</span>
                </div>
              )}
              {data.cost_per_conversion > 50 && (
                <div className="suggestion warning">
                  <span className="suggestion-icon">💸</span>
                  <span>High cost per conversion. Review ad spend efficiency.</span>
                </div>
              )}
              <div className="suggestion success">
                <span className="suggestion-icon">📈</span>
                <span>Track conversions throughout the customer journey for better insights.</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ConversionWidget;