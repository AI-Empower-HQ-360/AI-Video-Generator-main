import React, { useState, useEffect } from 'react';

/**
 * AvatarSystem Component - Renders spiritual guide avatars
 * @param {Object} props
 * @param {string} props.guruType - Type of guru (spiritual, sloka, meditation, etc.)
 * @param {string} props.size - Size of avatar (small, medium, large)
 * @param {Function} props.onAvatarClick - Callback when avatar is clicked
 * @param {boolean} props.isActive - Whether the avatar is currently active
 */
export function AvatarSystem({ guruType = 'spiritual', size = 'medium', onAvatarClick, isActive = false }) {
  const [isLoading, setIsLoading] = useState(true);
  const [avatarUrl, setAvatarUrl] = useState('');

  useEffect(() => {
    // Simulate avatar loading
    const timer = setTimeout(() => {
      setAvatarUrl(`/avatars/${guruType}.png`);
      setIsLoading(false);
    }, 500);

    return () => clearTimeout(timer);
  }, [guruType]);

  const handleClick = () => {
    if (onAvatarClick && !isLoading) {
      onAvatarClick(guruType);
    }
  };

  const getSizeClass = () => {
    switch (size) {
      case 'small': return 'w-12 h-12';
      case 'large': return 'w-32 h-32';
      default: return 'w-20 h-20';
    }
  };

  if (isLoading) {
    return (
      <div 
        className={`${getSizeClass()} rounded-full bg-gray-200 animate-pulse`}
        data-testid="avatar-loading"
      />
    );
  }

  return (
    <div 
      className={`${getSizeClass()} cursor-pointer transition-transform hover:scale-105 ${
        isActive ? 'ring-4 ring-blue-500' : ''
      }`}
      onClick={handleClick}
      data-testid={`avatar-${guruType}`}
    >
      <img
        src={avatarUrl}
        alt={`${guruType} guru avatar`}
        className="w-full h-full rounded-full object-cover"
        onError={() => setAvatarUrl('/avatars/default.png')}
      />
      <div className="text-center mt-2 text-sm font-medium capitalize">
        {guruType} Guru
      </div>
    </div>
  );
}

// Helper function for backward compatibility
export function renderAvatar(name) { 
  return `${name} avatar displayed`; 
}
