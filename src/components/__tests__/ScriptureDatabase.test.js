import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { ScriptureDatabase } from '../ScriptureDatabase';

describe('ScriptureDatabase Component', () => {
  const defaultProps = {
    searchQuery: '',
    selectedSource: 'all',
    onVerseSelect: jest.fn(),
    limit: 10
  };

  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  it('renders scripture database with heading', () => {
    render(<ScriptureDatabase {...defaultProps} />);
    
    expect(screen.getByTestId('scripture-database')).toBeInTheDocument();
    expect(screen.getByText('Scripture Database')).toBeInTheDocument();
    expect(screen.getByTestId('source-selector')).toBeInTheDocument();
  });

  it('shows loading state initially', () => {
    render(<ScriptureDatabase {...defaultProps} />);
    
    expect(screen.getByTestId('scripture-loading')).toBeInTheDocument();
    expect(document.querySelectorAll('.animate-pulse')).toHaveLength(3);
  });

  it('displays verses after loading', async () => {
    render(<ScriptureDatabase {...defaultProps} />);
    
    await act(async () => {
      jest.advanceTimersByTime(800);
    });
    
    await waitFor(() => {
      expect(screen.getByTestId('verses-list')).toBeInTheDocument();
    });

    expect(screen.getByTestId('verse-1')).toBeInTheDocument();
    expect(screen.getByTestId('verse-2')).toBeInTheDocument();
    
    expect(screen.getByText('You have the right to perform actions, but never to the fruits of action.')).toBeInTheDocument();
    expect(screen.getByText('कर्मण्येवाधिकारस्ते मा फलेषु कदाचन')).toBeInTheDocument();
  });

  it('displays scripture source information', async () => {
    render(<ScriptureDatabase {...defaultProps} />);
    
    await act(async () => {
      jest.advanceTimersByTime(800);
    });
    
    await waitFor(() => {
      expect(screen.getByText('bhagavad-gita - Chapter 2, Verse 47')).toBeInTheDocument();
      expect(screen.getByText('bhagavad-gita - Chapter 2, Verse 20')).toBeInTheDocument();
    });
  });

  it('handles verse selection', async () => {
    const onVerseSelect = jest.fn();
    render(<ScriptureDatabase {...defaultProps} onVerseSelect={onVerseSelect} />);
    
    await act(async () => {
      jest.advanceTimersByTime(800);
    });
    
    await waitFor(() => {
      expect(screen.getByTestId('verse-1')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByTestId('verse-1'));
    
    expect(onVerseSelect).toHaveBeenCalledWith({
      id: '1',
      text: 'You have the right to perform actions, but never to the fruits of action.',
      translation: 'कर्मण्येवाधिकारस्ते मा फलेषु कदाचन',
      source: 'bhagavad-gita',
      chapter: 2,
      verse: 47
    });
  });

  it('renders source selector with all options', () => {
    render(<ScriptureDatabase {...defaultProps} />);
    
    const selector = screen.getByTestId('source-selector');
    expect(selector).toBeInTheDocument();
    
    const options = selector.querySelectorAll('option');
    expect(options).toHaveLength(5);
    expect(options[0]).toHaveTextContent('All Sources');
    expect(options[1]).toHaveTextContent('Bhagavad Gita');
    expect(options[2]).toHaveTextContent('Upanishads');
    expect(options[3]).toHaveTextContent('Vedas');
    expect(options[4]).toHaveTextContent('Puranas');
  });

  it('handles source selection', () => {
    const onVerseSelect = jest.fn();
    render(<ScriptureDatabase {...defaultProps} onVerseSelect={onVerseSelect} />);
    
    const selector = screen.getByTestId('source-selector');
    fireEvent.change(selector, { target: { value: 'bhagavad-gita' } });
    
    expect(onVerseSelect).toHaveBeenCalledWith({ source: 'bhagavad-gita' });
  });

  it('applies hover effects to verses', async () => {
    render(<ScriptureDatabase {...defaultProps} />);
    
    await act(async () => {
      jest.advanceTimersByTime(800);
    });
    
    await waitFor(() => {
      expect(screen.getByTestId('verse-1')).toBeInTheDocument();
    });

    const verse = screen.getByTestId('verse-1');
    expect(verse).toHaveClass('hover:bg-gray-50', 'transition-colors', 'cursor-pointer');
  });

  it('shows "No verses found" when no results', async () => {
    // Mock a scenario where no verses are found
    render(<ScriptureDatabase {...defaultProps} searchQuery="nonexistent" />);
    
    await act(async () => {
      jest.advanceTimersByTime(800);
    });
    
    await waitFor(() => {
      expect(screen.getByTestId('no-verses')).toBeInTheDocument();
      expect(screen.getByText('No verses found')).toBeInTheDocument();
    });
  });

  it('reloads data when search query changes', async () => {
    const { rerender } = render(<ScriptureDatabase {...defaultProps} />);
    
    await act(async () => {
      jest.advanceTimersByTime(800);
    });
    
    await waitFor(() => {
      expect(screen.getByTestId('verses-list')).toBeInTheDocument();
    });

    // Change search query
    rerender(<ScriptureDatabase {...defaultProps} searchQuery="karma" />);
    
    // Should show loading again
    expect(screen.getByTestId('scripture-loading')).toBeInTheDocument();
    
    await act(async () => {
      jest.advanceTimersByTime(800);
    });
    
    await waitFor(() => {
      expect(screen.getByTestId('verses-list')).toBeInTheDocument();
    });
  });

  it('reloads data when selected source changes', async () => {
    const { rerender } = render(<ScriptureDatabase {...defaultProps} />);
    
    await act(async () => {
      jest.advanceTimersByTime(800);
    });
    
    await waitFor(() => {
      expect(screen.getByTestId('verses-list')).toBeInTheDocument();
    });

    // Change selected source
    rerender(<ScriptureDatabase {...defaultProps} selectedSource="upanishads" />);
    
    // Should show loading again
    expect(screen.getByTestId('scripture-loading')).toBeInTheDocument();
    
    await act(async () => {
      jest.advanceTimersByTime(800);
    });
    
    await waitFor(() => {
      expect(screen.getByTestId('verses-list')).toBeInTheDocument();
    });
  });

  it('handles API errors gracefully', async () => {
    // Mock console.error to avoid noise in tests
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    
    // Mock fetch to reject
    global.fetch = jest.fn().mockRejectedValue(new Error('API Error'));
    
    render(<ScriptureDatabase {...defaultProps} />);
    
    await act(async () => {
      jest.advanceTimersByTime(800);
    });
    
    await waitFor(() => {
      expect(screen.getByTestId('scripture-error')).toBeInTheDocument();
      expect(screen.getByText('Failed to fetch verses')).toBeInTheDocument();
    });

    // Test retry functionality
    const retryButton = screen.getByText('Retry');
    expect(retryButton).toBeInTheDocument();
    
    // Clean up
    consoleSpy.mockRestore();
    global.fetch.mockClear();
  });

  it('respects limit prop', async () => {
    render(<ScriptureDatabase {...defaultProps} limit={1} />);
    
    await act(async () => {
      jest.advanceTimersByTime(800);
    });
    
    await waitFor(() => {
      expect(screen.getByTestId('verses-list')).toBeInTheDocument();
    });

    // Should only show 1 verse due to limit
    expect(screen.getByTestId('verse-1')).toBeInTheDocument();
    expect(screen.queryByTestId('verse-2')).not.toBeInTheDocument();
  });

  it('handles missing onVerseSelect prop gracefully', async () => {
    const { onVerseSelect, ...propsWithoutCallback } = defaultProps;
    
    render(<ScriptureDatabase {...propsWithoutCallback} />);
    
    await act(async () => {
      jest.advanceTimersByTime(800);
    });
    
    await waitFor(() => {
      expect(screen.getByTestId('verse-1')).toBeInTheDocument();
    });

    // Should not throw error when clicking verse without callback
    fireEvent.click(screen.getByTestId('verse-1'));
    
    expect(screen.getByTestId('verse-1')).toBeInTheDocument();
  });
});