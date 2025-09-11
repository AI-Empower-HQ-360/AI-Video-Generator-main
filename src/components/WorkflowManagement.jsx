import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import WorkflowBuilder from './WorkflowBuilder';

// Workflow List Component
const WorkflowList = ({ workflows, onSelect, onCreate, onDelete, onExecute }) => {
  const [filter, setFilter] = useState('all');
  const [sortBy, setSortBy] = useState('created_at');

  const filteredWorkflows = workflows.filter(workflow => {
    if (filter === 'all') return true;
    if (filter === 'templates') return workflow.is_template;
    if (filter === 'active') return workflow.status === 'active';
    if (filter === 'draft') return workflow.status === 'draft';
    return true;
  });

  const sortedWorkflows = [...filteredWorkflows].sort((a, b) => {
    switch (sortBy) {
      case 'name':
        return a.name.localeCompare(b.name);
      case 'category':
        return (a.category || '').localeCompare(b.category || '');
      case 'created_at':
      default:
        return new Date(b.created_at) - new Date(a.created_at);
    }
  });

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'draft': return 'bg-yellow-100 text-yellow-800';
      case 'inactive': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'content_creation': return '📝';
      case 'approval': return '✅';
      case 'localization': return '🌍';
      case 'scheduling': return '⏰';
      default: return '🔄';
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold text-gray-900">🔄 Workflow Automation</h1>
          <button
            onClick={onCreate}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center gap-2"
          >
            <span>➕</span>
            Create Workflow
          </button>
        </div>

        {/* Filters and Sorting */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium text-gray-700">Filter:</label>
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="px-3 py-1 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Workflows</option>
              <option value="active">Active</option>
              <option value="draft">Draft</option>
              <option value="templates">Templates</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <label className="text-sm font-medium text-gray-700">Sort by:</label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-3 py-1 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="created_at">Created Date</option>
              <option value="name">Name</option>
              <option value="category">Category</option>
            </select>
          </div>

          <div className="text-sm text-gray-500">
            {sortedWorkflows.length} workflow{sortedWorkflows.length !== 1 ? 's' : ''}
          </div>
        </div>
      </div>

      {/* Workflow Grid */}
      <div className="flex-1 overflow-auto p-6">
        {sortedWorkflows.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🔄</div>
            <h3 className="text-xl font-medium text-gray-600 mb-2">No workflows found</h3>
            <p className="text-gray-400 mb-6">
              {filter === 'all' 
                ? 'Create your first workflow to get started'
                : `No workflows match the current filter: ${filter}`
              }
            </p>
            <button
              onClick={onCreate}
              className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              Create Your First Workflow
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sortedWorkflows.map(workflow => (
              <motion.div
                key={workflow.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => onSelect(workflow)}
              >
                <div className="p-6">
                  {/* Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">
                        {getCategoryIcon(workflow.category)}
                      </span>
                      <div>
                        <h3 className="font-medium text-gray-900 line-clamp-1">
                          {workflow.name}
                        </h3>
                        <div className="flex items-center gap-2 mt-1">
                          <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(workflow.status)}`}>
                            {workflow.status}
                          </span>
                          {workflow.is_template && (
                            <span className="px-2 py-1 text-xs bg-purple-100 text-purple-800 rounded-full">
                              Template
                            </span>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-1">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onExecute(workflow);
                        }}
                        className="p-1 text-green-600 hover:bg-green-50 rounded"
                        title="Execute workflow"
                      >
                        ▶️
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onDelete(workflow.id);
                        }}
                        className="p-1 text-red-600 hover:bg-red-50 rounded"
                        title="Delete workflow"
                      >
                        🗑️
                      </button>
                    </div>
                  </div>

                  {/* Description */}
                  {workflow.description && (
                    <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                      {workflow.description}
                    </p>
                  )}

                  {/* Stats */}
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <div className="flex items-center gap-4">
                      <span>{workflow.nodes?.length || 0} nodes</span>
                      {workflow.is_template && (
                        <span>⭐ {workflow.rating_average?.toFixed(1) || '0.0'}</span>
                      )}
                    </div>
                    <div>
                      {new Date(workflow.created_at).toLocaleDateString()}
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

// Template Marketplace Component
const TemplateMarketplace = ({ templates, onDownload, onRate, onClose }) => {
  const [filter, setFilter] = useState('all');
  const [sortBy, setSortBy] = useState('rating');

  const filteredTemplates = templates.filter(template => {
    if (filter === 'all') return true;
    return template.template_category === filter;
  });

  const sortedTemplates = [...filteredTemplates].sort((a, b) => {
    switch (sortBy) {
      case 'rating':
        return (b.rating_average || 0) - (a.rating_average || 0);
      case 'downloads':
        return (b.downloads_count || 0) - (a.downloads_count || 0);
      case 'name':
        return a.name.localeCompare(b.name);
      default:
        return new Date(b.created_at) - new Date(a.created_at);
    }
  });

  const categories = [...new Set(templates.map(t => t.template_category).filter(Boolean))];

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="bg-white rounded-xl shadow-xl w-full max-w-4xl h-[80vh] flex flex-col"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">🏪 Template Marketplace</h2>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 rounded-lg"
          >
            ✕
          </button>
        </div>

        {/* Filters */}
        <div className="p-6 border-b border-gray-100">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <label className="text-sm font-medium text-gray-700">Category:</label>
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className="px-3 py-1 border border-gray-300 rounded-lg text-sm"
              >
                <option value="all">All Categories</option>
                {categories.map(category => (
                  <option key={category} value={category}>
                    {category.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex items-center gap-2">
              <label className="text-sm font-medium text-gray-700">Sort by:</label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-3 py-1 border border-gray-300 rounded-lg text-sm"
              >
                <option value="rating">Rating</option>
                <option value="downloads">Downloads</option>
                <option value="name">Name</option>
                <option value="created_at">Date Created</option>
              </select>
            </div>
          </div>
        </div>

        {/* Templates Grid */}
        <div className="flex-1 overflow-auto p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {sortedTemplates.map(template => (
              <div
                key={template.id}
                className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="font-medium text-gray-900">{template.name}</h3>
                    <p className="text-sm text-gray-500 capitalize">
                      {template.template_category?.replace('_', ' ')}
                    </p>
                  </div>
                  <div className="text-right text-sm">
                    <div className="flex items-center gap-1 text-yellow-500">
                      ⭐ {template.rating_average?.toFixed(1) || '0.0'}
                      <span className="text-gray-400">({template.rating_count || 0})</span>
                    </div>
                    <div className="text-gray-500">
                      📥 {template.downloads_count || 0} downloads
                    </div>
                  </div>
                </div>

                <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                  {template.description}
                </p>

                <div className="flex items-center justify-between">
                  <div className="text-sm text-gray-500">
                    {template.nodes?.length || 0} nodes
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => onRate(template)}
                      className="px-3 py-1 text-sm text-blue-600 hover:bg-blue-50 rounded"
                    >
                      Rate
                    </button>
                    <button
                      onClick={() => onDownload(template)}
                      className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
                    >
                      Download
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};

// Workflow Execution Modal
const WorkflowExecutionModal = ({ workflow, onExecute, onClose }) => {
  const [inputData, setInputData] = useState({});
  const [isExecuting, setIsExecuting] = useState(false);

  const handleExecute = async () => {
    setIsExecuting(true);
    try {
      await onExecute(workflow, inputData);
      onClose();
    } catch (error) {
      console.error('Execution failed:', error);
    } finally {
      setIsExecuting(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="bg-white rounded-xl shadow-xl w-full max-w-lg"
      >
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Execute Workflow</h2>
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-gray-600 rounded-lg"
            >
              ✕
            </button>
          </div>

          <div className="mb-4">
            <h3 className="font-medium text-gray-700 mb-2">{workflow.name}</h3>
            <p className="text-sm text-gray-600">{workflow.description}</p>
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Input Data (JSON)
            </label>
            <textarea
              value={JSON.stringify(inputData, null, 2)}
              onChange={(e) => {
                try {
                  setInputData(JSON.parse(e.target.value));
                } catch {
                  // Invalid JSON, keep current state
                }
              }}
              placeholder='{"topic": "meditation", "guru_type": "spiritual"}'
              rows={6}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
            />
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              onClick={handleExecute}
              disabled={isExecuting}
              className="flex-1 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:opacity-50"
            >
              {isExecuting ? '🔄 Executing...' : '▶️ Execute'}
            </button>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};

// Main Workflow Management Component
export default function WorkflowManagement() {
  const [view, setView] = useState('list'); // list, builder, marketplace
  const [workflows, setWorkflows] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState(null);
  const [showMarketplace, setShowMarketplace] = useState(false);
  const [showExecutionModal, setShowExecutionModal] = useState(false);
  const [executingWorkflow, setExecutingWorkflow] = useState(null);
  const [loading, setLoading] = useState(true);

  // Load workflows and templates
  useEffect(() => {
    loadWorkflows();
    loadTemplates();
  }, []);

  const loadWorkflows = async () => {
    try {
      // Simulate API call
      setLoading(true);
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const mockWorkflows = [
        {
          id: '1',
          name: 'Daily Content Creation',
          description: 'Automated workflow for generating daily spiritual content',
          category: 'content_creation',
          status: 'active',
          is_template: false,
          created_at: '2024-01-15T10:00:00Z',
          nodes: Array(5).fill().map((_, i) => ({ id: i }))
        },
        {
          id: '2',
          name: 'Approval Chain Template',
          description: 'Multi-level approval process with escalation',
          category: 'approval',
          status: 'active',
          is_template: true,
          template_category: 'approval',
          rating_average: 4.5,
          rating_count: 12,
          downloads_count: 45,
          created_at: '2024-01-10T14:30:00Z',
          nodes: Array(6).fill().map((_, i) => ({ id: i }))
        }
      ];
      
      setWorkflows(mockWorkflows);
    } catch (error) {
      console.error('Failed to load workflows:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadTemplates = async () => {
    try {
      const mockTemplates = [
        {
          id: 't1',
          name: 'Content Creation Workflow',
          description: 'Automated content generation with approval and publishing',
          template_category: 'content',
          rating_average: 4.2,
          rating_count: 8,
          downloads_count: 23,
          created_at: '2024-01-08T09:00:00Z',
          nodes: Array(6).fill().map((_, i) => ({ id: i }))
        },
        {
          id: 't2',
          name: 'Localization Pipeline',
          description: 'Multi-language content translation and publishing',
          template_category: 'localization',
          rating_average: 4.7,
          rating_count: 15,
          downloads_count: 67,
          created_at: '2024-01-05T16:20:00Z',
          nodes: Array(4).fill().map((_, i) => ({ id: i }))
        }
      ];
      
      setTemplates(mockTemplates);
    } catch (error) {
      console.error('Failed to load templates:', error);
    }
  };

  const handleCreateWorkflow = () => {
    setSelectedWorkflow(null);
    setView('builder');
  };

  const handleSelectWorkflow = (workflow) => {
    setSelectedWorkflow(workflow);
    setView('builder');
  };

  const handleDeleteWorkflow = (workflowId) => {
    if (window.confirm('Are you sure you want to delete this workflow?')) {
      setWorkflows(prev => prev.filter(w => w.id !== workflowId));
    }
  };

  const handleExecuteWorkflow = (workflow) => {
    setExecutingWorkflow(workflow);
    setShowExecutionModal(true);
  };

  const handleSaveWorkflow = (workflowData) => {
    if (selectedWorkflow) {
      // Update existing workflow
      setWorkflows(prev => prev.map(w => 
        w.id === selectedWorkflow.id 
          ? { ...w, ...workflowData, updated_at: new Date().toISOString() }
          : w
      ));
    } else {
      // Create new workflow
      const newWorkflow = {
        id: `wf_${Date.now()}`,
        ...workflowData,
        status: 'draft',
        created_at: new Date().toISOString()
      };
      setWorkflows(prev => [newWorkflow, ...prev]);
      setSelectedWorkflow(newWorkflow);
    }
  };

  const handleDownloadTemplate = (template) => {
    // Create workflow from template
    const newWorkflow = {
      ...template,
      id: `wf_${Date.now()}`,
      name: `${template.name} - Copy`,
      is_template: false,
      status: 'draft',
      created_at: new Date().toISOString()
    };
    
    setWorkflows(prev => [newWorkflow, ...prev]);
    setShowMarketplace(false);
    setSelectedWorkflow(newWorkflow);
    setView('builder');
  };

  const handleRateTemplate = (template) => {
    // Simulate rating - in real app, show rating modal
    alert(`Rating template: ${template.name}`);
  };

  const handleExecuteFromModal = async (workflow, inputData) => {
    // Simulate workflow execution
    console.log('Executing workflow:', workflow.name, 'with input:', inputData);
    await new Promise(resolve => setTimeout(resolve, 2000));
    alert(`Workflow "${workflow.name}" executed successfully!`);
  };

  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-4xl mb-4">🔄</div>
          <div className="text-gray-600">Loading workflows...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen bg-gray-50">
      {view === 'list' && (
        <div className="h-full flex flex-col">
          <WorkflowList
            workflows={workflows}
            onSelect={handleSelectWorkflow}
            onCreate={handleCreateWorkflow}
            onDelete={handleDeleteWorkflow}
            onExecute={handleExecuteWorkflow}
          />
          
          {/* Floating Action Buttons */}
          <div className="fixed bottom-6 right-6 flex flex-col gap-3">
            <button
              onClick={() => setShowMarketplace(true)}
              className="w-12 h-12 bg-purple-500 text-white rounded-full shadow-lg hover:bg-purple-600 transition-colors flex items-center justify-center"
              title="Template Marketplace"
            >
              🏪
            </button>
          </div>
        </div>
      )}

      {view === 'builder' && (
        <div className="h-full flex flex-col">
          <div className="bg-white border-b border-gray-200 p-4 flex items-center justify-between">
            <button
              onClick={() => setView('list')}
              className="flex items-center gap-2 text-gray-600 hover:text-gray-800"
            >
              ← Back to Workflows
            </button>
          </div>
          
          <div className="flex-1">
            <WorkflowBuilder
              initialWorkflow={selectedWorkflow}
              onSave={handleSaveWorkflow}
              onExecute={(workflowData) => {
                const workflow = { ...selectedWorkflow, ...workflowData };
                handleExecuteWorkflow(workflow);
              }}
              readOnly={false}
            />
          </div>
        </div>
      )}

      {/* Modals */}
      <AnimatePresence>
        {showMarketplace && (
          <TemplateMarketplace
            templates={templates}
            onDownload={handleDownloadTemplate}
            onRate={handleRateTemplate}
            onClose={() => setShowMarketplace(false)}
          />
        )}
        
        {showExecutionModal && executingWorkflow && (
          <WorkflowExecutionModal
            workflow={executingWorkflow}
            onExecute={handleExecuteFromModal}
            onClose={() => {
              setShowExecutionModal(false);
              setExecutingWorkflow(null);
            }}
          />
        )}
      </AnimatePresence>
    </div>
  );
}