import React, { useState } from 'react';
import { 
  ShareIcon, 
  LinkIcon, 
  CheckIcon,
  DocumentDuplicateIcon,
  GlobeAltIcon,
  UserGroupIcon,
  LockClosedIcon
} from '@heroicons/react/24/outline';

const SocialShare = () => {
  const [selectedVideo, setSelectedVideo] = useState(null);
  const [shareSettings, setShareSettings] = useState({
    privacy: 'public',
    allowComments: true,
    allowDownload: false,
    description: '',
    tags: []
  });
  const [copiedLink, setCopiedLink] = useState(false);
  const [publishingStatus, setPublishingStatus] = useState({});

  // Mock video data
  const myVideos = [
    {
      id: 'video-1',
      title: 'Morning Meditation Guide',
      thumbnail: '🧘‍♀️',
      duration: '10:23',
      status: 'draft',
      shareUrl: 'https://aiempower360.com/video/morning-meditation-guide'
    },
    {
      id: 'video-2',
      title: 'Sanskrit Sloka Recitation',
      thumbnail: '🕉️',
      duration: '8:45',
      status: 'published',
      shareUrl: 'https://aiempower360.com/video/sanskrit-sloka-recitation'
    },
    {
      id: 'video-3',
      title: 'Heart Chakra Healing',
      thumbnail: '💚',
      duration: '15:30',
      status: 'published',
      shareUrl: 'https://aiempower360.com/video/heart-chakra-healing'
    }
  ];

  const socialPlatforms = [
    {
      id: 'youtube',
      name: 'YouTube',
      icon: '📺',
      color: 'bg-red-600',
      connected: true,
      maxDuration: 900, // 15 minutes for unverified accounts
      description: 'Share with the global spiritual community'
    },
    {
      id: 'facebook',
      name: 'Facebook',
      icon: '📘',
      color: 'bg-blue-600',
      connected: true,
      maxDuration: 240, // 4 minutes
      description: 'Connect with friends and family'
    },
    {
      id: 'instagram',
      name: 'Instagram',
      icon: '📷',
      color: 'bg-gradient-to-r from-purple-500 to-pink-500',
      connected: false,
      maxDuration: 60, // 1 minute for reels
      description: 'Share short spiritual moments'
    },
    {
      id: 'twitter',
      name: 'Twitter/X',
      icon: '🐦',
      color: 'bg-black',
      connected: true,
      maxDuration: 140, // 2:20 minutes
      description: 'Spread wisdom in short form'
    },
    {
      id: 'linkedin',
      name: 'LinkedIn',
      icon: '💼',
      color: 'bg-blue-700',
      connected: false,
      maxDuration: 600, // 10 minutes
      description: 'Professional spiritual content'
    },
    {
      id: 'tiktok',
      name: 'TikTok',
      icon: '🎵',
      color: 'bg-black',
      connected: false,
      maxDuration: 180, // 3 minutes
      description: 'Viral spiritual content'
    }
  ];

  const privacyOptions = [
    { id: 'public', name: 'Public', icon: GlobeAltIcon, description: 'Anyone can see this video' },
    { id: 'unlisted', name: 'Unlisted', icon: LinkIcon, description: 'Only people with the link can see this' },
    { id: 'private', name: 'Private', icon: LockClosedIcon, description: 'Only you can see this video' },
    { id: 'community', name: 'Community Only', icon: UserGroupIcon, description: 'Only community members can see this' }
  ];

  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedLink(true);
      setTimeout(() => setCopiedLink(false), 2000);
    } catch (err) {
      console.error('Failed to copy: ', err);
    }
  };

  const publishToPlatform = async (platformId) => {
    setPublishingStatus(prev => ({ ...prev, [platformId]: 'publishing' }));
    
    // Simulate API call
    setTimeout(() => {
      setPublishingStatus(prev => ({ ...prev, [platformId]: 'success' }));
      setTimeout(() => {
        setPublishingStatus(prev => ({ ...prev, [platformId]: null }));
      }, 3000);
    }, 2000);
  };

  const connectPlatform = (platformId) => {
    // Simulate OAuth connection
    alert(`Connecting to ${socialPlatforms.find(p => p.id === platformId)?.name}...`);
  };

  const getVideoDurationInSeconds = (duration) => {
    const parts = duration.split(':');
    return parseInt(parts[0]) * 60 + parseInt(parts[1]);
  };

  const canPublishToPlatform = (video, platform) => {
    if (!platform.connected) return false;
    const videoDuration = getVideoDurationInSeconds(video.duration);
    return videoDuration <= platform.maxDuration;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-white mb-4">
          🌐 Share & Collaborate
        </h1>
        <p className="text-xl text-white/80">
          Share your spiritual content with the world
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Video Selection */}
        <div className="lg:col-span-1">
          <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6">
            <h2 className="text-xl font-semibold text-white mb-4">Select Video</h2>
            
            <div className="space-y-3">
              {myVideos.map(video => (
                <div
                  key={video.id}
                  onClick={() => setSelectedVideo(video)}
                  className={`p-4 rounded-xl cursor-pointer transition-all ${
                    selectedVideo?.id === video.id
                      ? 'bg-blue-600/30 border-2 border-blue-400'
                      : 'bg-white/10 border-2 border-transparent hover:bg-white/20'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <div className="text-3xl">{video.thumbnail}</div>
                    <div className="flex-1">
                      <h3 className="text-white font-medium">{video.title}</h3>
                      <div className="flex items-center space-x-2 text-sm text-white/60">
                        <span>{video.duration}</span>
                        <span>•</span>
                        <span className={`capitalize ${
                          video.status === 'published' ? 'text-green-400' : 'text-yellow-400'
                        }`}>
                          {video.status}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {selectedVideo ? (
            <>
              {/* Share Settings */}
              <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6">
                <h2 className="text-xl font-semibold text-white mb-4">Share Settings</h2>
                
                {/* Privacy Settings */}
                <div className="mb-6">
                  <h3 className="text-lg font-medium text-white mb-3">Privacy</h3>
                  <div className="grid grid-cols-2 gap-3">
                    {privacyOptions.map(option => {
                      const Icon = option.icon;
                      return (
                        <button
                          key={option.id}
                          onClick={() => setShareSettings(prev => ({ ...prev, privacy: option.id }))}
                          className={`p-3 rounded-lg border-2 transition-all text-left ${
                            shareSettings.privacy === option.id
                              ? 'border-blue-400 bg-blue-600/20'
                              : 'border-white/20 bg-white/10 hover:bg-white/20'
                          }`}
                        >
                          <div className="flex items-center space-x-2 mb-1">
                            <Icon className="h-5 w-5 text-white" />
                            <span className="text-white font-medium">{option.name}</span>
                          </div>
                          <p className="text-white/70 text-sm">{option.description}</p>
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Additional Settings */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-white">Allow Comments</span>
                    <button
                      onClick={() => setShareSettings(prev => ({ ...prev, allowComments: !prev.allowComments }))}
                      className={`w-12 h-6 rounded-full transition-colors ${
                        shareSettings.allowComments ? 'bg-blue-600' : 'bg-gray-600'
                      }`}
                    >
                      <div className={`w-4 h-4 bg-white rounded-full transition-transform ${
                        shareSettings.allowComments ? 'translate-x-7' : 'translate-x-1'
                      }`} />
                    </button>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-white">Allow Download</span>
                    <button
                      onClick={() => setShareSettings(prev => ({ ...prev, allowDownload: !prev.allowDownload }))}
                      className={`w-12 h-6 rounded-full transition-colors ${
                        shareSettings.allowDownload ? 'bg-blue-600' : 'bg-gray-600'
                      }`}
                    >
                      <div className={`w-4 h-4 bg-white rounded-full transition-transform ${
                        shareSettings.allowDownload ? 'translate-x-7' : 'translate-x-1'
                      }`} />
                    </button>
                  </div>
                </div>

                {/* Share Link */}
                <div className="mt-6">
                  <h3 className="text-lg font-medium text-white mb-3">Share Link</h3>
                  <div className="flex items-center space-x-2">
                    <input
                      type="text"
                      value={selectedVideo.shareUrl}
                      readOnly
                      className="flex-1 px-3 py-2 bg-white/20 border border-white/30 rounded-lg text-white"
                    />
                    <button
                      onClick={() => copyToClipboard(selectedVideo.shareUrl)}
                      className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
                    >
                      {copiedLink ? (
                        <>
                          <CheckIcon className="h-4 w-4 text-white" />
                          <span className="text-white">Copied!</span>
                        </>
                      ) : (
                        <>
                          <DocumentDuplicateIcon className="h-4 w-4 text-white" />
                          <span className="text-white">Copy</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>

              {/* Social Platforms */}
              <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6">
                <h2 className="text-xl font-semibold text-white mb-4">Publish to Social Media</h2>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {socialPlatforms.map(platform => {
                    const canPublish = canPublishToPlatform(selectedVideo, platform);
                    const status = publishingStatus[platform.id];
                    
                    return (
                      <div
                        key={platform.id}
                        className="p-4 bg-white/10 rounded-xl border border-white/20"
                      >
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center space-x-3">
                            <div className={`w-10 h-10 rounded-lg ${platform.color} flex items-center justify-center text-white`}>
                              <span className="text-lg">{platform.icon}</span>
                            </div>
                            <div>
                              <h3 className="text-white font-medium">{platform.name}</h3>
                              <p className="text-white/60 text-sm">{platform.description}</p>
                            </div>
                          </div>
                          
                          {platform.connected ? (
                            <span className="text-green-400 text-sm">Connected</span>
                          ) : (
                            <span className="text-gray-400 text-sm">Not connected</span>
                          )}
                        </div>

                        {platform.connected ? (
                          canPublish ? (
                            <button
                              onClick={() => publishToPlatform(platform.id)}
                              disabled={status === 'publishing'}
                              className="w-full py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded-lg transition-colors"
                            >
                              {status === 'publishing' ? 'Publishing...' : 
                               status === 'success' ? 'Published!' : 'Publish'}
                            </button>
                          ) : (
                            <div className="text-red-400 text-sm">
                              Video too long for this platform (max {Math.floor(platform.maxDuration / 60)}:{(platform.maxDuration % 60).toString().padStart(2, '0')})
                            </div>
                          )
                        ) : (
                          <button
                            onClick={() => connectPlatform(platform.id)}
                            className="w-full py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
                          >
                            Connect Account
                          </button>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Collaboration */}
              <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6">
                <h2 className="text-xl font-semibold text-white mb-4">Collaboration</h2>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-white font-medium mb-2">Invite Collaborators</label>
                    <div className="flex space-x-2">
                      <input
                        type="email"
                        placeholder="Enter email address..."
                        className="flex-1 px-3 py-2 bg-white/20 border border-white/30 rounded-lg text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-blue-400"
                      />
                      <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors">
                        Invite
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-white font-medium mb-2">Permission Level</label>
                    <select className="w-full px-3 py-2 bg-white/20 border border-white/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-400">
                      <option value="view" className="bg-gray-800">View Only</option>
                      <option value="comment" className="bg-gray-800">Can Comment</option>
                      <option value="edit" className="bg-gray-800">Can Edit</option>
                    </select>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="bg-white/10 backdrop-blur-md rounded-2xl p-12 text-center">
              <ShareIcon className="h-16 w-16 text-white/40 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white/80 mb-2">Select a Video to Share</h3>
              <p className="text-white/60">Choose a video from the left panel to start sharing</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SocialShare;