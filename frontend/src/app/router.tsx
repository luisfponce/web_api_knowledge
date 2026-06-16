/* eslint-disable react-refresh/only-export-components */
import { Navigate, Outlet, createBrowserRouter } from 'react-router-dom'
import { AppShell } from '../components/layout/app-shell'
import { useAuth } from '../features/auth/auth-store'
import { AdminPromptsPage } from '../pages/admin/admin-prompts-page'
import { LoginPage } from '../pages/login/login-page'
import { PromptsPage } from '../pages/prompts/prompts-page'
import { RecoveryPage } from '../pages/recovery/recovery-page'

function ProtectedLayout() {
    const { isAuthenticated } = useAuth()
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
    const { isAuthenticated } = useAuth()
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
        path: '/login',
        element: <PublicLoginPage />,
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
        element: <Navigate to="/login" replace />,
    },
])
