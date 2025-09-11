import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { 
  SUPPORTED_LANGUAGES, 
  setLanguage, 
  getCurrentLanguage,
  getLanguageDirection,
  isRTL 
} from '../i18n';

const LanguageSwitcher = ({ className = '' }) => {
  const { t, i18n } = useTranslation();
  const [currentLang, setCurrentLang] = useState(getCurrentLanguage());
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    const handleLanguageChange = (lng) => {
      setCurrentLang(lng);
      
      // Update document direction for RTL support
      document.documentElement.dir = getLanguageDirection(lng);
      
      // Update document language
      document.documentElement.lang = lng;
      
      // Add RTL class to body for styling
      if (isRTL(lng)) {
        document.body.classList.add('rtl');
        document.body.classList.remove('ltr');
      } else {
        document.body.classList.add('ltr');
        document.body.classList.remove('rtl');
      }
    };

    i18n.on('languageChanged', handleLanguageChange);
    
    // Set initial direction
    handleLanguageChange(currentLang);

    return () => {
      i18n.off('languageChanged', handleLanguageChange);
    };
  }, [i18n, currentLang]);

  const handleLanguageChange = (langCode) => {
    setLanguage(langCode);
    setIsOpen(false);
  };

  const currentLanguage = SUPPORTED_LANGUAGES[currentLang];
  const direction = getLanguageDirection(currentLang);

  return (
    <div className={`relative inline-block text-left ${className}`}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`inline-flex items-center justify-center w-full px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${
          direction === 'rtl' ? 'flex-row-reverse' : ''
        }`}
        dir={direction}
      >
        <span className="mr-2">{currentLanguage?.flag}</span>
        <span className={`${direction === 'rtl' ? 'mr-2 ml-0' : 'mr-2'}`}>
          {currentLanguage?.name}
        </span>
        <svg
          className={`w-4 h-4 ${direction === 'rtl' ? 'mr-2 ml-0' : 'ml-2'} ${
            isOpen ? 'transform rotate-180' : ''
          }`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </button>

      {isOpen && (
        <div
          className={`absolute z-50 mt-2 w-64 bg-white border border-gray-300 rounded-md shadow-lg ${
            direction === 'rtl' ? 'left-0' : 'right-0'
          }`}
          dir={direction}
        >
          <div className="py-1 max-h-64 overflow-y-auto">
            {Object.entries(SUPPORTED_LANGUAGES).map(([langCode, langInfo]) => (
              <button
                key={langCode}
                onClick={() => handleLanguageChange(langCode)}
                className={`w-full text-left px-4 py-2 text-sm hover:bg-gray-100 focus:outline-none focus:bg-gray-100 ${
                  langCode === currentLang ? 'bg-blue-50 text-blue-600' : 'text-gray-700'
                } ${direction === 'rtl' ? 'text-right' : 'text-left'} ${
                  langInfo.rtl ? 'flex flex-row-reverse' : 'flex'
                }`}
                dir={langInfo.rtl ? 'rtl' : 'ltr'}
              >
                <span className={`${langInfo.rtl ? 'ml-3' : 'mr-3'}`}>
                  {langInfo.flag}
                </span>
                <span className="flex-1">{langInfo.name}</span>
                {langCode === currentLang && (
                  <svg
                    className={`w-4 h-4 text-blue-600 ${
                      langInfo.rtl ? 'mr-2' : 'ml-2'
                    }`}
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                )}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default LanguageSwitcher;