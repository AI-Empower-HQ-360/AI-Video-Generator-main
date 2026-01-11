import React, { useState, useRef, useCallback } from 'react';
import { MusicalNoteIcon, VideoCameraIcon, PhotoIcon } from '@heroicons/react/24/outline';

const VideoTimeline = ({ 
  timeline, 
  currentTime, 
  duration, 
  selectedClip, 
  onClipSelect, 
  onClipUpdate, 
  onTimeChange 
}) => {
  const [dragData, setDragData] = useState(null);
  const timelineRef = useRef(null);
  const pixelsPerSecond = 50; // Scale factor for timeline
  
  const getClipIcon = (type) => {
    switch (type) {
      case 'video': return VideoCameraIcon;
      case 'audio': return MusicalNoteIcon;
      case 'image': return PhotoIcon;
      default: return VideoCameraIcon;
    }
  };

  const getClipColor = (type) => {
    switch (type) {
      case 'video': return 'bg-blue-500';
      case 'audio': return 'bg-green-500';
      case 'image': return 'bg-purple-500';
      default: return 'bg-gray-500';
    }
  };

  const handleTimelineClick = (event) => {
    if (timelineRef.current) {
      const rect = timelineRef.current.getBoundingClientRect();
      const x = event.clientX - rect.left;
      const time = x / pixelsPerSecond;
      onTimeChange(Math.max(0, Math.min(time, duration)));
    }
  };

  const handleClipDragStart = (event, clip) => {
    setDragData({
      clipId: clip.id,
      startX: event.clientX,
      startTime: clip.startTime
    });
    event.dataTransfer.effectAllowed = 'move';
  };

  const handleClipDragOver = (event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  };

  const handleClipDrop = (event) => {
    event.preventDefault();
    
    if (!dragData || !timelineRef.current) return;
    
    const rect = timelineRef.current.getBoundingClientRect();
    const dropX = event.clientX - rect.left;
    const newStartTime = Math.max(0, dropX / pixelsPerSecond);
    
    onClipUpdate(dragData.clipId, { startTime: newStartTime });
    setDragData(null);
  };

  const handleClipResize = (clipId, edge, deltaX) => {
    const clip = timeline.find(c => c.id === clipId);
    if (!clip) return;

    const deltaTime = deltaX / pixelsPerSecond;
    
    if (edge === 'left') {
      const newStartTime = Math.max(0, clip.startTime + deltaTime);
      const newDuration = clip.duration - (newStartTime - clip.startTime);
      if (newDuration > 0.1) {
        onClipUpdate(clipId, { 
          startTime: newStartTime, 
          duration: Math.max(0.1, newDuration) 
        });
      }
    } else if (edge === 'right') {
      const newDuration = Math.max(0.1, clip.duration + deltaTime);
      onClipUpdate(clipId, { duration: newDuration });
    }
  };

  const ResizeHandle = ({ position, onMouseDown }) => (
    <div
      className={`absolute top-0 bottom-0 w-2 cursor-ew-resize bg-white/30 hover:bg-white/50 ${
        position === 'left' ? 'left-0' : 'right-0'
      }`}
      onMouseDown={onMouseDown}
    />
  );

  return (
    <div className="bg-gray-800 border-t border-gray-700 p-4">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-lg font-semibold">Timeline</h3>
        <div className="text-sm text-gray-400">
          Duration: {duration.toFixed(1)}s | Time: {currentTime.toFixed(1)}s
        </div>
      </div>
      
      {/* Timeline ruler */}
      <div className="mb-2">
        <div className="flex items-center text-xs text-gray-400 mb-1">
          {Array.from({ length: Math.ceil(duration / 5) + 1 }, (_, i) => (
            <div 
              key={i} 
              className="flex-none" 
              style={{ width: `${5 * pixelsPerSecond}px` }}
            >
              {i * 5}s
            </div>
          ))}
        </div>
        <div className="h-px bg-gray-600" />
      </div>

      {/* Timeline container */}
      <div 
        ref={timelineRef}
        className="relative h-32 bg-gray-900 rounded-lg border border-gray-600 overflow-hidden cursor-pointer"
        onClick={handleTimelineClick}
        onDragOver={handleClipDragOver}
        onDrop={handleClipDrop}
        style={{ minWidth: `${Math.max(800, duration * pixelsPerSecond)}px` }}
      >
        {/* Playhead */}
        <div
          className="absolute top-0 bottom-0 w-0.5 bg-red-500 z-20 pointer-events-none"
          style={{ left: `${currentTime * pixelsPerSecond}px` }}
        >
          <div className="absolute -top-2 -left-2 w-4 h-4 bg-red-500 rounded-full" />
        </div>

        {/* Video track */}
        <div className="absolute top-2 left-0 right-0 h-10 border border-gray-600 rounded bg-gray-800">
          <div className="absolute left-2 top-1 text-xs text-gray-400">Video</div>
          {timeline
            .filter(clip => clip.type === 'video' || clip.type === 'image')
            .map(clip => {
              const Icon = getClipIcon(clip.type);
              const isSelected = selectedClip?.id === clip.id;
              
              return (
                <div
                  key={clip.id}
                  className={`absolute top-1 h-8 rounded cursor-move border-2 transition-all ${
                    getClipColor(clip.type)
                  } ${
                    isSelected ? 'border-yellow-400 shadow-lg' : 'border-transparent'
                  }`}
                  style={{
                    left: `${clip.startTime * pixelsPerSecond}px`,
                    width: `${clip.duration * pixelsPerSecond}px`,
                  }}
                  draggable
                  onDragStart={(e) => handleClipDragStart(e, clip)}
                  onClick={(e) => {
                    e.stopPropagation();
                    onClipSelect(clip);
                  }}
                >
                  <div className="flex items-center justify-between h-full px-2">
                    <div className="flex items-center space-x-1">
                      <Icon className="h-4 w-4 text-white" />
                      <span className="text-xs text-white truncate max-w-24">
                        {clip.name}
                      </span>
                    </div>
                  </div>
                  
                  {/* Resize handles */}
                  {isSelected && (
                    <>
                      <ResizeHandle 
                        position="left" 
                        onMouseDown={(e) => {
                          e.stopPropagation();
                          // Implement resize logic here
                        }}
                      />
                      <ResizeHandle 
                        position="right" 
                        onMouseDown={(e) => {
                          e.stopPropagation();
                          // Implement resize logic here
                        }}
                      />
                    </>
                  )}
                </div>
              );
            })}
        </div>

        {/* Audio track */}
        <div className="absolute top-14 left-0 right-0 h-10 border border-gray-600 rounded bg-gray-800">
          <div className="absolute left-2 top-1 text-xs text-gray-400">Audio</div>
          {timeline
            .filter(clip => clip.type === 'audio')
            .map(clip => {
              const Icon = getClipIcon(clip.type);
              const isSelected = selectedClip?.id === clip.id;
              
              return (
                <div
                  key={clip.id}
                  className={`absolute top-1 h-8 rounded cursor-move border-2 transition-all ${
                    getClipColor(clip.type)
                  } ${
                    isSelected ? 'border-yellow-400 shadow-lg' : 'border-transparent'
                  }`}
                  style={{
                    left: `${clip.startTime * pixelsPerSecond}px`,
                    width: `${clip.duration * pixelsPerSecond}px`,
                  }}
                  draggable
                  onDragStart={(e) => handleClipDragStart(e, clip)}
                  onClick={(e) => {
                    e.stopPropagation();
                    onClipSelect(clip);
                  }}
                >
                  <div className="flex items-center justify-between h-full px-2">
                    <div className="flex items-center space-x-1">
                      <Icon className="h-4 w-4 text-white" />
                      <span className="text-xs text-white truncate max-w-24">
                        {clip.name}
                      </span>
                    </div>
                    <div className="text-xs text-white/70">
                      {Math.round(clip.volume * 100)}%
                    </div>
                  </div>
                  
                  {/* Resize handles */}
                  {isSelected && (
                    <>
                      <ResizeHandle 
                        position="left" 
                        onMouseDown={(e) => {
                          e.stopPropagation();
                          // Implement resize logic here
                        }}
                      />
                      <ResizeHandle 
                        position="right" 
                        onMouseDown={(e) => {
                          e.stopPropagation();
                          // Implement resize logic here
                        }}
                      />
                    </>
                  )}
                </div>
              );
            })}
        </div>
      </div>

      {/* Timeline controls */}
      <div className="mt-4 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm transition-colors">
            + Add Track
          </button>
          <button className="px-3 py-1 bg-green-600 hover:bg-green-700 rounded text-sm transition-colors">
            Split
          </button>
          <button className="px-3 py-1 bg-red-600 hover:bg-red-700 rounded text-sm transition-colors">
            Cut
          </button>
        </div>
        
        <div className="flex items-center space-x-2 text-sm">
          <span>Zoom:</span>
          <button className="px-2 py-1 bg-gray-700 hover:bg-gray-600 rounded">-</button>
          <span>50px/s</span>
          <button className="px-2 py-1 bg-gray-700 hover:bg-gray-600 rounded">+</button>
        </div>
      </div>
    </div>
  );
};

export default VideoTimeline;