import { translations } from '../lib/translations';

export type Language = keyof typeof translations;
export type TranslationKey = keyof (typeof translations)['en'];

export const useTranslation = (language: Language) => {
  const t = (key: TranslationKey): string => {
    return translations[language][key] || translations['en'][key];
  };

  return { t, language };
}; 