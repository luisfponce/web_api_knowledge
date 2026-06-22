/* eslint-disable react-refresh/only-export-components */
import {
    createContext,
    useCallback,
    useContext,
    useEffect,
    useMemo,
    useState,
    type ReactNode,
} from 'react'
import { getCurrentUser, loginAndResolveUserId } from './auth-service'
import type { UserRole } from './auth-types'

type SessionState = {
    token: string | null
    username: string | null
    userId: number | null
    role: UserRole | null
}

type AuthContextValue = {
    session: SessionState
    isAuthenticated: boolean
    isReady: boolean
    login: (username: string, password: string) => Promise<void>
    logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)
const SESSION_TOKEN_KEY = 'prompt-catalog-token'

type AuthProviderProps = {
    children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
    const [session, setSession] = useState<SessionState>({
        token: null,
        username: null,
        userId: null,
        role: null,
    })
    const [isReady, setIsReady] = useState(false)

    useEffect(() => {
        const token = sessionStorage.getItem(SESSION_TOKEN_KEY)
        if (!token) {
            setIsReady(true)
            return
        }

        let cancelled = false
        getCurrentUser(token)
            .then((user) => {
                if (cancelled) return
                setSession({
                    token,
                    username: user.username,
                    userId: user.id,
                    role: user.role,
                })
            })
            .catch(() => {
                sessionStorage.removeItem(SESSION_TOKEN_KEY)
            })
            .finally(() => {
                if (!cancelled) setIsReady(true)
            })

        return () => {
            cancelled = true
        }
    }, [])

    const login = useCallback(async (username: string, password: string) => {
        const resolved = await loginAndResolveUserId({ username, password })
        sessionStorage.setItem(SESSION_TOKEN_KEY, resolved.token)
        setSession({
            token: resolved.token,
            username: resolved.username,
            userId: resolved.userId,
            role: resolved.role,
        })
    }, [])

    const logout = useCallback(() => {
        sessionStorage.removeItem(SESSION_TOKEN_KEY)
        setSession({ token: null, username: null, userId: null, role: null })
    }, [])

    const value = useMemo<AuthContextValue>(
        () => ({
            session,
            isAuthenticated: Boolean(session.token),
            isReady,
            login,
            logout,
        }),
        [isReady, login, logout, session],
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
