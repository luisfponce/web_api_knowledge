import { useTranslation } from 'react-i18next'
import { persistLanguage, SUPPORTED_LANGUAGES, type SupportedLanguage } from '../../i18n'

const languageLabels: Record<SupportedLanguage, 'language.spanish' | 'language.english'> = {
    es: 'language.spanish',
    en: 'language.english',
}

export function LanguageSwitcher() {
    const { i18n, t } = useTranslation()
    const currentLanguage = (i18n.resolvedLanguage ?? i18n.language) as SupportedLanguage

    const handleLanguageChange = async (language: SupportedLanguage) => {
        await i18n.changeLanguage(language)
        persistLanguage(language)
    }

    return (
        <label className="language-switcher">
            <span className="sr-only">{t('language.label')}</span>
            <select
                aria-label={t('language.label')}
                className="input language-select"
                value={currentLanguage}
                onChange={(event) => handleLanguageChange(event.target.value as SupportedLanguage)}
            >
                {SUPPORTED_LANGUAGES.map((language) => (
                    <option key={language} value={language}>
                        {t(languageLabels[language])}
                    </option>
                ))}
            </select>
        </label>
    )
}
