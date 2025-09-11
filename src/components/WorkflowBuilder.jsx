import React, { useState, useCallback, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// Workflow Node Types
const NODE_TYPES = {
  start: { icon: '🚀', color: 'bg-green-500', label: 'Start' },
  action: { icon: '⚡', color: 'bg-blue-500', label: 'Action' },
  condition: { icon: '❓', color: 'bg-yellow-500', label: 'Condition' },
  approval: { icon: '✅', color: 'bg-purple-500', label: 'Approval' },
  localization: { icon: '🌍', color: 'bg-indigo-500', label: 'Localization' },
  schedule: { icon: '⏰', color: 'bg-orange-500', label: 'Schedule' },
  end: { icon: '🏁', color: 'bg-red-500', label: 'End' }
};

// Individual Workflow Node Component
const WorkflowNode = ({ node, onSelect, onDrag, isSelected, onConnect, connections }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const nodeRef = useRef(null);

  const nodeType = NODE_TYPES[node.node_type] || NODE_TYPES.action;

  const handleMouseDown = (e) => {
    if (e.target.classList.contains('connection-handle')) return;
    
    setIsDragging(true);
    const rect = nodeRef.current.getBoundingClientRect();
    setDragOffset({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    });
    onSelect(node.id);
  };

  const handleMouseMove = useCallback((e) => {
    if (!isDragging) return;
    
    const canvas = nodeRef.current.closest('.workflow-canvas');
    const canvasRect = canvas.getBoundingClientRect();
    
    const newX = e.clientX - canvasRect.left - dragOffset.x;
    const newY = e.clientY - canvasRect.top - dragOffset.y;
    
    onDrag(node.id, newX, newY);
  }, [isDragging, dragOffset, node.id, onDrag]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isDragging, handleMouseMove, handleMouseUp]);

  const handleConnectionClick = (type) => {
    onConnect(node.id, type);
  };

  return (
    <motion.div
      ref={nodeRef}
      className={`absolute cursor-move select-none`}
      style={{
        left: node.position_x,
        top: node.position_y,
        zIndex: isSelected ? 10 : 1
      }}
      onMouseDown={handleMouseDown}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      <div className={`
        ${nodeType.color} text-white rounded-lg p-4 shadow-lg border-2
        ${isSelected ? 'border-yellow-400 ring-2 ring-yellow-400' : 'border-transparent'}
        min-w-32 max-w-48 transition-all duration-200
      `}>
        <div className="flex items-center gap-2 mb-2">
          <span className="text-xl">{nodeType.icon}</span>
          <span className="font-medium text-sm">{nodeType.label}</span>
        </div>
        
        <div className="text-xs font-medium mb-1 truncate">
          {node.name}
        </div>
        
        {node.description && (
          <div className="text-xs opacity-80 line-clamp-2">
            {node.description}
          </div>
        )}

        {/* Connection Handles */}
        <div 
          className="connection-handle absolute -right-2 top-1/2 transform -translate-y-1/2 
                     w-4 h-4 bg-white border-2 border-gray-400 rounded-full cursor-crosshair
                     hover:bg-blue-200 transition-colors"
          onClick={() => handleConnectionClick('output')}
          title="Connect to next node"
        />
        
        <div 
          className="connection-handle absolute -left-2 top-1/2 transform -translate-y-1/2 
                     w-4 h-4 bg-white border-2 border-gray-400 rounded-full
                     hover:bg-green-200 transition-colors"
          title="Input connection"
        />
      </div>
    </motion.div>
  );
};

// Connection Line Component
const ConnectionLine = ({ connection, fromNode, toNode }) => {
  if (!fromNode || !toNode) return null;

  const startX = fromNode.position_x + 96; // Node width / 2
  const startY = fromNode.position_y + 32; // Node height / 2
  const endX = toNode.position_x;
  const endY = toNode.position_y + 32;

  const midX = (startX + endX) / 2;
  const midY = (startY + endY) / 2;

  // Create curved path
  const path = `M ${startX} ${startY} Q ${midX} ${startY} ${midX} ${midY} Q ${midX} ${endY} ${endX} ${endY}`;

  return (
    <motion.svg
      className="absolute inset-0 pointer-events-none"
      style={{ zIndex: 0 }}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      <path
        d={path}
        stroke="#6B7280"
        strokeWidth="2"
        fill="none"
        markerEnd="url(#arrowhead)"
        className="drop-shadow-sm"
      />
      
      {/* Condition label */}
      {connection.condition && (
        <text
          x={midX}
          y={midY - 5}
          textAnchor="middle"
          className="text-xs fill-gray-600 font-medium"
          style={{ textShadow: '0 0 3px white' }}
        >
          {connection.condition}
        </text>
      )}
      
      {/* Arrow marker definition */}
      <defs>
        <marker
          id="arrowhead"
          markerWidth="10"
          markerHeight="7"
          refX="9"
          refY="3.5"
          orient="auto"
        >
          <polygon
            points="0 0, 10 3.5, 0 7"
            fill="#6B7280"
          />
        </marker>
      </defs>
    </motion.svg>
  );
};

