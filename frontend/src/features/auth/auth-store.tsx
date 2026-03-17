/* eslint-disable react-refresh/only-export-components */
import {
    createContext,
    useCallback,
    useContext,
    useMemo,
    useState,
    type ReactNode,
} from 'react'
import { loginAndResolveUserId } from './auth-service'

type SessionState = {
    token: string | null
    username: string | null
    userId: number | null
}

type AuthContextValue = {
    session: SessionState
    isAuthenticated: boolean
    login: (username: string, password: string) => Promise<void>
    logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

type AuthProviderProps = {
    children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
    const [session, setSession] = useState<SessionState>({
        token: null,
        username: null,
        userId: null,
    })

    const login = useCallback(async (username: string, password: string) => {
        const resolved = await loginAndResolveUserId({ username, password })
        setSession({
            token: resolved.token,
            username: resolved.username,
            userId: resolved.userId,
        })
    }, [])

    const logout = useCallback(() => {
        setSession({ token: null, username: null, userId: null })
    }, [])

    const value = useMemo<AuthContextValue>(
        () => ({
            session,
            isAuthenticated: Boolean(session.token),
            login,
            logout,
        }),
        [login, logout, session],
    )

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
    const context = useContext(AuthContext)
    if (!context) {
        throw new Error('useAuth must be used within AuthProvider')
    }
    return context
}
