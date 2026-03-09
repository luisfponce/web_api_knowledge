/* eslint-disable react-refresh/only-export-components */
import { Navigate, Outlet, createBrowserRouter } from 'react-router-dom'
import { AppShell } from '../components/layout/app-shell'
import { useAuth } from '../features/auth/auth-store'
import { LoginPage } from '../pages/login/login-page'
import { PromptsPage } from '../pages/prompts/prompts-page'

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

export const router = createBrowserRouter([
    {
        path: '/login',
        element: <PublicLoginPage />,
    },
    {
        path: '/app',
        element: <ProtectedLayout />,
        children: [
            {
                path: 'prompts',
                element: <PromptsPage />,
            },
        ],
    },
    {
        path: '*',
        element: <Navigate to="/login" replace />,
    },
])
