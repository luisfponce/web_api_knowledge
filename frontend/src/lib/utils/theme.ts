const STORAGE_KEY = 'theme-preference'

export type ThemeMode = 'light' | 'dark'

export function getInitialTheme(): ThemeMode {
    const fromStorage = localStorage.getItem(STORAGE_KEY)
    if (fromStorage === 'light' || fromStorage === 'dark') {
        return fromStorage
    }

    return window.matchMedia('(prefers-color-scheme: dark)').matches
        ? 'dark'
        : 'light'
}

export function applyTheme(mode: ThemeMode) {
    document.documentElement.setAttribute('data-theme', mode)
    localStorage.setItem(STORAGE_KEY, mode)
}

