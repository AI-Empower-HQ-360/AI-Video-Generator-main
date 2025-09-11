/**
 * Custom Dashboard Builder with Drag-Drop Widgets
 */

import React, { useState, useEffect, useRef } from 'react';
import analyticsAPI from '../api/analytics-integration.js';

const DashboardBuilder = ({ widgets = [], onSave }) => {
  const [availableWidgets, setAvailableWidgets] = useState(widgets);
  const [dashboardLayout, setDashboardLayout] = useState([]);
  const [draggedWidget, setDraggedWidget] = useState(null);
  const [dragOverPosition, setDragOverPosition] = useState(null);
  const [editMode, setEditMode] = useState(true);
  const [selectedWidget, setSelectedWidget] = useState(null);
  const dashboardRef = useRef(null);

  useEffect(() => {
    setAvailableWidgets(widgets);
    // Load saved dashboard layout if exists
    loadSavedLayout();
  }, [widgets]);

  const loadSavedLayout = () => {
    const saved = localStorage.getItem('dashboard_layout');
    if (saved) {
      try {
        setDashboardLayout(JSON.parse(saved));
      } catch (error) {
        console.error('Error loading saved layout:', error);
      }
    }
  };

  const saveDashboardLayout = async () => {
    try {
      // Save to localStorage
      localStorage.setItem('dashboard_layout', JSON.stringify(dashboardLayout));
      
      // Save to backend
      const result = await analyticsAPI.saveWidgetConfiguration('default', {
        layout: dashboardLayout,
        timestamp: new Date().toISOString()
      });
      
      if (result) {
        alert('Dashboard layout saved successfully!');
        if (onSave) onSave();
      }
    } catch (error) {
      console.error('Error saving dashboard:', error);
      alert('Error saving dashboard layout');
    }
  };

  const handleDragStart = (e, widget) => {
    setDraggedWidget(widget);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    
    const rect = dashboardRef.current?.getBoundingClientRect();
    if (rect) {
      const x = Math.floor((e.clientX - rect.left) / 280); // Assuming 280px grid
      const y = Math.floor((e.clientY - rect.top) / 200);   // Assuming 200px grid
      setDragOverPosition({ x, y });
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    
    if (draggedWidget && dragOverPosition) {
      const newWidget = {
        ...draggedWidget,
        id: `${draggedWidget.id}_${Date.now()}`,
        position: dragOverPosition,
        size: draggedWidget.size || { width: 2, height: 2 }
      };
      
      setDashboardLayout(prev => [...prev, newWidget]);
    }
    
    setDraggedWidget(null);
    setDragOverPosition(null);
  };

  const handleWidgetMove = (widgetId, newPosition) => {
    setDashboardLayout(prev => 
      prev.map(widget => 
        widget.id === widgetId 
          ? { ...widget, position: newPosition }
          : widget
      )
    );
  };

  const handleWidgetResize = (widgetId, newSize) => {
    setDashboardLayout(prev => 
      prev.map(widget => 
        widget.id === widgetId 
          ? { ...widget, size: newSize }
          : widget
      )
    );
  };

  const handleWidgetRemove = (widgetId) => {
    setDashboardLayout(prev => prev.filter(widget => widget.id !== widgetId));
  };

  const handleWidgetConfig = (widget) => {
    setSelectedWidget(widget);
  };

  const clearDashboard = () => {
    if (confirm('Are you sure you want to clear the entire dashboard?')) {
      setDashboardLayout([]);
    }
  };

  const getGridPosition = (position) => ({
    gridColumn: `${position.x + 1} / span 2`,
    gridRow: `${position.y + 1} / span 2`
  });

  return (
    <div className="dashboard-builder">
      <div className="builder-header">
        <h3>🛠️ Custom Dashboard Builder</h3>
        <div className="builder-controls">
          <button 
            className={`mode-toggle ${editMode ? 'active' : ''}`}
            onClick={() => setEditMode(!editMode)}
          >
            {editMode ? '✏️ Edit Mode' : '👁️ View Mode'}
          </button>
          <button onClick={saveDashboardLayout} className="save-btn">
            💾 Save Layout
          </button>
          <button onClick={clearDashboard} className="clear-btn">
            🗑️ Clear
          </button>
        </div>
      </div>

      <div className="builder-content">
        {/* Widget Palette */}
        {editMode && (
          <div className="widget-palette">
            <h4>📦 Available Widgets</h4>
            <div className="palette-widgets">
              {availableWidgets.map(widget => (
                <div
                  key={widget.id}
                  className="palette-widget"
                  draggable
                  onDragStart={(e) => handleDragStart(e, widget)}
                >
                  <div className="widget-icon">
                    {widget.type === 'heatmap' ? '🔥' :
                     widget.type === 'roi_analytics' ? '💰' :
                     widget.type === 'viewer_behavior' ? '👥' :
                     widget.type === 'predictive_modeling' ? '🔮' :
                     widget.type === 'competitor_analysis' ? '⚔️' : '📊'}
                  </div>
                  <div className="widget-info">
                    <div className="widget-title">{widget.title}</div>
                    <div className="widget-description">{widget.description}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Dashboard Grid */}
        <div 
          className={`dashboard-grid ${editMode ? 'edit-mode' : ''}`}
          ref={dashboardRef}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
        >
          {/* Grid Background */}
          {editMode && (
            <div className="grid-background">
              {Array.from({ length: 24 }, (_, i) => (
                <div key={i} className="grid-cell"></div>
              ))}
            </div>
          )}

          {/* Drop Zone Indicator */}
          {editMode && dragOverPosition && (
            <div 
              className="drop-zone-indicator"
              style={getGridPosition(dragOverPosition)}
            />
          )}

          {/* Dashboard Widgets */}
          {dashboardLayout.map(widget => (
            <DashboardWidget
              key={widget.id}
              widget={widget}
              editMode={editMode}
              onMove={handleWidgetMove}
              onResize={handleWidgetResize}
              onRemove={handleWidgetRemove}
              onConfig={handleWidgetConfig}
            />
          ))}

          {/* Empty State */}
          {dashboardLayout.length === 0 && (
            <div className="empty-dashboard">
              <div className="empty-icon">📊</div>
              <h4>Your Custom Dashboard</h4>
              <p>
                {editMode 
                  ? 'Drag widgets from the palette to build your custom analytics dashboard'
                  : 'No widgets added yet. Switch to Edit Mode to add widgets.'
                }
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Widget Configuration Modal */}
      {selectedWidget && (
        <WidgetConfigModal
          widget={selectedWidget}
          onSave={(config) => {
            setDashboardLayout(prev =>
              prev.map(w => w.id === selectedWidget.id ? { ...w, config } : w)
            );
            setSelectedWidget(null);
          }}
          onClose={() => setSelectedWidget(null)}
        />
      )}
    </div>
  );
};

// Individual Dashboard Widget Component
const DashboardWidget = ({ widget, editMode, onMove, onResize, onRemove, onConfig }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isResizing, setIsResizing] = useState(false);

  const handleDragStart = (e) => {
    if (!editMode) return;
    setIsDragging(true);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragEnd = () => {
    setIsDragging(false);
  };

  const style = {
    gridColumn: `${widget.position.x + 1} / span ${widget.size.width}`,
    gridRow: `${widget.position.y + 1} / span ${widget.size.height}`,
    opacity: isDragging ? 0.5 : 1
  };

  return (
    <div
      className={`dashboard-widget ${editMode ? 'editable' : ''}`}
      style={style}
      draggable={editMode}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
    >
      {editMode && (
        <div className="widget-controls">
          <button onClick={() => onConfig(widget)} className="config-btn" title="Configure">
            ⚙️
          </button>
          <button onClick={() => onRemove(widget.id)} className="remove-btn" title="Remove">
            ❌
          </button>
        </div>
      )}

      <div className="widget-content">
        <div className="widget-header">
          <h4>{widget.title}</h4>
        </div>
        <div className="widget-body">
          <div className="widget-placeholder">
            <div className="placeholder-icon">
              {widget.type === 'heatmap' ? '🔥' :
               widget.type === 'roi_analytics' ? '💰' :
               widget.type === 'viewer_behavior' ? '👥' :
               widget.type === 'predictive_modeling' ? '🔮' :
               widget.type === 'competitor_analysis' ? '⚔️' : '📊'}
            </div>
            <p>{widget.description}</p>
          </div>
        </div>
      </div>

      {editMode && (
        <div className="resize-handle" 
             onMouseDown={() => setIsResizing(true)}
             title="Resize">
          ↘️
        </div>
      )}
    </div>
  );
};

// Widget Configuration Modal
const WidgetConfigModal = ({ widget, onSave, onClose }) => {
  const [config, setConfig] = useState(widget.config || {});

  const handleSave = () => {
    onSave(config);
  };

  return (
    <div className="modal-overlay">
      <div className="config-modal">
        <div className="modal-header">
          <h3>⚙️ Configure {widget.title}</h3>
          <button onClick={onClose} className="close-btn">❌</button>
        </div>
        <div className="modal-body">
          <div className="config-form">
            <div className="form-group">
              <label>Title:</label>
              <input
                type="text"
                value={config.title || widget.title}
                onChange={(e) => setConfig({...config, title: e.target.value})}
              />
            </div>
            <div className="form-group">
              <label>Refresh Interval (seconds):</label>
              <input
                type="number"
                value={config.refresh_interval || 30}
                onChange={(e) => setConfig({...config, refresh_interval: parseInt(e.target.value)})}
              />
            </div>
            {widget.type === 'heatmap' && (
              <div className="form-group">
                <label>Video ID:</label>
                <input
                  type="text"
                  value={config.video_id || 'auto'}
                  onChange={(e) => setConfig({...config, video_id: e.target.value})}
                />
              </div>
            )}
          </div>
        </div>
        <div className="modal-footer">
          <button onClick={onClose} className="cancel-btn">Cancel</button>
          <button onClick={handleSave} className="save-btn">Save</button>
        </div>
      </div>
    </div>
  );
};

export default DashboardBuilder;