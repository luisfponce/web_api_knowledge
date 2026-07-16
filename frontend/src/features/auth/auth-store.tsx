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
import { getCurrentUser, loginAndResolveUserId, signupAndResolveSession } from './auth-service'
import type { PreferredLanguage, RegisterInput, UserRole } from './auth-types'

type SessionState = {
    token: string | null
    username: string | null
    userId: number | null
    role: UserRole | null
    preferredLanguage: PreferredLanguage | null
}

type AuthContextValue = {
    session: SessionState
    isAuthenticated: boolean
    isReady: boolean
    login: (username: string, password: string) => Promise<void>
    signup: (input: RegisterInput) => Promise<void>
    logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)
const SESSION_TOKEN_KEY = 'prompt-catalog-token'

type AuthProviderProps = {
    children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
    const [initialToken] = useState(() =>
        typeof sessionStorage === 'undefined' ? null : sessionStorage.getItem(SESSION_TOKEN_KEY),
    )
    const [session, setSession] = useState<SessionState>({
        token: null,
        username: null,
        userId: null,
        role: null,
        preferredLanguage: null,
    })
    const [isReady, setIsReady] = useState(() => !initialToken)

    useEffect(() => {
        if (!initialToken) return

        let cancelled = false
        getCurrentUser(initialToken)
            .then((user) => {
                if (cancelled) return
                setSession({
                    token: initialToken,
                    username: user.username,
                    userId: user.id,
                    role: user.role,
                    preferredLanguage: user.preferred_language,
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
    }, [initialToken])

    const login = useCallback(async (username: string, password: string) => {
        const resolved = await loginAndResolveUserId({ username, password })
        sessionStorage.setItem(SESSION_TOKEN_KEY, resolved.token)
        setSession({
            token: resolved.token,
            username: resolved.username,
            userId: resolved.userId,
            role: resolved.role,
            preferredLanguage: resolved.preferredLanguage,
        })
    }, [])

    const signup = useCallback(async (input: RegisterInput) => {
        const resolved = await signupAndResolveSession(input)
        sessionStorage.setItem(SESSION_TOKEN_KEY, resolved.token)
        setSession({
            token: resolved.token,
            username: resolved.username,
            userId: resolved.userId,
            role: resolved.role,
            preferredLanguage: resolved.preferredLanguage,
        })
    }, [])

    const logout = useCallback(() => {
        sessionStorage.removeItem(SESSION_TOKEN_KEY)
        setSession({ token: null, username: null, userId: null, role: null, preferredLanguage: null })
    }, [])

    const value = useMemo<AuthContextValue>(
        () => ({
            session,
            isAuthenticated: Boolean(session.token),
            isReady,
            login,
            signup,
            logout,
        }),
        [isReady, login, logout, session, signup],
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
