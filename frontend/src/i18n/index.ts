import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import { en } from './locales/en'
import { es } from './locales/es'

export const STORAGE_KEY = 'app.language'
export const DEFAULT_LANGUAGE = 'es'
export const SUPPORTED_LANGUAGES = ['es', 'en'] as const

export type SupportedLanguage = (typeof SUPPORTED_LANGUAGES)[number]

const resources = {
    es: { translation: es },
    en: { translation: en },
}

function isSupportedLanguage(language: string | null): language is SupportedLanguage {
    return SUPPORTED_LANGUAGES.includes(language as SupportedLanguage)
}

export function getInitialLanguage(): SupportedLanguage {
    const urlLanguage = new URLSearchParams(window.location.search).get('lng')
    if (isSupportedLanguage(urlLanguage)) {
        return urlLanguage
    }

    const savedLanguage = localStorage.getItem(STORAGE_KEY)
    if (isSupportedLanguage(savedLanguage)) {
        return savedLanguage
    }

    return DEFAULT_LANGUAGE
}

export function persistLanguage(language: SupportedLanguage) {
    localStorage.setItem(STORAGE_KEY, language)
    document.documentElement.lang = language
    document.documentElement.dir = 'ltr'
}

i18n.use(initReactI18next).init({
    resources,
    lng: getInitialLanguage(),
    fallbackLng: DEFAULT_LANGUAGE,
    supportedLngs: SUPPORTED_LANGUAGES,
    interpolation: {
        escapeValue: false,
    },
})

persistLanguage(i18n.resolvedLanguage as SupportedLanguage)

export { i18n }
