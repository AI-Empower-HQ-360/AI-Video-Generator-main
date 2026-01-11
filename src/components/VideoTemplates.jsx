import React, { useState } from 'react';
import { XMarkIcon, PlayIcon, EyeIcon } from '@heroicons/react/24/outline';

const VideoTemplates = ({ onApplyTemplate, onClose }) => {
  const [selectedCategory, setSelectedCategory] = useState('spiritual');

  const templates = {
    spiritual: [
      {
        id: 'meditation-guide',
        name: 'Meditation Guide',
        description: 'Peaceful meditation session with calming music and gentle transitions',
        thumbnail: '🧘‍♀️',
        duration: '5-15 min',
        timeline: [
          {
            id: 'intro',
            name: 'Meditation Intro',
            type: 'image',
            duration: 3,
            startTime: 0,
            effects: ['fade-in']
          },
          {
            id: 'background-music',
            name: 'Calming Music',
            type: 'audio',
            duration: 600,
            startTime: 0,
            volume: 0.3
          }
        ],
        style: {
          background: 'linear-gradient(to bottom, #667eea, #764ba2)',
          textColor: '#ffffff',
          accentColor: '#FFD700'
        }
      },
      {
        id: 'spiritual-journey',
        name: 'Spiritual Journey',
        description: 'A guided spiritual journey with Sanskrit chants and visuals',
        thumbnail: '🕉️',
        duration: '10-20 min',
        timeline: [
          {
            id: 'opening-prayer',
            name: 'Opening Prayer',
            type: 'audio',
            duration: 30,
            startTime: 0,
            volume: 0.8
          }
        ],
        style: {
          background: 'linear-gradient(to bottom, #f093fb, #f5576c)',
          textColor: '#ffffff',
          accentColor: '#FFD700'
        }
      },
      {
        id: 'mindfulness-session',
        name: 'Mindfulness Session',
        description: 'Focused mindfulness practice with breathing exercises',
        thumbnail: '🌱',
        duration: '15-30 min',
        timeline: [],
        style: {
          background: 'linear-gradient(to bottom, #4facfe, #00f2fe)',
          textColor: '#ffffff',
          accentColor: '#00ff88'
        }
      }
    ],
    educational: [
      {
        id: 'lesson-template',
        name: 'Educational Lesson',
        description: 'Clean template for educational content with slides and narration',
        thumbnail: '📚',
        duration: '5-60 min',
        timeline: [],
        style: {
          background: 'linear-gradient(to bottom, #667eea, #764ba2)',
          textColor: '#333333',
          accentColor: '#3b82f6'
        }
      },
      {
        id: 'presentation',
        name: 'Presentation',
        description: 'Professional presentation template with smooth transitions',
        thumbnail: '📊',
        duration: '10-45 min',
        timeline: [],
        style: {
          background: 'linear-gradient(to bottom, #fa709a, #fee140)',
          textColor: '#ffffff',
          accentColor: '#ff6b6b'
        }
      }
    ],
    creative: [
      {
        id: 'artistic-vision',
        name: 'Artistic Vision',
        description: 'Creative template with artistic transitions and effects',
        thumbnail: '🎨',
        duration: '3-10 min',
        timeline: [],
        style: {
          background: 'linear-gradient(to bottom, #a8edea, #fed6e3)',
          textColor: '#2d3748',
          accentColor: '#ed64a6'
        }
      },
      {
        id: 'storytelling',
        name: 'Storytelling',
        description: 'Narrative-driven template perfect for storytelling',
        thumbnail: '📖',
        duration: '5-30 min',
        timeline: [],
        style: {
          background: 'linear-gradient(to bottom, #d299c2, #fef9d7)',
          textColor: '#4a5568',
          accentColor: '#9f7aea'
        }
      }
    ]
  };

  const categories = [
    { id: 'spiritual', name: 'Spiritual', icon: '🕉️' },
    { id: 'educational', name: 'Educational', icon: '📚' },
    { id: 'creative', name: 'Creative', icon: '🎨' }
  ];

  const handleApplyTemplate = (template) => {
    onApplyTemplate({
      ...template,
      timeline: template.timeline.map(clip => ({
        ...clip,
        id: `${clip.id}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      }))
    });
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-gray-900 rounded-2xl max-w-6xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-gray-800 p-6 border-b border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-white">Video Templates</h2>
              <p className="text-gray-400 mt-1">Choose a template to get started quickly</p>
            </div>
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-white transition-colors"
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>
        </div>

        <div className="flex h-[600px]">
          {/* Categories Sidebar */}
          <div className="w-64 bg-gray-800 border-r border-gray-700 p-4">
            <h3 className="text-lg font-semibold text-white mb-4">Categories</h3>
            <div className="space-y-2">
              {categories.map(category => (
                <button
                  key={category.id}
                  onClick={() => setSelectedCategory(category.id)}
                  className={`w-full flex items-center space-x-3 p-3 rounded-lg transition-colors text-left ${
                    selectedCategory === category.id
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-300 hover:bg-gray-700'
                  }`}
                >
                  <span className="text-xl">{category.icon}</span>
                  <span>{category.name}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Templates Grid */}
          <div className="flex-1 p-6 overflow-y-auto">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {templates[selectedCategory]?.map(template => (
                <div
                  key={template.id}
                  className="bg-gray-800 rounded-xl overflow-hidden border border-gray-700 hover:border-gray-600 transition-all duration-200 hover:scale-105"
                >
                  {/* Template Preview */}
                  <div 
                    className="h-40 flex items-center justify-center text-6xl"
                    style={{ background: template.style.background }}
                  >
                    <span className="drop-shadow-lg">{template.thumbnail}</span>
                  </div>

                  {/* Template Info */}
                  <div className="p-4">
                    <div className="flex items-start justify-between mb-2">
                      <h4 className="text-lg font-semibold text-white">{template.name}</h4>
                      <span className="text-xs text-gray-400 bg-gray-700 px-2 py-1 rounded">
                        {template.duration}
                      </span>
                    </div>
                    
                    <p className="text-gray-400 text-sm mb-4 line-clamp-2">
                      {template.description}
                    </p>

                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleApplyTemplate(template)}
                        className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
                      >
                        Use Template
                      </button>
                      
                      <button className="p-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors">
                        <EyeIcon className="h-5 w-5" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {templates[selectedCategory]?.length === 0 && (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">🚧</div>
                <h3 className="text-xl font-semibold text-gray-300 mb-2">Coming Soon</h3>
                <p className="text-gray-500">More templates for this category are being prepared.</p>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="bg-gray-800 p-4 border-t border-gray-700">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-400">
              {templates[selectedCategory]?.length || 0} templates available
            </div>
            <div className="flex space-x-2">
              <button
                onClick={onClose}
                className="px-4 py-2 text-gray-300 hover:text-white transition-colors"
              >
                Cancel
              </button>
              <button className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors">
                Create Custom Template
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VideoTemplates;