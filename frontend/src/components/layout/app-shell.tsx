import { useState, type ReactNode } from 'react'
import { NavLink } from 'react-router-dom'
import { useAuth } from '../../features/auth/auth-store'
import { applyTheme, getInitialTheme, type ThemeMode } from '../../lib/utils/theme'
import { Button } from '../ui/button'
import { Badge } from '../ui/badge'

type AppShellProps = {
    children: ReactNode
}

export function AppShell({ children }: AppShellProps) {
    const { session, logout } = useAuth()
    const [theme, setTheme] = useState<ThemeMode>(() => {
        const initial = getInitialTheme()
        applyTheme(initial)
        return initial
    })

    const toggleTheme = () => {
        const nextTheme: ThemeMode = theme === 'light' ? 'dark' : 'light'
        setTheme(nextTheme)
        applyTheme(nextTheme)
    }

    return (
        <div className="page">
            <header className="topbar app-topbar">
                <div>
                    <strong>Prompt Catalog</strong>
                    <p className="muted">Personal library for prompts that work</p>
                </div>
                <div className="topbar-actions">
                    <NavLink className="nav-link" to="/app/prompts">
                        Catalog
                    </NavLink>
                    {session.role === 'admin' || session.role === 'god' ? (
                        <NavLink className="nav-link" to="/app/admin/prompts">
                            Admin
                        </NavLink>
                    ) : null}
                    <Badge tone="accent">{session.username} · {session.role}</Badge>
                    <Button variant="ghost" onClick={toggleTheme}>
                        {theme === 'light' ? 'Dark' : 'Light'}
                    </Button>
                    <Button variant="ghost" onClick={logout}>
                        Logout
                    </Button>
                </div>
            </header>
            <main className="app-main">{children}</main>
        </div>
    )
}
