import React, { useState, useEffect } from 'react';

/**
 * MultilingualEngine Component - Handles language switching and translations
 * @param {Object} props
 * @param {string} props.currentLanguage - Current selected language
 * @param {Function} props.onLanguageChange - Callback when language changes
 * @param {Array} props.availableLanguages - List of available languages
 * @param {Object} props.translations - Translation object
 */
export function MultilingualEngine({ 
  currentLanguage = 'en', 
  onLanguageChange, 
  availableLanguages = ['en', 'hi', 'sa'], 
  translations = {} 
}) {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [loadingLanguage, setLoadingLanguage] = useState(null);

  const languageNames = {
    'en': 'English',
    'hi': 'हिन्दी',
    'sa': 'संस्कृत'
  };

  const handleLanguageSelect = async (language) => {
    if (language === currentLanguage) return;
    
    setLoadingLanguage(language);
    setIsDropdownOpen(false);
    
    // Simulate loading translations
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    if (onLanguageChange) {
      onLanguageChange(language);
    }
    
    setLoadingLanguage(null);
  };

  const translateText = (key) => {
    return translations[currentLanguage]?.[key] || key;
  };

  return (
    <div className="relative inline-block" data-testid="multilingual-engine">
      <button
        onClick={() => setIsDropdownOpen(!isDropdownOpen)}
        className="flex items-center space-x-2 px-4 py-2 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50"
        data-testid="language-selector"
        disabled={loadingLanguage !== null}
      >
        <span>{languageNames[currentLanguage]}</span>
        {loadingLanguage ? (
          <div className="animate-spin h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full" />
        ) : (
          <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        )}
      </button>

      {isDropdownOpen && (
        <div 
          className="absolute right-0 mt-1 w-48 bg-white border border-gray-300 rounded-md shadow-lg z-10"
          data-testid="language-dropdown"
        >
          {availableLanguages.map((language) => (
            <button
              key={language}
              onClick={() => handleLanguageSelect(language)}
              className={`block w-full text-left px-4 py-2 hover:bg-gray-100 ${
                language === currentLanguage ? 'bg-blue-50 text-blue-700' : ''
              }`}
              data-testid={`language-option-${language}`}
            >
              {languageNames[language]}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

// Helper function for backward compatibility
export function translate(text, lang) { 
  return `Translated ${text} to ${lang}`; 
}

export default MultilingualEngine;
