import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card } from '../../components/ui/card'
import { InlineError } from '../../components/ui/inline-error'
import { Button } from '../../components/ui/button'
import { Input } from '../../components/ui/input'
import { useAuth } from '../../features/auth/auth-store'
import { loginSchema } from '../../lib/validation/auth-schemas'

export function LoginPage() {
    const navigate = useNavigate()
    const { login } = useAuth()
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState<string | null>(null)
    const [loading, setLoading] = useState(false)

    const onSubmit = async (event: FormEvent) => {
        event.preventDefault()

        const parsed = loginSchema.safeParse({ username, password })
        if (!parsed.success) {
            setError(parsed.error.issues[0]?.message ?? 'Invalid credentials')
            return
        }

        try {
            setLoading(true)
            setError(null)
            await login(parsed.data.username, parsed.data.password)
            navigate('/app/prompts', { replace: true })
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Unable to login')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="centered-page">
            <Card className="auth-card">
                <h1>Login</h1>
                <p className="muted">Use your API account credentials.</p>
                <form className="stack" onSubmit={onSubmit}>
                    <Input
                        label="Username"
                        value={username}
                        onChange={(event) => setUsername(event.target.value)}
                        autoComplete="username"
                    />
                    <Input
                        label="Password"
                        value={password}
                        type="password"
                        onChange={(event) => setPassword(event.target.value)}
                        autoComplete="current-password"
                    />
                    {error ? <InlineError message={error} /> : null}
                    <Button type="submit" disabled={loading}>
                        {loading ? 'Signing in...' : 'Sign in'}
                    </Button>
                </form>
            </Card>
        </div>
    )
}
