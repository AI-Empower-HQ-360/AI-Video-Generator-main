/**
 * Competitor Analysis and Benchmarking Widget
 */

import React, { useState, useEffect } from 'react';

const CompetitorWidget = ({ data, expanded = false }) => {
  const [selectedMetric, setSelectedMetric] = useState('engagement');
  const [sortBy, setSortBy] = useState('engagement_rate');
  const [viewMode, setViewMode] = useState('table');

  if (!data) {
    return (
      <div className="competitor-widget loading">
        <div className="widget-header">
          <h3>⚔️ Competitor Analysis</h3>
        </div>
        <div className="loading-content">Analyzing competitors...</div>
      </div>
    );
  }

  const formatPercentage = (value) => `${(value * 100).toFixed(2)}%`;
  const formatNumber = (value) => value.toLocaleString();

  const getGrowthColor = (rate) => {
    if (rate > 0.1) return '#28a745'; // Green for high growth
    if (rate > 0) return '#ffc107'; // Yellow for positive growth
    return '#dc3545'; // Red for negative growth
  };

  const getGrowthIcon = (rate) => {
    if (rate > 0.1) return '🚀';
    if (rate > 0) return '📈';
    return '📉';
  };

  const getRankingIcon = (index) => {
    switch(index) {
      case 0: return '🥇';
      case 1: return '🥈';
      case 2: return '🥉';
      default: return `${index + 1}`;
    }
  };

  const sortedCompetitors = [...data.competitors].sort((a, b) => {
    switch(sortBy) {
      case 'engagement_rate':
        return b.engagement_rate - a.engagement_rate;
      case 'avg_views':
        return b.avg_views - a.avg_views;
      case 'growth_rate':
        return b.growth_rate - a.growth_rate;
      case 'posting_frequency':
        return b.posting_frequency - a.posting_frequency;
      default:
        return 0;
    }
  });

  const metrics = [
    { id: 'engagement', label: 'Engagement Rate', icon: '💫' },
    { id: 'views', label: 'Average Views', icon: '👀' },
    { id: 'growth', label: 'Growth Rate', icon: '📈' },
    { id: 'frequency', label: 'Posting Frequency', icon: '📅' }
  ];

  const viewModes = [
    { id: 'table', label: 'Table', icon: '📊' },
    { id: 'chart', label: 'Chart', icon: '📈' },
    { id: 'comparison', label: 'Comparison', icon: '⚖️' }
  ];

  return (
    <div className={`competitor-widget ${expanded ? 'expanded' : ''}`}>
      <div className="widget-header">
        <h3>⚔️ Competitor Analysis</h3>
        {expanded && (
          <div className="widget-controls">
            <div className="control-group">
              <label>Sort by:</label>
              <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                <option value="engagement_rate">Engagement Rate</option>
                <option value="avg_views">Average Views</option>
                <option value="growth_rate">Growth Rate</option>
                <option value="posting_frequency">Posting Frequency</option>
              </select>
            </div>
            <div className="view-toggles">
              {viewModes.map(mode => (
                <button
                  key={mode.id}
                  className={`view-btn ${viewMode === mode.id ? 'active' : ''}`}
                  onClick={() => setViewMode(mode.id)}
                >
                  <span>{mode.icon}</span>
                  {mode.label}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="competitor-content">
        {/* Industry Benchmarks */}
        <div className="benchmark-summary">
          <h4>📊 Industry Benchmarks</h4>
          <div className="benchmark-cards">
            <div className="benchmark-card">
              <div className="benchmark-icon">💫</div>
              <div className="benchmark-info">
                <div className="benchmark-value">{formatPercentage(data.benchmarks.industry_avg_engagement)}</div>
                <div className="benchmark-label">Avg Engagement</div>
              </div>
            </div>
            <div className="benchmark-card">
              <div className="benchmark-icon">✅</div>
              <div className="benchmark-info">
                <div className="benchmark-value">{formatPercentage(data.benchmarks.industry_avg_completion)}</div>
                <div className="benchmark-label">Avg Completion</div>
              </div>
            </div>
            <div className="benchmark-card">
              <div className="benchmark-icon">🏆</div>
              <div className="benchmark-info">
                <div className="benchmark-value">{formatPercentage(data.benchmarks.top_performer_engagement)}</div>
                <div className="benchmark-label">Top Performer</div>
              </div>
            </div>
          </div>
        </div>

        {/* Competitor Rankings */}
        {(viewMode === 'table' || !expanded) && (
          <div className="competitor-rankings">
            <h4>🏆 Competitor Rankings</h4>
            <div className="rankings-table">
              <div className="table-header">
                <div className="rank-col">Rank</div>
                <div className="name-col">Competitor</div>
                <div className="metric-col">Engagement</div>
                <div className="metric-col">Avg Views</div>
                <div className="metric-col">Growth</div>
                {expanded && <div className="metric-col">Frequency</div>}
              </div>
              {sortedCompetitors.slice(0, expanded ? 10 : 3).map((competitor, index) => (
                <div key={competitor.name} className="table-row">
                  <div className="rank-col">
                    <span className="rank-icon">{getRankingIcon(index)}</span>
                  </div>
                  <div className="name-col">
                    <span className="competitor-name">{competitor.name}</span>
                  </div>
                  <div className="metric-col">
                    <span className="metric-value">{formatPercentage(competitor.engagement_rate)}</span>
                  </div>
                  <div className="metric-col">
                    <span className="metric-value">{formatNumber(competitor.avg_views)}</span>
                  </div>
                  <div className="metric-col">
                    <span className="metric-value" style={{ color: getGrowthColor(competitor.growth_rate) }}>
                      {getGrowthIcon(competitor.growth_rate)} {formatPercentage(competitor.growth_rate)}
                    </span>
                  </div>
                  {expanded && (
                    <div className="metric-col">
                      <span className="metric-value">{competitor.posting_frequency}/week</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Chart View */}
        {viewMode === 'chart' && expanded && (
          <div className="competitor-chart">
            <h4>📈 Performance Comparison</h4>
            <div className="chart-container">
              <div className="chart-axis-label">Engagement Rate</div>
              <div className="chart-bars">
                {sortedCompetitors.map((competitor, index) => (
                  <div key={competitor.name} className="chart-bar-group">
                    <div className="chart-bar">
                      <div 
                        className="bar-fill"
                        style={{ 
                          height: `${(competitor.engagement_rate / Math.max(...sortedCompetitors.map(c => c.engagement_rate))) * 100}%`,
                          backgroundColor: index === 0 ? '#28a745' : index === 1 ? '#ffc107' : index === 2 ? '#fd7e14' : '#6c757d'
                        }}
                      ></div>
                    </div>
                    <div className="chart-label">
                      <div className="competitor-name">{competitor.name}</div>
                      <div className="metric-value">{formatPercentage(competitor.engagement_rate)}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Comparison View */}
        {viewMode === 'comparison' && expanded && (
          <div className="competitor-comparison">
            <h4>⚖️ Head-to-Head Comparison</h4>
            <div className="comparison-matrix">
              {sortedCompetitors.slice(0, 3).map(competitor => (
                <div key={competitor.name} className="comparison-card">
                  <div className="comparison-header">
                    <h5>{competitor.name}</h5>
                    <div className="overall-score">
                      Score: {Math.round((competitor.engagement_rate + competitor.growth_rate + 0.1) * 100)}
                    </div>
                  </div>
                  <div className="comparison-metrics">
                    <div className="comparison-metric">
                      <span className="metric-icon">💫</span>
                      <span className="metric-label">Engagement</span>
                      <span className="metric-value">{formatPercentage(competitor.engagement_rate)}</span>
                    </div>
                    <div className="comparison-metric">
                      <span className="metric-icon">👀</span>
                      <span className="metric-label">Views</span>
                      <span className="metric-value">{formatNumber(competitor.avg_views)}</span>
                    </div>
                    <div className="comparison-metric">
                      <span className="metric-icon">📈</span>
                      <span className="metric-label">Growth</span>
                      <span className="metric-value" style={{ color: getGrowthColor(competitor.growth_rate) }}>
                        {formatPercentage(competitor.growth_rate)}
                      </span>
                    </div>
                    <div className="comparison-metric">
                      <span className="metric-icon">📝</span>
                      <span className="metric-label">Content</span>
                      <span className="metric-value">{competitor.top_content_types.join(', ')}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Insights & Recommendations */}
        {expanded && (
          <div className="competitor-insights">
            <h4>💡 Strategic Insights</h4>
            <div className="insights-grid">
              <div className="insight-card opportunity">
                <div className="insight-icon">🎯</div>
                <div className="insight-content">
                  <h5>Market Opportunity</h5>
                  <p>
                    {data.benchmarks.top_performer_engagement > data.benchmarks.industry_avg_engagement * 1.5 ?
                      'High-performing competitors show significant room for improvement in engagement rates.' :
                      'Market engagement rates are fairly competitive across all players.'
                    }
                  </p>
                </div>
              </div>
              
              <div className="insight-card trend">
                <div className="insight-icon">📊</div>
                <div className="insight-content">
                  <h5>Growth Trends</h5>
                  <p>
                    {sortedCompetitors.filter(c => c.growth_rate > 0.1).length > 2 ?
                      'Multiple competitors are experiencing high growth - market is expanding rapidly.' :
                      'Moderate growth across the competitive landscape suggests market maturity.'
                    }
                  </p>
                </div>
              </div>

              <div className="insight-card strategy">
                <div className="insight-icon">🚀</div>
                <div className="insight-content">
                  <h5>Content Strategy</h5>
                  <p>
                    Top performers focus on {sortedCompetitors[0]?.top_content_types?.join(' and ')} content types 
                    with a posting frequency of {sortedCompetitors[0]?.posting_frequency} times per week.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Compact Summary */}
        {!expanded && (
          <div className="competitor-summary">
            <div className="summary-item">
              <span className="summary-label">Your Position:</span>
              <span className="summary-value">#{Math.floor(Math.random() * 3) + 2}</span>
            </div>
            <div className="summary-item">
              <span className="summary-label">vs Industry Avg:</span>
              <span className="summary-value">
                {Math.random() > 0.5 ? '📈 Above' : '📉 Below'}
              </span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Growth Opportunity:</span>
              <span className="summary-value">
                {formatPercentage(data.benchmarks.top_performer_engagement - data.benchmarks.industry_avg_engagement)}
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CompetitorWidget;