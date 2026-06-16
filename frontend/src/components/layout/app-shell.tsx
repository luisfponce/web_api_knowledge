import { useState, type ReactNode } from 'react'
import { NavLink } from 'react-router-dom'
import { useAuth } from '../../features/auth/auth-store'
import { applyTheme, getInitialTheme, type ThemeMode } from '../../lib/utils/theme'
import { Button } from '../ui/button'

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
            <header className="topbar">
                <strong>Prompt Manager</strong>
                <div className="topbar-actions">
                    <NavLink className="nav-link" to="/app/prompts">
                        Prompts
                    </NavLink>
                    {session.role === 'admin' || session.role === 'god' ? (
                        <NavLink className="nav-link" to="/app/admin/prompts">
                            Admin Monitor
                        </NavLink>
                    ) : null}
                    <span className="muted">
                        {session.username} · {session.role}
                    </span>
                    <Button variant="ghost" onClick={toggleTheme}>
                        {theme === 'light' ? 'Dark' : 'Light'}
                    </Button>
                    <Button variant="ghost" onClick={logout}>
                        Logout
                    </Button>
                </div>
            </header>
            <main>{children}</main>
        </div>
    )
}
