import React, { useState } from 'react';

const VideoAIDemo = () => {
  const [activeTab, setActiveTab] = useState('script');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:5000';

  const generateScript = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/video-ai/generate-script`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          keywords: ['artificial intelligence', 'machine learning', 'future technology'],
          video_type: 'educational',
          duration: 120
        }),
      });
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('Error generating script:', error);
      setResults({ error: 'Failed to generate script' });
    }
    setLoading(false);
  };

  const analyzeDeepfake = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/video-ai/detect-deepfake`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          video_url: 'https://example.com/test-video.mp4'
        }),
      });
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('Error analyzing deepfake:', error);
      setResults({ error: 'Failed to analyze video' });
    }
    setLoading(false);
  };

  const analyzeEmotions = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/video-ai/analyze-emotion`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          video_url: 'https://example.com/test-video.mp4',
          analyze_audio: true,
          analyze_visual: true
        }),
      });
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('Error analyzing emotions:', error);
      setResults({ error: 'Failed to analyze emotions' });
    }
    setLoading(false);
  };

  const getRecommendations = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/video-ai/recommend-videos`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: 'demo_user_123',
          preferences: { categories: ['educational', 'technology'] },
          count: 5
        }),
      });
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('Error getting recommendations:', error);
      setResults({ error: 'Failed to get recommendations' });
    }
    setLoading(false);
  };

  const createABTest = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/video-ai/ab-test`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          test_name: 'Thumbnail A/B Test Demo',
          video_variants: [
            { video_url: 'https://example.com/variant-a.mp4', description: 'Variant A with text overlay' },
            { video_url: 'https://example.com/variant-b.mp4', description: 'Variant B with face thumbnail' }
          ],
          target_metrics: ['engagement', 'completion_rate'],
          duration_days: 7
        }),
      });
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('Error creating A/B test:', error);
      setResults({ error: 'Failed to create A/B test' });
    }
    setLoading(false);
  };

  const predictPerformance = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/video-ai/predict-performance`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          video_metadata: {
            title: 'Amazing AI Technology Breakthrough',
            description: 'Discover the latest advances in artificial intelligence technology',
            duration: 300,
            tags: ['AI', 'technology', 'innovation', 'machine learning'],
            category: 'educational'
          },
          metrics: ['views', 'engagement', 'completion_rate']
        }),
      });
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('Error predicting performance:', error);
      setResults({ error: 'Failed to predict performance' });
    }
    setLoading(false);
  };

  const getAnalyticsDashboard = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/video-ai/analytics/dashboard`);
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('Error getting analytics:', error);
      setResults({ error: 'Failed to get analytics' });
    }
    setLoading(false);
  };

  const tabs = [
    { id: 'script', label: 'Script Generation', action: generateScript },
    { id: 'deepfake', label: 'Deepfake Detection', action: analyzeDeepfake },
    { id: 'emotion', label: 'Emotion Analysis', action: analyzeEmotions },
    { id: 'recommendations', label: 'Recommendations', action: getRecommendations },
    { id: 'abtest', label: 'A/B Testing', action: createABTest },
    { id: 'prediction', label: 'Performance Prediction', action: predictPerformance },
    { id: 'analytics', label: 'Analytics Dashboard', action: getAnalyticsDashboard }
  ];

  const renderResults = () => {
    if (!results) return null;

    if (results.error) {
      return (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-600">Error: {results.error}</p>
        </div>
      );
    }

    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-3">Results:</h3>
        <pre className="bg-white p-3 rounded border text-sm overflow-auto max-h-96">
          {JSON.stringify(results, null, 2)}
        </pre>
      </div>
    );
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h1 className="text-2xl font-bold text-gray-900">AI Video Enhancement Suite</h1>
          <p className="text-gray-600 mt-2">
            Explore advanced AI capabilities for video generation, analysis, and optimization
          </p>
        </div>

        <div className="px-6 py-4">
          {/* Tab Navigation */}
          <div className="flex flex-wrap gap-2 mb-6">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Demo Actions */}
          <div className="mb-6">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
              <h3 className="text-lg font-semibold text-blue-900 mb-2">
                {tabs.find(t => t.id === activeTab)?.label}
              </h3>
              
              {activeTab === 'script' && (
                <p className="text-blue-700 mb-3">
                  Generate AI-powered video scripts from keywords with optimized structure and timing.
                </p>
              )}
              
              {activeTab === 'deepfake' && (
                <p className="text-blue-700 mb-3">
                  Detect deepfake content and verify video authenticity using advanced ML models.
                </p>
              )}
              
              {activeTab === 'emotion' && (
                <p className="text-blue-700 mb-3">
                  Analyze emotions and sentiment in video content using computer vision and audio analysis.
                </p>
              )}
              
              {activeTab === 'recommendations' && (
                <p className="text-blue-700 mb-3">
                  Get personalized video recommendations using collaborative filtering and deep learning.
                </p>
              )}
              
              {activeTab === 'abtest' && (
                <p className="text-blue-700 mb-3">
                  Create automated A/B tests for video variations with statistical analysis.
                </p>
              )}
              
              {activeTab === 'prediction' && (
                <p className="text-blue-700 mb-3">
                  Predict video performance using predictive analytics and machine learning models.
                </p>
              )}
              
              {activeTab === 'analytics' && (
                <p className="text-blue-700 mb-3">
                  View comprehensive analytics dashboard with insights across all AI features.
                </p>
              )}

              <button
                onClick={tabs.find(t => t.id === activeTab)?.action}
                disabled={loading}
                className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                  loading
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                }`}
              >
                {loading ? 'Processing...' : `Demo ${tabs.find(t => t.id === activeTab)?.label}`}
              </button>
            </div>
          </div>

          {/* Results Display */}
          {renderResults()}
        </div>

        {/* Feature Overview */}
        <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
          <h3 className="text-lg font-semibold mb-4">AI Features Overview</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="bg-white p-4 rounded-lg border">
              <h4 className="font-semibold text-blue-600 mb-2">🎬 Script Generation</h4>
              <p className="text-sm text-gray-600">
                AI-powered script creation from keywords with optimized structure for engagement
              </p>
            </div>
            
            <div className="bg-white p-4 rounded-lg border">
              <h4 className="font-semibold text-red-600 mb-2">🔍 Deepfake Detection</h4>
              <p className="text-sm text-gray-600">
                Advanced detection of manipulated content with confidence scoring
              </p>
            </div>
            
            <div className="bg-white p-4 rounded-lg border">
              <h4 className="font-semibold text-green-600 mb-2">😊 Emotion Analysis</h4>
              <p className="text-sm text-gray-600">
                Real-time emotion recognition and sentiment analysis for video optimization
              </p>
            </div>
            
            <div className="bg-white p-4 rounded-lg border">
              <h4 className="font-semibold text-purple-600 mb-2">🎯 Smart Recommendations</h4>
              <p className="text-sm text-gray-600">
                Personalized video suggestions using collaborative filtering and deep learning
              </p>
            </div>
            
            <div className="bg-white p-4 rounded-lg border">
              <h4 className="font-semibold text-orange-600 mb-2">⚡ A/B Testing</h4>
              <p className="text-sm text-gray-600">
                Automated testing of video variations with statistical significance analysis
              </p>
            </div>
            
            <div className="bg-white p-4 rounded-lg border">
              <h4 className="font-semibold text-indigo-600 mb-2">📊 Predictive Analytics</h4>
              <p className="text-sm text-gray-600">
                Performance prediction and optimization recommendations using ML models
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VideoAIDemo;