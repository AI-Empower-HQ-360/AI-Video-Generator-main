import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { AvatarSystem } from '../AvatarSystem';

describe('AvatarSystem Component', () => {
  const defaultProps = {
    guruType: 'spiritual',
    size: 'medium',
    onAvatarClick: jest.fn(),
    isActive: false
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders loading state initially', () => {
    render(<AvatarSystem {...defaultProps} />);
    
    expect(screen.getByTestId('avatar-loading')).toBeInTheDocument();
    expect(screen.getByTestId('avatar-loading')).toHaveClass('animate-pulse');
  });

  it('renders avatar after loading', async () => {
    render(<AvatarSystem {...defaultProps} />);
    
    await waitFor(() => {
      expect(screen.getByTestId('avatar-spiritual')).toBeInTheDocument();
    }, { timeout: 1000 });

    const avatar = screen.getByTestId('avatar-spiritual');
    const img = avatar.querySelector('img');
    
    expect(img).toHaveAttribute('src', '/avatars/spiritual.png');
    expect(img).toHaveAttribute('alt', 'spiritual guru avatar');
    expect(screen.getByText(/spiritual/i)).toBeInTheDocument();
    expect(screen.getByText(/guru/i)).toBeInTheDocument();
  });

  it('applies correct size classes', async () => {
    const { rerender } = render(<AvatarSystem {...defaultProps} size="small" />);
    
    await waitFor(() => {
      expect(screen.getByTestId('avatar-spiritual')).toHaveClass('w-12', 'h-12');
    });

    rerender(<AvatarSystem {...defaultProps} size="large" />);
    await waitFor(() => {
      expect(screen.getByTestId('avatar-spiritual')).toHaveClass('w-32', 'h-32');
    });

    rerender(<AvatarSystem {...defaultProps} size="medium" />);
    await waitFor(() => {
      expect(screen.getByTestId('avatar-spiritual')).toHaveClass('w-20', 'h-20');
    });
  });

  it('shows active state styling', async () => {
    render(<AvatarSystem {...defaultProps} isActive={true} />);
    
    await waitFor(() => {
      expect(screen.getByTestId('avatar-spiritual')).toHaveClass('ring-4', 'ring-blue-500');
    });
  });

  it('handles click events', async () => {
    const onAvatarClick = jest.fn();
    render(<AvatarSystem {...defaultProps} onAvatarClick={onAvatarClick} />);
    
    await waitFor(() => {
      expect(screen.getByTestId('avatar-spiritual')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByTestId('avatar-spiritual'));
    expect(onAvatarClick).toHaveBeenCalledWith('spiritual');
  });

  it('does not call onClick when loading', () => {
    const onAvatarClick = jest.fn();
    render(<AvatarSystem {...defaultProps} onAvatarClick={onAvatarClick} />);
    
    const loadingElement = screen.getByTestId('avatar-loading');
    fireEvent.click(loadingElement);
    
    expect(onAvatarClick).not.toHaveBeenCalled();
  });

  it('handles different guru types', async () => {
    const { rerender } = render(<AvatarSystem {...defaultProps} guruType="meditation" />);
    
    await waitFor(() => {
      expect(screen.getByTestId('avatar-meditation')).toBeInTheDocument();
    });

    const img = screen.getByTestId('avatar-meditation').querySelector('img');
    expect(img).toHaveAttribute('src', '/avatars/meditation.png');
    expect(screen.getByText(/meditation/i)).toBeInTheDocument();

    rerender(<AvatarSystem {...defaultProps} guruType="yoga" />);
    
    await waitFor(() => {
      expect(screen.getByTestId('avatar-yoga')).toBeInTheDocument();
    });
    
    expect(screen.getByText(/yoga/i)).toBeInTheDocument();
  });

  it('handles image load error by using default avatar', async () => {
    render(<AvatarSystem {...defaultProps} />);
    
    await waitFor(() => {
      expect(screen.getByTestId('avatar-spiritual')).toBeInTheDocument();
    });

    const img = screen.getByTestId('avatar-spiritual').querySelector('img');
    
    // Simulate image load error
    fireEvent.error(img);
    
    expect(img).toHaveAttribute('src', '/avatars/default.png');
  });

  it('renders with hover effects', async () => {
    render(<AvatarSystem {...defaultProps} />);
    
    await waitFor(() => {
      expect(screen.getByTestId('avatar-spiritual')).toBeInTheDocument();
    });

    const avatar = screen.getByTestId('avatar-spiritual');
    expect(avatar).toHaveClass('hover:scale-105', 'transition-transform');
  });
});