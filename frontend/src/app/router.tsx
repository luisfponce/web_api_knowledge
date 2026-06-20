/* eslint-disable react-refresh/only-export-components */
import { Navigate, Outlet, createBrowserRouter } from 'react-router-dom'
import { AppShell } from '../components/layout/app-shell'
import { useAuth } from '../features/auth/auth-store'
import { AdminPromptsPage } from '../pages/admin/admin-prompts-page'
import { LandingPage } from '../pages/landing/landing-page'
import { LoginPage } from '../pages/login/login-page'
import { NotFoundPage } from '../pages/not-found/not-found-page'
import { PromptsPage } from '../pages/prompts/prompts-page'
import { RecoveryPage } from '../pages/recovery/recovery-page'
import { RegisterPage } from '../pages/register/register-page'

function ProtectedLayout() {
    const { isAuthenticated, isReady } = useAuth()
    if (!isReady) {
        return <div className="centered-page"><p className="muted">Restoring session...</p></div>
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />
    }

    return (
        <AppShell>
            <Outlet />
        </AppShell>
    )
}

function PublicLoginPage() {
    const { isAuthenticated, isReady } = useAuth()
    if (!isReady) {
        return <div className="centered-page"><p className="muted">Loading...</p></div>
    }

    if (isAuthenticated) {
        return <Navigate to="/app/prompts" replace />
    }
    return <LoginPage />
}

function RoleGuard() {
    const { session } = useAuth()
    if (session.role !== 'admin' && session.role !== 'god') {
        return <Navigate to="/app/prompts" replace />
    }

    return <Outlet />
}

export const router = createBrowserRouter([
    {
        path: '/',
        element: <LandingPage />,
    },
    {
        path: '/login',
        element: <PublicLoginPage />,
    },
    {
        path: '/register',
        element: <RegisterPage />,
    },
    {
        path: '/recovery',
        element: <RecoveryPage />,
    },
    {
        path: '/app',
        element: <ProtectedLayout />,
        children: [
            {
                index: true,
                element: <Navigate to="/app/prompts" replace />,
            },
            {
                path: 'prompts',
                element: <PromptsPage />,
            },
            {
                path: 'admin',
                element: <RoleGuard />,
                children: [
                    {
                        path: 'prompts',
                        element: <AdminPromptsPage />,
                    },
                ],
            },
        ],
    },
    {
        path: '*',
        element: <NotFoundPage />,
    },
])