// Node Palette Component
const NodePalette = ({ onAddNode, isOpen, onToggle }) => {
  const handleAddNode = (nodeType) => {
    const newNode = {
      id: `node_${Date.now()}`,
      node_type: nodeType,
      name: `New ${NODE_TYPES[nodeType].label}`,
      description: '',
      position_x: 100 + Math.random() * 200,
      position_y: 100 + Math.random() * 200,
      config: {},
      action_type: nodeType === 'action' ? 'content_generation' : null,
      action_config: {},
      approval_required_from: nodeType === 'approval' ? [] : null,
      localization_enabled: nodeType === 'localization',
      target_languages: nodeType === 'localization' ? ['en'] : null
    };
    
    onAddNode(newNode);
  };

  return (
    <motion.div
      className={`fixed left-4 top-1/2 transform -translate-y-1/2 z-20 
                  bg-white rounded-lg shadow-xl border border-gray-200 p-4
                  ${isOpen ? 'w-48' : 'w-12'} transition-all duration-300`}
      initial={{ x: -100 }}
      animate={{ x: 0 }}
    >
      <button
        onClick={onToggle}
        className="w-full h-10 bg-blue-500 text-white rounded-lg hover:bg-blue-600 
                   transition-colors flex items-center justify-center mb-4"
      >
        {isOpen ? '←' : '→'}
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="space-y-2"
          >
            <h3 className="font-medium text-gray-700 mb-3">Add Nodes</h3>
            
            {Object.entries(NODE_TYPES).map(([type, config]) => (
              <button
                key={type}
                onClick={() => handleAddNode(type)}
                className={`w-full p-2 rounded-lg text-white text-sm font-medium
                           hover:opacity-80 transition-opacity flex items-center gap-2
                           ${config.color}`}
              >
                <span>{config.icon}</span>
                <span>{config.label}</span>
              </button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

// Properties Panel Component
const PropertiesPanel = ({ selectedNode, onUpdateNode, onDeleteNode, isOpen, onToggle }) => {
  const [localNode, setLocalNode] = useState(selectedNode || {});

  useEffect(() => {
    setLocalNode(selectedNode || {});
  }, [selectedNode]);

  const handleFieldChange = (field, value) => {
    const updatedNode = { ...localNode, [field]: value };
    setLocalNode(updatedNode);
    if (onUpdateNode) {
      onUpdateNode(updatedNode);
    }
  };

  const handleConfigChange = (configField, value) => {
    const updatedConfig = { ...localNode.action_config, [configField]: value };
    handleFieldChange('action_config', updatedConfig);
  };

  if (!selectedNode) {
    return (
      <motion.div
        className={`fixed right-4 top-1/2 transform -translate-y-1/2 z-20 
                    bg-white rounded-lg shadow-xl border border-gray-200 p-4
                    ${isOpen ? 'w-80' : 'w-12'} transition-all duration-300`}
      >
        <button
          onClick={onToggle}
          className="w-full h-10 bg-gray-500 text-white rounded-lg hover:bg-gray-600 
                     transition-colors flex items-center justify-center"
        >
          {isOpen ? '→' : '←'}
        </button>
        {isOpen && (
          <div className="mt-4 text-gray-500 text-center">
            Select a node to edit properties
          </div>
        )}
      </motion.div>
    );
  }

  return (
    <motion.div
      className={`fixed right-4 top-1/2 transform -translate-y-1/2 z-20 
                  bg-white rounded-lg shadow-xl border border-gray-200 p-4
                  ${isOpen ? 'w-80' : 'w-12'} transition-all duration-300 max-h-[80vh] overflow-y-auto`}
      initial={{ x: 100 }}
      animate={{ x: 0 }}
    >
      <button
        onClick={onToggle}
        className="w-full h-10 bg-blue-500 text-white rounded-lg hover:bg-blue-600 
                   transition-colors flex items-center justify-center mb-4"
      >
        {isOpen ? '→' : '←'}
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="space-y-4"
          >
            <div className="flex items-center justify-between">
              <h3 className="font-medium text-gray-700">Node Properties</h3>
              <button
                onClick={() => onDeleteNode(selectedNode.id)}
                className="text-red-500 hover:text-red-700 p-1"
                title="Delete node"
              >
                🗑️
              </button>
            </div>

            {/* Basic Properties */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Name
              </label>
              <input
                type="text"
                value={localNode.name || ''}
                onChange={(e) => handleFieldChange('name', e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                value={localNode.description || ''}
                onChange={(e) => handleFieldChange('description', e.target.value)}
                rows={3}
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Node Type Specific Properties */}
            {localNode.node_type === 'action' && (
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Action Type
                  </label>
                  <select
                    value={localNode.action_type || ''}
                    onChange={(e) => handleFieldChange('action_type', e.target.value)}
                    className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="content_generation">Content Generation</option>
                    <option value="api_call">API Call</option>
                    <option value="data_transformation">Data Transformation</option>
                    <option value="notification">Notification</option>
                  </select>
                </div>

                {localNode.action_type === 'content_generation' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Prompt Template
                    </label>
                    <textarea
                      value={localNode.action_config?.prompt || ''}
                      onChange={(e) => handleConfigChange('prompt', e.target.value)}
                      rows={3}
                      placeholder="Enter prompt template (use ${variable} for substitution)"
                      className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                )}

                {localNode.action_type === 'api_call' && (
                  <div className="space-y-2">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        URL
                      </label>
                      <input
                        type="text"
                        value={localNode.action_config?.url || ''}
                        onChange={(e) => handleConfigChange('url', e.target.value)}
                        placeholder="https://api.example.com/endpoint"
                        className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Method
                      </label>
                      <select
                        value={localNode.action_config?.method || 'GET'}
                        onChange={(e) => handleConfigChange('method', e.target.value)}
                        className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value="GET">GET</option>
                        <option value="POST">POST</option>
                        <option value="PUT">PUT</option>
                        <option value="DELETE">DELETE</option>
                      </select>
                    </div>
                  </div>
                )}
              </div>
            )}

            {localNode.node_type === 'condition' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Condition Expression
                </label>
                <input
                  type="text"
                  value={localNode.condition_expression || ''}
                  onChange={(e) => handleFieldChange('condition_expression', e.target.value)}
                  placeholder="e.g., ${status} equals approved"
                  className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <div className="text-xs text-gray-500 mt-1">
                  Use: equals, contains, greater_than operators
                </div>
              </div>
            )}

            {localNode.node_type === 'approval' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Timeout (hours)
                </label>
                <input
                  type="number"
                  value={localNode.approval_timeout_hours || 24}
                  onChange={(e) => handleFieldChange('approval_timeout_hours', parseInt(e.target.value))}
                  min="1"
                  max="168"
                  className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            )}

            {localNode.node_type === 'localization' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Target Languages
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {['en', 'es', 'fr', 'de', 'hi', 'zh', 'ar'].map(lang => (
                    <label key={lang} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={localNode.target_languages?.includes(lang) || false}
                        onChange={(e) => {
                          const currentLangs = localNode.target_languages || [];
                          const newLangs = e.target.checked
                            ? [...currentLangs, lang]
                            : currentLangs.filter(l => l !== lang);
                          handleFieldChange('target_languages', newLangs);
                        }}
                        className="mr-1"
                      />
                      <span className="text-sm">{lang.toUpperCase()}</span>
                    </label>
                  ))}
                </div>
              </div>
            )}

            {/* Position */}
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  X Position
                </label>
                <input
                  type="number"
                  value={Math.round(localNode.position_x || 0)}
                  onChange={(e) => handleFieldChange('position_x', parseInt(e.target.value))}
                  className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Y Position
                </label>
                <input
                  type="number"
                  value={Math.round(localNode.position_y || 0)}
                  onChange={(e) => handleFieldChange('position_y', parseInt(e.target.value))}
                  className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default function WorkflowBuilder({ 
  initialWorkflow = null, 
  onSave = () => {}, 
  onExecute = () => {},
  readOnly = false 
}) {
  const [nodes, setNodes] = useState(initialWorkflow?.nodes || []);
  const [connections, setConnections] = useState(initialWorkflow?.connections || []);
  const [selectedNodeId, setSelectedNodeId] = useState(null);
  const [connectingFrom, setConnectingFrom] = useState(null);
  const [paletteOpen, setPaletteOpen] = useState(true);
  const [propertiesOpen, setPropertiesOpen] = useState(true);
  const [workflowName, setWorkflowName] = useState(initialWorkflow?.name || 'New Workflow');

  const selectedNode = nodes.find(node => node.id === selectedNodeId);

  const handleAddNode = (newNode) => {
    if (readOnly) return;
    setNodes(prev => [...prev, newNode]);
    setSelectedNodeId(newNode.id);
  };

  const handleDragNode = (nodeId, x, y) => {
    if (readOnly) return;
    setNodes(prev => prev.map(node => 
      node.id === nodeId 
        ? { ...node, position_x: x, position_y: y }
        : node
    ));
  };

  const handleSelectNode = (nodeId) => {
    setSelectedNodeId(nodeId);
  };

  const handleUpdateNode = (updatedNode) => {
    if (readOnly) return;
    setNodes(prev => prev.map(node => 
      node.id === updatedNode.id ? updatedNode : node
    ));
  };

  const handleDeleteNode = (nodeId) => {
    if (readOnly) return;
    setNodes(prev => prev.filter(node => node.id !== nodeId));
    setConnections(prev => prev.filter(conn => 
      conn.from_node_id !== nodeId && conn.to_node_id !== nodeId
    ));
    setSelectedNodeId(null);
  };

  const handleConnect = (nodeId, type) => {
    if (readOnly) return;
    
    if (type === 'output') {
      if (connectingFrom === nodeId) {
        setConnectingFrom(null);
      } else {
        setConnectingFrom(nodeId);
      }
    } else if (type === 'input' && connectingFrom && connectingFrom !== nodeId) {
      // Create connection
      const newConnection = {
        id: `conn_${Date.now()}`,
        from_node_id: connectingFrom,
        to_node_id: nodeId,
        condition: 'success'
      };
      
      setConnections(prev => [...prev, newConnection]);
      setConnectingFrom(null);
    }
  };

  const handleSave = () => {
    const workflowData = {
      name: workflowName,
      nodes,
      connections,
      updated_at: new Date().toISOString()
    };
    onSave(workflowData);
  };

  const handleExecute = () => {
    const workflowData = {
      name: workflowName,
      nodes,
      connections
    };
    onExecute(workflowData);
  };

  return (
    <div className="h-screen bg-gray-50 relative overflow-hidden">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🔄</span>
            <input
              type="text"
              value={workflowName}
              onChange={(e) => setWorkflowName(e.target.value)}
              className="text-xl font-semibold bg-transparent border-none focus:outline-none focus:bg-gray-50 px-2 py-1 rounded"
              readOnly={readOnly}
            />
          </div>
          <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
            {nodes.length} nodes, {connections.length} connections
          </span>
        </div>

        <div className="flex items-center gap-2">
          {!readOnly && (
            <>
              <button
                onClick={handleSave}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              >
                💾 Save
              </button>
              <button
                onClick={handleExecute}
                className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
                disabled={nodes.length === 0}
              >
                ▶️ Execute
              </button>
            </>
          )}
        </div>
      </div>

      {/* Workflow Canvas */}
      <div className="workflow-canvas relative h-full overflow-auto bg-gray-50">
        {/* Grid Background */}
        <div 
          className="absolute inset-0 opacity-20"
          style={{
            backgroundImage: `
              linear-gradient(to right, #e5e7eb 1px, transparent 1px),
              linear-gradient(to bottom, #e5e7eb 1px, transparent 1px)
            `,
            backgroundSize: '20px 20px'
          }}
        />

        {/* Connections */}
        {connections.map(connection => {
          const fromNode = nodes.find(n => n.id === connection.from_node_id);
          const toNode = nodes.find(n => n.id === connection.to_node_id);
          return (
            <ConnectionLine
              key={connection.id}
              connection={connection}
              fromNode={fromNode}
              toNode={toNode}
            />
          );
        })}

        {/* Nodes */}
        {nodes.map(node => (
          <WorkflowNode
            key={node.id}
            node={node}
            onSelect={handleSelectNode}
            onDrag={handleDragNode}
            isSelected={node.id === selectedNodeId}
            onConnect={handleConnect}
            connections={connections}
          />
        ))}

        {/* Connection Preview */}
        {connectingFrom && (
          <div className="absolute inset-0 pointer-events-none">
            <div className="text-center mt-4 bg-blue-100 text-blue-800 px-4 py-2 rounded-lg inline-block">
              Click on a target node to create connection
            </div>
          </div>
        )}

        {/* Empty State */}
        {nodes.length === 0 && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center text-gray-500">
              <div className="text-6xl mb-4">🔄</div>
              <h3 className="text-xl font-medium mb-2">Build Your Workflow</h3>
              <p className="text-gray-400 mb-4">
                Add nodes from the palette to get started
              </p>
              {!readOnly && (
                <button
                  onClick={() => setPaletteOpen(true)}
                  className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                >
                  Open Node Palette
                </button>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Node Palette */}
      {!readOnly && (
        <NodePalette
          onAddNode={handleAddNode}
          isOpen={paletteOpen}
          onToggle={() => setPaletteOpen(!paletteOpen)}
        />
      )}

      {/* Properties Panel */}
      <PropertiesPanel
        selectedNode={selectedNode}
        onUpdateNode={handleUpdateNode}
        onDeleteNode={handleDeleteNode}
        isOpen={propertiesOpen}
        onToggle={() => setPropertiesOpen(!propertiesOpen)}
      />
    </div>
  );
}