import type { ReactNode } from 'react'
import { useTranslation } from 'react-i18next'
import { NavLink } from 'react-router-dom'
import { useAuth } from '../../features/auth/auth-store'
import { LanguageSwitcher } from '../i18n/language-switcher'
import { Button } from '../ui/button'
import { Badge } from '../ui/badge'
import { ThemeToggle } from '../ui/theme-toggle'

type AppShellProps = {
    children: ReactNode
}

export function AppShell({ children }: AppShellProps) {
    const { t } = useTranslation()
    const { session, logout } = useAuth()

    return (
        <div className="page">
            <header className="topbar app-topbar">
                <div>
                    <strong>{t('app.name')}</strong>
                    <p className="muted">{t('app.tagline')}</p>
                </div>
                <div className="topbar-actions">
                    <NavLink className="nav-link" to="/app/prompts">
                        {t('nav.catalog')}
                    </NavLink>
                    {session.role === 'admin' || session.role === 'god' ? (
                        <NavLink className="nav-link" to="/app/admin/prompts">
                            {t('nav.admin')}
                        </NavLink>
                    ) : null}
                    <Badge tone="accent">{session.username} · {session.role}</Badge>
                    <LanguageSwitcher />
                    <ThemeToggle />
                    <Button variant="ghost" onClick={logout}>
                        {t('nav.logout')}
                    </Button>
                </div>
            </header>
            <main className="app-main">{children}</main>
        </div>
    )
}
