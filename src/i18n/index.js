import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import Backend from 'i18next-http-backend';

// Import translation files
import enUS from './locales/en-US.json';
import enGB from './locales/en-GB.json';
import deDE from './locales/de-DE.json';
import frFR from './locales/fr-FR.json';
import esES from './locales/es-ES.json';
import itIT from './locales/it-IT.json';
import jaJP from './locales/ja-JP.json';
import koKR from './locales/ko-KR.json';
import zhCN from './locales/zh-CN.json';
import arSA from './locales/ar-SA.json';
import heIL from './locales/he-IL.json';
import faIR from './locales/fa-IR.json';
import hiIN from './locales/hi-IN.json';
import msMY from './locales/ms-MY.json';

// RTL languages configuration
export const RTL_LANGUAGES = ['ar', 'he', 'fa'];

export const SUPPORTED_LANGUAGES = {
  'en-US': { name: 'English (US)', flag: '🇺🇸', rtl: false },
  'en-GB': { name: 'English (UK)', flag: '🇬🇧', rtl: false },
  'de-DE': { name: 'Deutsch', flag: '🇩🇪', rtl: false },
  'fr-FR': { name: 'Français', flag: '🇫🇷', rtl: false },
  'es-ES': { name: 'Español', flag: '🇪🇸', rtl: false },
  'it-IT': { name: 'Italiano', flag: '🇮🇹', rtl: false },
  'ja-JP': { name: '日本語', flag: '🇯🇵', rtl: false },
  'ko-KR': { name: '한국어', flag: '🇰🇷', rtl: false },
  'zh-CN': { name: '中文 (简体)', flag: '🇨🇳', rtl: false },
  'ar-SA': { name: 'العربية', flag: '🇸🇦', rtl: true },
  'he-IL': { name: 'עברית', flag: '🇮🇱', rtl: true },
  'fa-IR': { name: 'فارسی', flag: '🇮🇷', rtl: true },
  'hi-IN': { name: 'हिन्दी', flag: '🇮🇳', rtl: false },
  'ms-MY': { name: 'Bahasa Malaysia', flag: '🇲🇾', rtl: false }
};

// Regional language mappings
export const REGION_LANGUAGES = {
  'us-east-1': ['en-US', 'es-ES'],
  'us-west-2': ['en-US', 'es-ES'],
  'eu-west-1': ['en-GB', 'de-DE', 'fr-FR', 'es-ES', 'it-IT'],
  'eu-central-1': ['de-DE', 'en-GB', 'fr-FR'],
  'ap-southeast-1': ['en-GB', 'zh-CN', 'ms-MY', 'hi-IN'],
  'ap-northeast-1': ['ja-JP', 'en-GB', 'ko-KR'],
  'me-south-1': ['ar-SA', 'en-US', 'fa-IR', 'he-IL']
};

// Detection options
const detectionOptions = {
  order: ['querystring', 'cookie', 'localStorage', 'sessionStorage', 'navigator', 'htmlTag'],
  lookupQuerystring: 'lng',
  lookupCookie: 'language',
  lookupLocalStorage: 'i18nextLng',
  lookupSessionStorage: 'i18nextLng',
  lookupFromPathIndex: 0,
  lookupFromSubdomainIndex: 0,
  caches: ['localStorage', 'cookie'],
  excludeCacheFor: ['cimode'],
  cookieMinutes: 10080, // 7 days
  cookieDomain: 'ai-heart-platform.com'
};

// Initialize i18next
i18n
  .use(Backend)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      'en-US': { translation: enUS },
      'en-GB': { translation: enGB },
      'de-DE': { translation: deDE },
      'fr-FR': { translation: frFR },
      'es-ES': { translation: esES },
      'it-IT': { translation: itIT },
      'ja-JP': { translation: jaJP },
      'ko-KR': { translation: koKR },
      'zh-CN': { translation: zhCN },
      'ar-SA': { translation: arSA },
      'he-IL': { translation: heIL },
      'fa-IR': { translation: faIR },
      'hi-IN': { translation: hiIN },
      'ms-MY': { translation: msMY }
    },
    fallbackLng: 'en-US',
    debug: process.env.NODE_ENV === 'development',
    
    detection: detectionOptions,
    
    interpolation: {
      escapeValue: false, // React already escapes values
    },
    
    backend: {
      loadPath: '/locales/{{lng}}.json',
      addPath: '/locales/add/{{lng}}/{{ns}}'
    },
    
    react: {
      useSuspense: false,
      transSupportBasicHtmlNodes: true,
      transKeepBasicHtmlNodesFor: ['br', 'strong', 'i', 'em', 'span']
    },
    
    // Namespace configuration
    ns: ['translation'],
    defaultNS: 'translation',
    
    // Pluralization rules for different languages
    pluralSeparator: '_',
    contextSeparator: '_',
    
    // Key separator
    keySeparator: '.',
    nsSeparator: ':',
    
    // Formatting
    returnNull: false,
    returnEmptyString: false,
    
    // Load resources
    load: 'languageOnly',
    preload: ['en-US'],
    
    // Clean up code
    cleanCode: true,
    
    // Savemissing keys in development
    saveMissing: process.env.NODE_ENV === 'development',
    saveMissingTo: 'fallback',
    
    // Performance
    partialBundledLanguages: true
  });

// Helper functions
export const isRTL = (language) => {
  const langCode = language.split('-')[0];
  return RTL_LANGUAGES.includes(langCode);
};

export const getLanguageDirection = (language) => {
  return isRTL(language) ? 'rtl' : 'ltr';
};

export const getRegionalLanguages = (region) => {
  return REGION_LANGUAGES[region] || ['en-US'];
};

export const getBrowserLanguage = () => {
  const browserLang = navigator.language || navigator.languages[0];
  const supportedLangs = Object.keys(SUPPORTED_LANGUAGES);
  
  // Exact match
  if (supportedLangs.includes(browserLang)) {
    return browserLang;
  }
  
  // Language family match (e.g., 'en' matches 'en-US')
  const langFamily = browserLang.split('-')[0];
  const familyMatch = supportedLangs.find(lang => lang.startsWith(langFamily));
  
  return familyMatch || 'en-US';
};

export const setLanguage = (language) => {
  i18n.changeLanguage(language);
  
  // Update HTML lang attribute
  document.documentElement.lang = language;
  
  // Update HTML dir attribute for RTL support
  document.documentElement.dir = getLanguageDirection(language);
  
  // Store in localStorage for persistence
  localStorage.setItem('i18nextLng', language);
  
  // Set cookie for server-side rendering
  document.cookie = `language=${language}; max-age=${detectionOptions.cookieMinutes * 60}; path=/; domain=${detectionOptions.cookieDomain}`;
};

export const getCurrentLanguage = () => {
  return i18n.language || 'en-US';
};

export const getAvailableLanguages = () => {
  return Object.keys(SUPPORTED_LANGUAGES);
};

export default i18n;