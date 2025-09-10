import React, { useState, useRef, useCallback } from 'react';
import { 
  PlayIcon, 
  PauseIcon, 
  ArrowUpTrayIcon, 
  ScissorsIcon,
  PlusIcon,
  EyeIcon
} from '@heroicons/react/24/outline';
import VideoTimeline from './VideoTimeline';
import VideoPreview from './VideoPreview';
import VideoTemplates from './VideoTemplates';

const VideoEditor = () => {
  const [currentProject, setCurrentProject] = useState({
    id: 'project-1',
    name: 'New Spiritual Video',
    duration: 0,
    timeline: []
  });
  
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [selectedClip, setSelectedClip] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [showTemplates, setShowTemplates] = useState(false);
  
  const fileInputRef = useRef(null);

  const handleFileUpload = useCallback((event) => {
    const files = Array.from(event.target.files);
    files.forEach(file => {
      if (file.type.startsWith('video/') || file.type.startsWith('audio/') || file.type.startsWith('image/')) {
        const newClip = {
          id: `clip-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          name: file.name,
          type: file.type.startsWith('video/') ? 'video' : file.type.startsWith('audio/') ? 'audio' : 'image',
          file: file,
          url: URL.createObjectURL(file),
          duration: file.type.startsWith('image/') ? 5 : 0, // Default 5s for images
          startTime: currentProject.timeline.reduce((sum, clip) => sum + clip.duration, 0),
          volume: 1,
          effects: []
        };
        
        setCurrentProject(prev => ({
          ...prev,
          timeline: [...prev.timeline, newClip],
          duration: prev.duration + newClip.duration
        }));
      }
    });
  }, [currentProject.timeline]);

  const handleDrop = useCallback((event) => {
    event.preventDefault();
    setIsDragging(false);
    
    const files = Array.from(event.dataTransfer.files);
    files.forEach(file => {
      if (file.type.startsWith('video/') || file.type.startsWith('audio/') || file.type.startsWith('image/')) {
        handleFileUpload({ target: { files: [file] } });
      }
    });
  }, [handleFileUpload]);

  const handleDragOver = useCallback((event) => {
    event.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((event) => {
    event.preventDefault();
    setIsDragging(false);
  }, []);

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handleTimeUpdate = (time) => {
    setCurrentTime(time);
  };

  const handleClipSelect = (clip) => {
    setSelectedClip(clip);
  };

  const handleClipDelete = (clipId) => {
    setCurrentProject(prev => ({
      ...prev,
      timeline: prev.timeline.filter(clip => clip.id !== clipId)
    }));
    if (selectedClip?.id === clipId) {
      setSelectedClip(null);
    }
  };

  const handleClipUpdate = (clipId, updates) => {
    setCurrentProject(prev => ({
      ...prev,
      timeline: prev.timeline.map(clip => 
        clip.id === clipId ? { ...clip, ...updates } : clip
      )
    }));
  };

  const applyTemplate = (template) => {
    setCurrentProject(prev => ({
      ...prev,
      ...template,
      id: prev.id,
      name: `${prev.name} - ${template.name}`
    }));
    setShowTemplates(false);
  };

  return (
    <div className="h-screen flex flex-col bg-gray-900 text-white">
      {/* Header */}
      <div className="bg-gray-800 p-4 border-b border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold">🎬 Video Editor</h1>
            <span className="text-gray-400">|</span>
            <input
              type="text"
              value={currentProject.name}
              onChange={(e) => setCurrentProject(prev => ({ ...prev, name: e.target.value }))}
              className="bg-gray-700 px-3 py-1 rounded border border-gray-600 focus:outline-none focus:border-blue-500"
            />
          </div>
          
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setShowTemplates(true)}
              className="flex items-center space-x-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors"
            >
              <EyeIcon className="h-4 w-4" />
              <span>Templates</span>
            </button>
            
            <button
              onClick={() => fileInputRef.current?.click()}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
            >
              <ArrowUpTrayIcon className="h-4 w-4" />
              <span>Import Media</span>
            </button>
            
            <button
              onClick={handlePlayPause}
              className="flex items-center space-x-2 px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg transition-colors"
            >
              {isPlaying ? <PauseIcon className="h-4 w-4" /> : <PlayIcon className="h-4 w-4" />}
              <span>{isPlaying ? 'Pause' : 'Play'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex">
        {/* Preview Area */}
        <div className="flex-1 p-4">
          <div
            className={`h-full rounded-lg border-2 border-dashed transition-colors ${
              isDragging 
                ? 'border-blue-400 bg-blue-500/10' 
                : 'border-gray-600 bg-gray-800'
            }`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
          >
            {currentProject.timeline.length > 0 ? (
              <VideoPreview
                timeline={currentProject.timeline}
                currentTime={currentTime}
                isPlaying={isPlaying}
                onTimeUpdate={handleTimeUpdate}
              />
            ) : (
              <div className="h-full flex items-center justify-center">
                <div className="text-center space-y-4">
                  <ArrowUpTrayIcon className="h-16 w-16 mx-auto text-gray-500" />
                  <div className="space-y-2">
                    <h3 className="text-xl font-semibold text-gray-300">
                      Drop media files here or click Import Media
                    </h3>
                    <p className="text-gray-500">
                      Supports video, audio, and image files
                    </p>
                  </div>
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
                  >
                    Select Files
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Properties Panel */}
        {selectedClip && (
          <div className="w-80 bg-gray-800 border-l border-gray-700 p-4">
            <h3 className="text-lg font-semibold mb-4">Clip Properties</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Name</label>
                <input
                  type="text"
                  value={selectedClip.name}
                  onChange={(e) => handleClipUpdate(selectedClip.id, { name: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded focus:outline-none focus:border-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Duration (seconds)</label>
                <input
                  type="number"
                  min="0.1"
                  step="0.1"
                  value={selectedClip.duration}
                  onChange={(e) => handleClipUpdate(selectedClip.id, { duration: parseFloat(e.target.value) })}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded focus:outline-none focus:border-blue-500"
                />
              </div>
              
              {selectedClip.type === 'audio' && (
                <div>
                  <label className="block text-sm font-medium mb-2">Volume</label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={selectedClip.volume}
                    onChange={(e) => handleClipUpdate(selectedClip.id, { volume: parseFloat(e.target.value) })}
                    className="w-full"
                  />
                  <span className="text-sm text-gray-400">{Math.round(selectedClip.volume * 100)}%</span>
                </div>
              )}
              
              <button
                onClick={() => handleClipDelete(selectedClip.id)}
                className="w-full px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg transition-colors"
              >
                Delete Clip
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Timeline */}
      <VideoTimeline
        timeline={currentProject.timeline}
        currentTime={currentTime}
        duration={currentProject.duration}
        selectedClip={selectedClip}
        onClipSelect={handleClipSelect}
        onClipUpdate={handleClipUpdate}
        onTimeChange={setCurrentTime}
      />

      {/* Hidden File Input */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept="video/*,audio/*,image/*"
        onChange={handleFileUpload}
        className="hidden"
      />

      {/* Templates Modal */}
      {showTemplates && (
        <VideoTemplates
          onApplyTemplate={applyTemplate}
          onClose={() => setShowTemplates(false)}
        />
      )}
    </div>
  );
};

export default VideoEditor;