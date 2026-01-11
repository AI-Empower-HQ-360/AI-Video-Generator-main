import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'react-hot-toast';

const VideoProcessor = () => {
  const [videos, setVideos] = useState([]);
  const [selectedVideo, setSelectedVideo] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [activeTab, setActiveTab] = useState('upload');
  const [voices, setVoices] = useState({});
  const [enhancementPresets, setEnhancementPresets] = useState({});
  const [analytics, setAnalytics] = useState({});

  // Load available options on component mount
  useEffect(() => {
    loadVoices();
    loadEnhancementPresets();
  }, []);

  const loadVoices = async () => {
    try {
      const response = await fetch('/api/video/voices');
      const data = await response.json();
      if (data.success) {
        setVoices(data.voices);
      }
    } catch (error) {
      console.error('Error loading voices:', error);
    }
  };

  const loadEnhancementPresets = async () => {
    try {
      const response = await fetch('/api/video/enhancement-presets');
      const data = await response.json();
      if (data.success) {
        setEnhancementPresets(data.presets);
      }
    } catch (error) {
      console.error('Error loading presets:', error);
    }
  };

  const handleVideoUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('video_file', file);
    formData.append('metadata', JSON.stringify({
      description: 'Spiritual video content',
      category: 'meditation'
    }));

    setProcessing(true);
    
    try {
      const response = await fetch('/api/video/upload', {
        method: 'POST',
        body: formData
      });
      
      const result = await response.json();
      
      if (result.success) {
        toast.success('Video uploaded successfully!');
        setVideos(prev => [...prev, {
          id: result.video_id,
          name: result.upload_info.original_filename,
          metadata: result.metadata,
          uploaded_at: new Date().toISOString()
        }]);
      } else {
        toast.error(result.error);
      }
    } catch (error) {
      toast.error('Upload failed');
      console.error('Upload error:', error);
    } finally {
      setProcessing(false);
    }
  };

  const trimVideo = async (videoId, startTime, endTime) => {
    setProcessing(true);
    
    try {
      const response = await fetch('/api/video/trim', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          video_id: videoId,
          start_time: parseFloat(startTime),
          end_time: parseFloat(endTime)
        })
      });
      
      const result = await response.json();
      
      if (result.success) {
        toast.success('Video trimmed successfully!');
        return result;
      } else {
        toast.error(result.error);
      }
    } catch (error) {
      toast.error('Trimming failed');
      console.error('Trim error:', error);
    } finally {
      setProcessing(false);
    }
  };

  const enhanceVideo = async (videoId, preset) => {
    setProcessing(true);
    
    try {
      const response = await fetch('/api/video/enhance', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          video_id: videoId,
          enhancement_preset: preset
        })
      });
      
      const result = await response.json();
      
      if (result.success) {
        toast.success('Video enhanced successfully!');
        return result;
      } else {
        toast.error(result.error);
      }
    } catch (error) {
      toast.error('Enhancement failed');
      console.error('Enhancement error:', error);
    } finally {
      setProcessing(false);
    }
  };

  const generateSubtitles = async (videoId, language = 'en') => {
    setProcessing(true);
    
    try {
      const response = await fetch('/api/video/subtitles/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          video_id: videoId,
          language: language
        })
      });
      
      const result = await response.json();
      
      if (result.success) {
        toast.success('Subtitles generated successfully!');
        return result;
      } else {
        toast.error(result.error);
      }
    } catch (error) {
      toast.error('Subtitle generation failed');
      console.error('Subtitle error:', error);
    } finally {
      setProcessing(false);
    }
  };

  const generateSpeech = async (text, voice) => {
    setProcessing(true);
    
    try {
      const response = await fetch('/api/video/text-to-speech', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          text: text,
          voice: voice
        })
      });
      
      const result = await response.json();
      
      if (result.success) {
        toast.success('Speech generated successfully!');
        return result;
      } else {
        toast.error(result.error);
      }
    } catch (error) {
      toast.error('Speech generation failed');
      console.error('Speech error:', error);
    } finally {
      setProcessing(false);
    }
  };

  const loadVideoAnalytics = async (videoId) => {
    try {
      const response = await fetch(`/api/video/analytics/${videoId}`);
      const result = await response.json();
      
      if (result.success) {
        setAnalytics(prev => ({
          ...prev,
          [videoId]: result.analytics
        }));
      }
    } catch (error) {
      console.error('Analytics error:', error);
    }
  };

  const tabs = [
    { id: 'upload', name: 'Upload Video', icon: '📹' },
    { id: 'edit', name: 'Video Editing', icon: '✂️' },
    { id: 'enhance', name: 'AI Enhancement', icon: '✨' },
    { id: 'speech', name: 'Text-to-Speech', icon: '🗣️' },
    { id: 'subtitles', name: 'Subtitles', icon: '📝' },
    { id: 'analytics', name: 'Analytics', icon: '📊' }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            🎬 Advanced AI Video Studio
          </h1>
          <p className="text-lg text-gray-600">
            Professional video processing with AI-powered capabilities
          </p>
        </motion.div>

        {/* Tab Navigation */}
        <div className="flex flex-wrap justify-center mb-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`mx-2 mb-2 px-6 py-3 rounded-lg font-medium transition-all duration-200 ${
                activeTab === tab.id
                  ? 'bg-indigo-600 text-white shadow-lg transform scale-105'
                  : 'bg-white text-gray-700 hover:bg-indigo-50 shadow-md'
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.name}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
            className="bg-white rounded-xl shadow-lg p-6"
          >
            {/* Upload Tab */}
            {activeTab === 'upload' && (
              <div>
                <h2 className="text-2xl font-bold mb-6 text-gray-800">Upload Video</h2>
                
                <div className="border-2 border-dashed border-indigo-300 rounded-lg p-8 text-center mb-6">
                  <input
                    type="file"
                    accept="video/*"
                    onChange={handleVideoUpload}
                    className="hidden"
                    id="video-upload"
                    disabled={processing}
                  />
                  <label
                    htmlFor="video-upload"
                    className="cursor-pointer flex flex-col items-center"
                  >
                    <div className="text-6xl mb-4">📹</div>
                    <div className="text-xl font-medium text-gray-700 mb-2">
                      {processing ? 'Uploading...' : 'Choose Video File'}
                    </div>
                    <div className="text-gray-500">
                      Supports MP4, AVI, MOV, MKV, WebM (max 500MB)
                    </div>
                  </label>
                </div>

                {/* Video List */}
                {videos.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold mb-4">Uploaded Videos</h3>
                    <div className="grid gap-4">
                      {videos.map((video) => (
                        <div
                          key={video.id}
                          className="flex items-center justify-between p-4 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100"
                          onClick={() => setSelectedVideo(video)}
                        >
                          <div>
                            <div className="font-medium">{video.name}</div>
                            <div className="text-sm text-gray-500">
                              Duration: {video.metadata?.duration?.toFixed(1)}s
                            </div>
                          </div>
                          <div className="text-sm text-gray-400">
                            {new Date(video.uploaded_at).toLocaleDateString()}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Video Editing Tab */}
            {activeTab === 'edit' && (
              <VideoEditingPanel
                videos={videos}
                selectedVideo={selectedVideo}
                onTrim={trimVideo}
                processing={processing}
              />
            )}

            {/* AI Enhancement Tab */}
            {activeTab === 'enhance' && (
              <VideoEnhancementPanel
                videos={videos}
                selectedVideo={selectedVideo}
                presets={enhancementPresets}
                onEnhance={enhanceVideo}
                processing={processing}
              />
            )}

            {/* Text-to-Speech Tab */}
            {activeTab === 'speech' && (
              <TextToSpeechPanel
                voices={voices}
                onGenerate={generateSpeech}
                processing={processing}
              />
            )}

            {/* Subtitles Tab */}
            {activeTab === 'subtitles' && (
              <SubtitlesPanel
                videos={videos}
                selectedVideo={selectedVideo}
                onGenerate={generateSubtitles}
                processing={processing}
              />
            )}

            {/* Analytics Tab */}
            {activeTab === 'analytics' && (
              <AnalyticsPanel
                videos={videos}
                analytics={analytics}
                onLoadAnalytics={loadVideoAnalytics}
              />
            )}
          </motion.div>
        </AnimatePresence>

        {/* Processing Overlay */}
        {processing && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
          >
            <div className="bg-white rounded-lg p-8 text-center">
              <div className="animate-spin text-4xl mb-4">⚙️</div>
              <div className="text-lg font-medium">Processing...</div>
              <div className="text-gray-500">Please wait while we process your request</div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
};

// Video Editing Panel Component
const VideoEditingPanel = ({ videos, selectedVideo, onTrim, processing }) => {
  const [startTime, setStartTime] = useState('0');
  const [endTime, setEndTime] = useState('10');

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Video Editing</h2>
      
      {/* Video Selection */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Select Video to Edit
        </label>
        <select 
          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
          disabled={processing}
        >
          <option value="">Choose a video...</option>
          {videos.map((video) => (
            <option key={video.id} value={video.id}>
              {video.name}
            </option>
          ))}
        </select>
      </div>

      {/* Trim Controls */}
      <div className="bg-gray-50 rounded-lg p-6 mb-6">
        <h3 className="text-lg font-semibold mb-4">Trim Video</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Start Time (seconds)
            </label>
            <input
              type="number"
              value={startTime}
              onChange={(e) => setStartTime(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg"
              min="0"
              step="0.1"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              End Time (seconds)
            </label>
            <input
              type="number"
              value={endTime}
              onChange={(e) => setEndTime(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg"
              min="0"
              step="0.1"
            />
          </div>
        </div>
        <button
          onClick={() => selectedVideo && onTrim(selectedVideo.id, startTime, endTime)}
          disabled={!selectedVideo || processing}
          className="w-full bg-indigo-600 text-white py-3 rounded-lg hover:bg-indigo-700 disabled:opacity-50"
        >
          ✂️ Trim Video
        </button>
      </div>
    </div>
  );
};

// Video Enhancement Panel Component
const VideoEnhancementPanel = ({ videos, selectedVideo, presets, onEnhance, processing }) => {
  const [selectedPreset, setSelectedPreset] = useState('spiritual_ambient');

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6 text-gray-800">AI Video Enhancement</h2>
      
      {/* Enhancement Presets */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {Object.entries(presets).map(([key, preset]) => (
          <div
            key={key}
            onClick={() => setSelectedPreset(key)}
            className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
              selectedPreset === key
                ? 'border-indigo-500 bg-indigo-50'
                : 'border-gray-200 hover:border-indigo-300'
            }`}
          >
            <div className="font-medium text-gray-800">{preset.name}</div>
            <div className="text-sm text-gray-600 mt-2">{preset.description}</div>
          </div>
        ))}
      </div>

      <button
        onClick={() => selectedVideo && onEnhance(selectedVideo.id, selectedPreset)}
        disabled={!selectedVideo || processing}
        className="w-full bg-gradient-to-r from-purple-600 to-indigo-600 text-white py-3 rounded-lg hover:from-purple-700 hover:to-indigo-700 disabled:opacity-50"
      >
        ✨ Enhance Video
      </button>
    </div>
  );
};

// Text-to-Speech Panel Component
const TextToSpeechPanel = ({ voices, onGenerate, processing }) => {
  const [text, setText] = useState('');
  const [selectedVoice, setSelectedVoice] = useState('male_calm');

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Text-to-Speech</h2>
      
      {/* Voice Selection */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Select Voice
        </label>
        <select
          value={selectedVoice}
          onChange={(e) => setSelectedVoice(e.target.value)}
          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
        >
          {Object.entries(voices).map(([key, voice]) => (
            <option key={key} value={key}>
              {voice.name} - {voice.description}
            </option>
          ))}
        </select>
      </div>

      {/* Text Input */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Text to Convert (max 5000 characters)
        </label>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Enter the text you want to convert to speech..."
          className="w-full h-40 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
          maxLength={5000}
        />
        <div className="text-sm text-gray-500 mt-1">
          {text.length}/5000 characters
        </div>
      </div>

      <button
        onClick={() => text.trim() && onGenerate(text, selectedVoice)}
        disabled={!text.trim() || processing}
        className="w-full bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 disabled:opacity-50"
      >
        🗣️ Generate Speech
      </button>
    </div>
  );
};

// Subtitles Panel Component
const SubtitlesPanel = ({ videos, selectedVideo, onGenerate, processing }) => {
  const [language, setLanguage] = useState('en');

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Subtitle Generation</h2>
      
      {/* Language Selection */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Subtitle Language
        </label>
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
        >
          <option value="en">English</option>
          <option value="es">Spanish</option>
          <option value="fr">French</option>
          <option value="de">German</option>
          <option value="hi">Hindi</option>
          <option value="sa">Sanskrit</option>
        </select>
      </div>

      <button
        onClick={() => selectedVideo && onGenerate(selectedVideo.id, language)}
        disabled={!selectedVideo || processing}
        className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50"
      >
        📝 Generate Subtitles
      </button>
    </div>
  );
};

// Analytics Panel Component
const AnalyticsPanel = ({ videos, analytics, onLoadAnalytics }) => {
  return (
    <div>
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Video Analytics</h2>
      
      {videos.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          Upload some videos to see analytics
        </div>
      ) : (
        <div className="grid gap-4">
          {videos.map((video) => (
            <div key={video.id} className="border rounded-lg p-4">
              <div className="flex justify-between items-center mb-4">
                <h3 className="font-medium">{video.name}</h3>
                <button
                  onClick={() => onLoadAnalytics(video.id)}
                  className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
                >
                  Load Analytics
                </button>
              </div>
              
              {analytics[video.id] && (
                <div className="bg-gray-50 rounded p-4">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <div className="font-medium">Duration</div>
                      <div>{analytics[video.id].duration?.toFixed(1)}s</div>
                    </div>
                    <div>
                      <div className="font-medium">File Size</div>
                      <div>{(analytics[video.id].file_size / (1024*1024)).toFixed(1)}MB</div>
                    </div>
                    <div>
                      <div className="font-medium">Operations</div>
                      <div>{analytics[video.id].processing_operations?.length || 0}</div>
                    </div>
                    <div>
                      <div className="font-medium">Engagement</div>
                      <div>{analytics[video.id].engagement_score || 0}</div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default VideoProcessor;