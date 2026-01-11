import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { MultilingualEngine } from '../MultilingualEngine';

describe('MultilingualEngine Component', () => {
  const defaultProps = {
    currentLanguage: 'en',
    onLanguageChange: jest.fn(),
    availableLanguages: ['en', 'hi', 'sa'],
    translations: {
      en: { welcome: 'Welcome' },
      hi: { welcome: 'स्वागत है' },
      sa: { welcome: 'स्वागतम्' }
    }
  };

  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  it('renders with default language selected', () => {
    render(<MultilingualEngine {...defaultProps} />);
    
    expect(screen.getByTestId('multilingual-engine')).toBeInTheDocument();
    expect(screen.getByTestId('language-selector')).toBeInTheDocument();
    expect(screen.getByTestId('language-selector')).toHaveTextContent('English');
  });

  it('opens dropdown when selector is clicked', () => {
    render(<MultilingualEngine {...defaultProps} />);
    
    fireEvent.click(screen.getByTestId('language-selector'));
    
    expect(screen.getByTestId('language-dropdown')).toBeInTheDocument();
    expect(screen.getByTestId('language-option-en')).toBeInTheDocument();
    expect(screen.getByTestId('language-option-hi')).toBeInTheDocument();
    expect(screen.getByTestId('language-option-sa')).toBeInTheDocument();
  });

  it('displays correct language names', () => {
    render(<MultilingualEngine {...defaultProps} />);
    
    fireEvent.click(screen.getByTestId('language-selector'));
    
    expect(screen.getByTestId('language-option-en')).toHaveTextContent('English');
    expect(screen.getByTestId('language-option-hi')).toHaveTextContent('हिन्दी');
    expect(screen.getByTestId('language-option-sa')).toHaveTextContent('संस्कृत');
  });

  it('highlights current language in dropdown', () => {
    render(<MultilingualEngine {...defaultProps} currentLanguage="hi" />);
    
    fireEvent.click(screen.getByTestId('language-selector'));
    
    const hiOption = screen.getByTestId('language-option-hi');
    expect(hiOption).toHaveClass('bg-blue-50', 'text-blue-700');
  });

  it('handles language selection with loading state', async () => {
    const onLanguageChange = jest.fn();
    render(<MultilingualEngine {...defaultProps} onLanguageChange={onLanguageChange} />);
    
    fireEvent.click(screen.getByTestId('language-selector'));
    
    await act(async () => {
      fireEvent.click(screen.getByTestId('language-option-hi'));
      jest.advanceTimersByTime(1000);
    });
    
    await waitFor(() => {
      expect(onLanguageChange).toHaveBeenCalledWith('hi');
    });
  });

  it('does not change language when selecting current language', async () => {
    const onLanguageChange = jest.fn();
    render(<MultilingualEngine {...defaultProps} onLanguageChange={onLanguageChange} />);
    
    fireEvent.click(screen.getByTestId('language-selector'));
    fireEvent.click(screen.getByTestId('language-option-en'));
    
    expect(onLanguageChange).not.toHaveBeenCalled();
  });

  it('closes dropdown after language selection', async () => {
    render(<MultilingualEngine {...defaultProps} />);
    
    fireEvent.click(screen.getByTestId('language-selector'));
    expect(screen.getByTestId('language-dropdown')).toBeInTheDocument();
    
    fireEvent.click(screen.getByTestId('language-option-hi'));
    
    // Dropdown should close immediately
    expect(screen.queryByTestId('language-dropdown')).not.toBeInTheDocument();
  });

  it('closes dropdown when clicking selector again', () => {
    render(<MultilingualEngine {...defaultProps} />);
    
    // Open dropdown
    fireEvent.click(screen.getByTestId('language-selector'));
    expect(screen.getByTestId('language-dropdown')).toBeInTheDocument();
    
    // Close dropdown
    fireEvent.click(screen.getByTestId('language-selector'));
    expect(screen.queryByTestId('language-dropdown')).not.toBeInTheDocument();
  });

  it('disables selector during language loading', async () => {
    render(<MultilingualEngine {...defaultProps} />);
    
    fireEvent.click(screen.getByTestId('language-selector'));
    fireEvent.click(screen.getByTestId('language-option-hi'));
    
    const selector = screen.getByTestId('language-selector');
    expect(selector).toBeDisabled();
    
    await act(async () => {
      jest.advanceTimersByTime(1000);
    });
    
    await waitFor(() => {
      expect(selector).not.toBeDisabled();
    });
  });

  it('renders with custom available languages', () => {
    const customProps = {
      ...defaultProps,
      availableLanguages: ['en', 'hi'],
      currentLanguage: 'en'
    };
    
    render(<MultilingualEngine {...customProps} />);
    
    fireEvent.click(screen.getByTestId('language-selector'));
    
    expect(screen.getByTestId('language-option-en')).toBeInTheDocument();
    expect(screen.getByTestId('language-option-hi')).toBeInTheDocument();
    expect(screen.queryByTestId('language-option-sa')).not.toBeInTheDocument();
  });

  it('displays fallback for unknown language', () => {
    render(<MultilingualEngine {...defaultProps} currentLanguage="unknown" />);
    
    // Should still render the selector, but with the unknown language code
    expect(screen.getByTestId('language-selector')).toBeInTheDocument();
  });

  it('handles missing onLanguageChange prop gracefully', async () => {
    const { onLanguageChange, ...propsWithoutCallback } = defaultProps;
    
    render(<MultilingualEngine {...propsWithoutCallback} />);
    
    fireEvent.click(screen.getByTestId('language-selector'));
    fireEvent.click(screen.getByTestId('language-option-hi'));
    
    // Should not throw error even without callback
    await act(async () => {
      jest.advanceTimersByTime(1000);
    });
    
    await waitFor(() => {
      expect(screen.getByTestId('language-selector')).not.toBeDisabled();
    });
  });
});