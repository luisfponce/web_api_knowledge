import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { applyTheme, getInitialTheme, type ThemeMode } from '../../lib/utils/theme'
import { Button } from './button'

export function ThemeToggle() {
    const { t } = useTranslation()
    const [theme, setTheme] = useState<ThemeMode>(() => getInitialTheme())

    const toggleTheme = () => {
        const nextTheme: ThemeMode = theme === 'light' ? 'dark' : 'light'
        setTheme(nextTheme)
        applyTheme(nextTheme)
    }

    return (
        <Button type="button" variant="ghost" onClick={toggleTheme}>
            {theme === 'light' ? t('theme.dark') : t('theme.light')}
        </Button>
    )
}
