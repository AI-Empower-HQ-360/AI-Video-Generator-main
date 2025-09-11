/**
 * Predictive Modeling Widget for Content Success
 */

import React, { useState, useEffect } from 'react';

const PredictiveWidget = ({ data, expanded = false }) => {
  const [selectedPrediction, setSelectedPrediction] = useState('performance');

  if (!data) {
    return (
      <div className="predictive-widget loading">
        <div className="widget-header">
          <h3>🔮 Predictive Insights</h3>
        </div>
        <div className="loading-content">Generating predictions...</div>
      </div>
    );
  }

  const getScoreColor = (score) => {
    if (score >= 80) return '#28a745'; // Green
    if (score >= 60) return '#ffc107'; // Yellow
    if (score >= 40) return '#fd7e14'; // Orange
    return '#dc3545'; // Red
  };

  const getScoreLabel = (score) => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Fair';
    return 'Needs Improvement';
  };

  const getConfidenceIcon = (confidence) => {
    if (confidence >= 0.8) return '🎯';
    if (confidence >= 0.6) return '👍';
    return '🤔';
  };

  const formatPercentage = (value) => `${(value * 100).toFixed(1)}%`;

  const predictionTypes = [
    { id: 'performance', label: 'Performance Score', icon: '📊' },
    { id: 'optimization', label: 'Optimization Tips', icon: '💡' },
    { id: 'projections', label: 'Future Projections', icon: '📈' }
  ];

  return (
    <div className={`predictive-widget ${expanded ? 'expanded' : ''}`}>
      <div className="widget-header">
        <h3>🔮 Predictive Modeling</h3>
        {expanded && (
          <div className="prediction-selector">
            {predictionTypes.map(type => (
              <button
                key={type.id}
                className={`prediction-btn ${selectedPrediction === type.id ? 'active' : ''}`}
                onClick={() => setSelectedPrediction(type.id)}
              >
                <span>{type.icon}</span>
                {type.label}
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="predictive-content">
        {/* Performance Prediction Score */}
        {(selectedPrediction === 'performance' || !expanded) && (
          <div className="performance-prediction">
            <div className="prediction-score-container">
              <div className="score-circle">
                <svg width="120" height="120" viewBox="0 0 120 120">
                  <circle
                    cx="60"
                    cy="60"
                    r="50"
                    stroke="#e9ecef"
                    strokeWidth="8"
                    fill="transparent"
                  />
                  <circle
                    cx="60"
                    cy="60"
                    r="50"
                    stroke={getScoreColor(data.performance_prediction.score)}
                    strokeWidth="8"
                    fill="transparent"
                    strokeDasharray={`${2 * Math.PI * 50}`}
                    strokeDashoffset={`${2 * Math.PI * 50 * (1 - data.performance_prediction.score / 100)}`}
                    strokeLinecap="round"
                    transform="rotate(-90 60 60)"
                  />
                  <text x="60" y="65" textAnchor="middle" className="score-text">
                    {Math.round(data.performance_prediction.score)}
                  </text>
                </svg>
              </div>
              <div className="score-details">
                <h4>Performance Score</h4>
                <div className="score-label" style={{ color: getScoreColor(data.performance_prediction.score) }}>
                  {getScoreLabel(data.performance_prediction.score)}
                </div>
                <div className="confidence-indicator">
                  <span>{getConfidenceIcon(data.performance_prediction.confidence)}</span>
                  <span>Confidence: {formatPercentage(data.performance_prediction.confidence)}</span>
                </div>
              </div>
            </div>

            {expanded && (
              <div className="prediction-factors">
                <h4>🎯 Contributing Factors</h4>
                <div className="factors-grid">
                  {Object.entries(data.performance_prediction.factors).map(([factor, score]) => (
                    <div key={factor} className="factor-item">
                      <div className="factor-header">
                        <span className="factor-name">
                          {factor.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </span>
                        <span className="factor-score">{formatPercentage(score)}</span>
                      </div>
                      <div className="factor-bar">
                        <div 
                          className="factor-fill"
                          style={{ 
                            width: `${score * 100}%`,
                            backgroundColor: getScoreColor(score * 100)
                          }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Optimization Suggestions */}
        {(selectedPrediction === 'optimization' || (!expanded && data.optimization_suggestions)) && (
          <div className="optimization-suggestions">
            <h4>💡 AI-Powered Recommendations</h4>
            <div className="suggestions-list">
              {data.optimization_suggestions.map((suggestion, index) => (
                <div key={index} className="suggestion-item">
                  <div className="suggestion-icon">💡</div>
                  <div className="suggestion-text">{suggestion}</div>
                  <div className="suggestion-priority">
                    {index < 2 ? '🔥 High' : index < 4 ? '⚡ Medium' : '📋 Low'}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Future Projections */}
        {(selectedPrediction === 'projections' || expanded) && (
          <div className="future-projections">
            <h4>📈 7-Day Projections</h4>
            <div className="projections-grid">
              <div className="projection-card">
                <div className="projection-icon">👀</div>
                <div className="projection-info">
                  <div className="projection-value">
                    {data.projected_metrics.views_7_days.toLocaleString()}
                  </div>
                  <div className="projection-label">Projected Views</div>
                </div>
              </div>
              <div className="projection-card">
                <div className="projection-icon">✅</div>
                <div className="projection-info">
                  <div className="projection-value">
                    {formatPercentage(data.projected_metrics.completion_rate)}
                  </div>
                  <div className="projection-label">Completion Rate</div>
                </div>
              </div>
              <div className="projection-card">
                <div className="projection-icon">💫</div>
                <div className="projection-info">
                  <div className="projection-value">
                    {Math.round(data.projected_metrics.engagement_score)}
                  </div>
                  <div className="projection-label">Engagement Score</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Compact View Summary */}
        {!expanded && (
          <div className="prediction-summary">
            <div className="summary-item">
              <span className="summary-label">Score:</span>
              <span className="summary-value" style={{ color: getScoreColor(data.performance_prediction.score) }}>
                {Math.round(data.performance_prediction.score)}/100
              </span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Confidence:</span>
              <span className="summary-value">
                {getConfidenceIcon(data.performance_prediction.confidence)} {formatPercentage(data.performance_prediction.confidence)}
              </span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Status:</span>
              <span className="summary-value" style={{ color: getScoreColor(data.performance_prediction.score) }}>
                {getScoreLabel(data.performance_prediction.score)}
              </span>
            </div>
          </div>
        )}

        {/* Action Recommendations */}
        {expanded && (
          <div className="action-recommendations">
            <h4>🎯 Recommended Actions</h4>
            <div className="actions-list">
              {data.performance_prediction.score < 60 && (
                <div className="action-item urgent">
                  <span className="action-icon">🚨</span>
                  <div className="action-content">
                    <strong>Immediate Action Required</strong>
                    <p>Content score is below optimal. Review the highest-impact optimization suggestions.</p>
                  </div>
                </div>
              )}
              {data.performance_prediction.confidence < 0.7 && (
                <div className="action-item warning">
                  <span className="action-icon">⚠️</span>
                  <div className="action-content">
                    <strong>Low Prediction Confidence</strong>
                    <p>Gather more performance data to improve prediction accuracy.</p>
                  </div>
                )}
              )}
              <div className="action-item info">
                <span className="action-icon">📊</span>
                <div className="action-content">
                  <strong>Monitor Performance</strong>
                  <p>Track actual metrics against predictions to validate model accuracy.</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Model Information */}
        {expanded && (
          <div className="model-info">
            <h4>🤖 Model Information</h4>
            <div className="model-details">
              <div className="model-stat">
                <span className="stat-label">Model Version:</span>
                <span className="stat-value">v2.1.0</span>
              </div>
              <div className="model-stat">
                <span className="stat-label">Training Data:</span>
                <span className="stat-value">10K+ videos</span>
              </div>
              <div className="model-stat">
                <span className="stat-label">Accuracy:</span>
                <span className="stat-value">87.3%</span>
              </div>
              <div className="model-stat">
                <span className="stat-label">Last Updated:</span>
                <span className="stat-value">2 days ago</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PredictiveWidget;