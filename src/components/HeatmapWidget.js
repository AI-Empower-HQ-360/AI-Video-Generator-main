/**
 * Real-time Video Engagement Heatmap Widget
 */

import React, { useState, useEffect, useRef } from 'react';
import analyticsAPI from '../api/analytics-integration.js';

const HeatmapWidget = ({ data = [], videoId, expanded = false }) => {
  const [heatmapData, setHeatmapData] = useState(data);
  const [isRealTime, setIsRealTime] = useState(false);
  const [videoDuration, setVideoDuration] = useState(300); // Default 5 minutes
  const canvasRef = useRef(null);
  const intervalRef = useRef(null);

  useEffect(() => {
    setHeatmapData(data);
    if (data.length > 0) {
      drawHeatmap();
    }
  }, [data]);

  useEffect(() => {
    if (isRealTime) {
      startRealTimeUpdates();
    } else {
      stopRealTimeUpdates();
    }
    return () => stopRealTimeUpdates();
  }, [isRealTime, videoId]);

  const startRealTimeUpdates = () => {
    intervalRef.current = setInterval(async () => {
      try {
        const newData = await analyticsAPI.getVideoHeatmap(videoId, videoDuration);
        setHeatmapData(newData);
      } catch (error) {
        console.error('Error updating heatmap:', error);
      }
    }, 5000); // Update every 5 seconds
  };

  const stopRealTimeUpdates = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  };

  const drawHeatmap = () => {
    const canvas = canvasRef.current;
    if (!canvas || !heatmapData.length) return;

    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Draw time axis
    ctx.fillStyle = '#333';
    ctx.font = '12px Arial';
    
    // Draw heatmap bars
    const barWidth = width / heatmapData.length;
    
    heatmapData.forEach((point, index) => {
      const x = index * barWidth;
      const intensity = point.intensity || 0;
      
      // Color based on intensity (blue to red gradient)
      const hue = (1 - intensity) * 240; // Blue=240, Red=0
      ctx.fillStyle = `hsl(${hue}, 70%, 50%)`;
      
      const barHeight = height * 0.8 * intensity;
      const y = height - barHeight - 20; // Leave space for time labels
      
      ctx.fillRect(x, y, barWidth - 1, barHeight);
      
      // Add time labels every minute
      if (point.time % 60 === 0) {
        ctx.fillStyle = '#666';
        ctx.fillText(`${Math.floor(point.time / 60)}m`, x, height - 5);
      }
    });

    // Draw intensity scale
    ctx.fillStyle = '#333';
    ctx.fillText('Low', 5, height - 5);
    ctx.fillText('High', width - 30, height - 5);
  };

  useEffect(() => {
    if (heatmapData.length > 0) {
      drawHeatmap();
    }
  }, [heatmapData]);

  const getIntensityColor = (intensity) => {
    const hue = (1 - intensity) * 240;
    return `hsl(${hue}, 70%, 50%)`;
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className={`heatmap-widget ${expanded ? 'expanded' : ''}`}>
      <div className="widget-header">
        <h3>🔥 Engagement Heatmap</h3>
        <div className="widget-controls">
          <label className="real-time-toggle">
            <input
              type="checkbox"
              checked={isRealTime}
              onChange={(e) => setIsRealTime(e.target.checked)}
            />
            <span>Real-time</span>
          </label>
          {isRealTime && <div className="live-indicator">🔴 LIVE</div>}
        </div>
      </div>

      <div className="heatmap-container">
        <canvas
          ref={canvasRef}
          width={expanded ? 800 : 400}
          height={expanded ? 200 : 100}
          className="heatmap-canvas"
        />
        
        {expanded && (
          <div className="heatmap-details">
            <div className="intensity-legend">
              <h4>Engagement Intensity</h4>
              <div className="legend-bar">
                {[0, 0.25, 0.5, 0.75, 1].map(intensity => (
                  <div
                    key={intensity}
                    className="legend-item"
                    style={{ backgroundColor: getIntensityColor(intensity) }}
                  >
                    {Math.round(intensity * 100)}%
                  </div>
                ))}
              </div>
            </div>
            
            <div className="heatmap-stats">
              <h4>Statistics</h4>
              <div className="stats-grid">
                <div className="stat">
                  <label>Peak Engagement</label>
                  <span>
                    {heatmapData.length > 0 && 
                      formatTime(heatmapData.reduce((max, point) => 
                        point.intensity > max.intensity ? point : max, heatmapData[0]
                      ).time)
                    }
                  </span>
                </div>
                <div className="stat">
                  <label>Average Intensity</label>
                  <span>
                    {heatmapData.length > 0 && 
                      Math.round((heatmapData.reduce((sum, point) => sum + point.intensity, 0) / heatmapData.length) * 100)
                    }%
                  </span>
                </div>
                <div className="stat">
                  <label>Total Data Points</label>
                  <span>{heatmapData.length}</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {!expanded && heatmapData.length > 0 && (
        <div className="heatmap-summary">
          <div className="summary-item">
            <span className="label">Peak:</span>
            <span className="value">
              {formatTime(heatmapData.reduce((max, point) => 
                point.intensity > max.intensity ? point : max, heatmapData[0]
              ).time)}
            </span>
          </div>
          <div className="summary-item">
            <span className="label">Avg:</span>
            <span className="value">
              {Math.round((heatmapData.reduce((sum, point) => sum + point.intensity, 0) / heatmapData.length) * 100)}%
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default HeatmapWidget;