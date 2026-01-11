import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { HomeIcon, VideoCameraIcon, PhotoIcon, ShareIcon } from '@heroicons/react/24/outline';
import SpiritualGuidance from './components/SpiritualGuidance';
import VideoEditor from './components/VideoEditor';
import VideoGallery from './components/VideoGallery';
import SocialShare from './components/SocialShare';

function App() {
  const [currentPage, setCurrentPage] = useState('home');

  const navigation = [
    { id: 'home', name: 'Spiritual Guidance', icon: HomeIcon, component: SpiritualGuidance },
    { id: 'editor', name: 'Video Editor', icon: VideoCameraIcon, component: VideoEditor },
    { id: 'gallery', name: 'Video Gallery', icon: PhotoIcon, component: VideoGallery },
    { id: 'share', name: 'Social Share', icon: ShareIcon, component: SocialShare },
  ];

  const CurrentComponent = navigation.find(nav => nav.id === currentPage)?.component || SpiritualGuidance;

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-500 to-secondary-500">
      <nav className="bg-white/10 backdrop-blur-md border-b border-white/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-2xl font-bold text-white">🕉️ AI Empower Heart 360</h1>
              </div>
            </div>
            <div className="hidden md:block">
              <div className="ml-10 flex items-baseline space-x-4">
                {navigation.map((item) => {
                  const Icon = item.icon;
                  return (
                    <button
                      key={item.id}
                      onClick={() => setCurrentPage(item.id)}
                      className={`${
                        currentPage === item.id
                          ? 'bg-white/20 text-white'
                          : 'text-white/70 hover:bg-white/10 hover:text-white'
                      } px-3 py-2 rounded-md text-sm font-medium flex items-center space-x-2 transition-all duration-200`}
                    >
                      <Icon className="h-5 w-5" />
                      <span>{item.name}</span>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <CurrentComponent />
        </div>
      </main>

      {/* Mobile navigation */}
      <div className="md:hidden fixed bottom-0 left-0 right-0 bg-white/10 backdrop-blur-md border-t border-white/20">
        <div className="grid grid-cols-4 h-16">
          {navigation.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => setCurrentPage(item.id)}
                className={`${
                  currentPage === item.id
                    ? 'text-white bg-white/20'
                    : 'text-white/70'
                } flex flex-col items-center justify-center space-y-1 transition-all duration-200`}
              >
                <Icon className="h-5 w-5" />
                <span className="text-xs">{item.name.split(' ')[0]}</span>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default App;