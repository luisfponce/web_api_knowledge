import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Button } from '../../components/ui/button'
import { Card } from '../../components/ui/card'
import { InlineError } from '../../components/ui/inline-error'
import { Input } from '../../components/ui/input'
import { signup } from '../../features/auth/auth-service'
import { ApiError } from '../../lib/http/api-error'
import { registerSchema } from '../../lib/validation/auth-schemas'

export function RegisterPage() {
    const navigate = useNavigate()
    const [form, setForm] = useState({ name: '', last_name: '', email: '', username: '', password: '' })
    const [error, setError] = useState<string | null>(null)
    const [loading, setLoading] = useState(false)

    const updateField = (field: keyof typeof form, value: string) => {
        setForm((current) => ({ ...current, [field]: value }))
    }

    const onSubmit = async (event: FormEvent) => {
        event.preventDefault()
        const parsed = registerSchema.safeParse(form)
        if (!parsed.success) {
            setError(parsed.error.issues[0]?.message ?? 'Check your registration details')
            return
        }

        try {
            setLoading(true)
            setError(null)
            await signup({ ...parsed.data, role: 'user' })
            navigate('/login?registered=1', { replace: true })
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Unable to create account'
            setError(err instanceof ApiError && err.status === 400 ? 'Username is already taken' : message)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="centered-page auth-gradient">
            <Card className="auth-card">
                <h1>Create account</h1>
                <p className="muted">Start building a catalog of prompts you can trust and reuse.</p>
                <form className="stack" onSubmit={onSubmit}>
                    <Input label="First name" value={form.name} onChange={(event) => updateField('name', event.target.value)} autoComplete="given-name" />
                    <Input label="Last name" value={form.last_name} onChange={(event) => updateField('last_name', event.target.value)} autoComplete="family-name" />
                    <Input label="Email" value={form.email} onChange={(event) => updateField('email', event.target.value)} autoComplete="email" />
                    <Input label="Username" value={form.username} onChange={(event) => updateField('username', event.target.value)} autoComplete="username" />
                    <Input label="Password" type="password" value={form.password} onChange={(event) => updateField('password', event.target.value)} autoComplete="new-password" />
                    {error ? <InlineError message={error} /> : null}
                    <Button type="submit" disabled={loading}>{loading ? 'Creating...' : 'Create account'}</Button>
                    <Link className="text-link" to="/login">Already have an account?</Link>
                </form>
            </Card>
        </div>
    )
}
