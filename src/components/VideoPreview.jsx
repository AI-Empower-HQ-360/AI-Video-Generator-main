import React, { useRef, useEffect, useState } from 'react';
import { PlayIcon, PauseIcon, SpeakerWaveIcon, SpeakerXMarkIcon } from '@heroicons/react/24/outline';

const VideoPreview = ({ timeline, currentTime, isPlaying, onTimeUpdate }) => {
  const canvasRef = useRef(null);
  const videoRefs = useRef({});
  const audioRefs = useRef({});
  const [isMuted, setIsMuted] = useState(false);
  const animationRef = useRef(null);
  const lastTimeRef = useRef(0);

  // Initialize media elements
  useEffect(() => {
    timeline.forEach(clip => {
      if (clip.type === 'video' && !videoRefs.current[clip.id]) {
        const video = document.createElement('video');
        video.src = clip.url;
        video.muted = true;
        video.preload = 'metadata';
        videoRefs.current[clip.id] = video;
      } else if (clip.type === 'audio' && !audioRefs.current[clip.id]) {
        const audio = document.createElement('audio');
        audio.src = clip.url;
        audio.preload = 'metadata';
        audioRefs.current[clip.id] = audio;
      }
    });

    // Cleanup removed clips
    Object.keys(videoRefs.current).forEach(clipId => {
      if (!timeline.find(clip => clip.id === clipId)) {
        delete videoRefs.current[clipId];
      }
    });
    Object.keys(audioRefs.current).forEach(clipId => {
      if (!timeline.find(clip => clip.id === clipId)) {
        delete audioRefs.current[clipId];
      }
    });
  }, [timeline]);

  // Update media playback
  useEffect(() => {
    timeline.forEach(clip => {
      const clipStartTime = clip.startTime;
      const clipEndTime = clip.startTime + clip.duration;
      const isClipActive = currentTime >= clipStartTime && currentTime < clipEndTime;
      const clipCurrentTime = currentTime - clipStartTime;

      if (clip.type === 'video') {
        const video = videoRefs.current[clip.id];
        if (video && isClipActive) {
          video.currentTime = clipCurrentTime;
          if (isPlaying && video.paused) {
            video.play().catch(() => {}); // Ignore play errors
          } else if (!isPlaying && !video.paused) {
            video.pause();
          }
        } else if (video && !video.paused) {
          video.pause();
        }
      } else if (clip.type === 'audio') {
        const audio = audioRefs.current[clip.id];
        if (audio && isClipActive) {
          audio.currentTime = clipCurrentTime;
          audio.volume = isMuted ? 0 : clip.volume;
          if (isPlaying && audio.paused) {
            audio.play().catch(() => {}); // Ignore play errors
          } else if (!isPlaying && !audio.paused) {
            audio.pause();
          }
        } else if (audio && !audio.paused) {
          audio.pause();
        }
      }
    });
  }, [currentTime, isPlaying, timeline, isMuted]);

  // Animation loop for canvas rendering
  useEffect(() => {
    const renderFrame = () => {
      if (canvasRef.current) {
        renderCanvas();
      }
      if (isPlaying) {
        const now = Date.now();
        const deltaTime = (now - lastTimeRef.current) / 1000;
        lastTimeRef.current = now;
        onTimeUpdate(currentTime + deltaTime);
      }
      animationRef.current = requestAnimationFrame(renderFrame);
    };

    lastTimeRef.current = Date.now();
    animationRef.current = requestAnimationFrame(renderFrame);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isPlaying, currentTime, onTimeUpdate]);

  const renderCanvas = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const { width, height } = canvas;

    // Clear canvas
    ctx.fillStyle = '#000000';
    ctx.fillRect(0, 0, width, height);

    // Render active clips
    timeline.forEach(clip => {
      const clipStartTime = clip.startTime;
      const clipEndTime = clip.startTime + clip.duration;
      const isClipActive = currentTime >= clipStartTime && currentTime < clipEndTime;

      if (!isClipActive) return;

      if (clip.type === 'video') {
        const video = videoRefs.current[clip.id];
        if (video && video.videoWidth > 0) {
          // Calculate aspect ratio and fit video in canvas
          const videoAspect = video.videoWidth / video.videoHeight;
          const canvasAspect = width / height;
          
          let drawWidth, drawHeight, drawX, drawY;
          
          if (videoAspect > canvasAspect) {
            drawWidth = width;
            drawHeight = width / videoAspect;
            drawX = 0;
            drawY = (height - drawHeight) / 2;
          } else {
            drawWidth = height * videoAspect;
            drawHeight = height;
            drawX = (width - drawWidth) / 2;
            drawY = 0;
          }
          
          ctx.drawImage(video, drawX, drawY, drawWidth, drawHeight);
        }
      } else if (clip.type === 'image') {
        // For images, we would need to load them and draw them
        // This is a simplified version
        ctx.fillStyle = '#4B5563';
        ctx.fillRect(0, 0, width, height);
        ctx.fillStyle = '#FFFFFF';
        ctx.font = '24px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(clip.name, width / 2, height / 2);
      }
    });

    // Add watermark or overlay
    ctx.fillStyle = 'rgba(255, 255, 255, 0.1)';
    ctx.font = '14px Arial';
    ctx.textAlign = 'right';
    ctx.fillText('🕉️ AI Heart 360', width - 10, height - 10);
  };

  const handleCanvasClick = (event) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const progress = x / rect.width;
    const totalDuration = Math.max(...timeline.map(clip => clip.startTime + clip.duration));
    
    onTimeUpdate(progress * totalDuration);
  };

  return (
    <div className="h-full flex flex-col bg-black rounded-lg overflow-hidden">
      {/* Video Canvas */}
      <div className="flex-1 relative">
        <canvas
          ref={canvasRef}
          width={1920}
          height={1080}
          className="w-full h-full object-contain cursor-pointer"
          onClick={handleCanvasClick}
        />
        
        {/* Overlay Controls */}
        <div className="absolute bottom-4 left-4 right-4 bg-black/50 backdrop-blur-sm rounded-lg p-3">
          <div className="flex items-center justify-between">
            {/* Play Controls */}
            <div className="flex items-center space-x-3">
              <button
                onClick={() => onTimeUpdate(Math.max(0, currentTime - 10))}
                className="text-white hover:text-blue-400 transition-colors"
              >
                ⏪
              </button>
              
              <button
                onClick={() => {}} // This would be handled by parent
                className="w-10 h-10 flex items-center justify-center bg-white/20 hover:bg-white/30 rounded-full transition-colors"
              >
                {isPlaying ? (
                  <PauseIcon className="h-5 w-5 text-white" />
                ) : (
                  <PlayIcon className="h-5 w-5 text-white ml-0.5" />
                )}
              </button>
              
              <button
                onClick={() => onTimeUpdate(currentTime + 10)}
                className="text-white hover:text-blue-400 transition-colors"
              >
                ⏩
              </button>
            </div>

            {/* Time Display */}
            <div className="text-white text-sm">
              {Math.floor(currentTime / 60).toString().padStart(2, '0')}:
              {Math.floor(currentTime % 60).toString().padStart(2, '0')}
            </div>

            {/* Volume Control */}
            <button
              onClick={() => setIsMuted(!isMuted)}
              className="text-white hover:text-blue-400 transition-colors"
            >
              {isMuted ? (
                <SpeakerXMarkIcon className="h-5 w-5" />
              ) : (
                <SpeakerWaveIcon className="h-5 w-5" />
              )}
            </button>
          </div>

          {/* Progress Bar */}
          <div className="mt-3">
            <div className="relative h-1 bg-white/20 rounded-full cursor-pointer">
              <div
                className="absolute top-0 left-0 h-full bg-blue-500 rounded-full"
                style={{
                  width: `${timeline.length > 0 ? 
                    (currentTime / Math.max(...timeline.map(clip => clip.startTime + clip.duration))) * 100 : 0
                  }%`
                }}
              />
            </div>
          </div>
        </div>

        {/* Loading indicator */}
        {timeline.length === 0 && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-white/60 text-center">
              <div className="text-4xl mb-4">🎬</div>
              <div>Video preview will appear here</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default VideoPreview;