import { useState, type FormEvent } from 'react'
import { useTranslation } from 'react-i18next'
import { Link, useNavigate } from 'react-router-dom'
import { Button } from '../../components/ui/button'
import { Card } from '../../components/ui/card'
import { InlineError } from '../../components/ui/inline-error'
import { Input } from '../../components/ui/input'
import { signup } from '../../features/auth/auth-service'
import { ApiError } from '../../lib/http/api-error'
import { registerSchema } from '../../lib/validation/auth-schemas'

export function RegisterPage() {
    const { t } = useTranslation()
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
            setError(parsed.error.issues[0]?.message ?? t('auth.checkRegistration'))
            return
        }

        try {
            setLoading(true)
            setError(null)
            await signup(parsed.data)
            navigate('/login?registered=1', { replace: true })
        } catch (err) {
            const message = err instanceof Error ? err.message : t('auth.unableToCreate')
            setError(err instanceof ApiError && err.status === 400 ? t('auth.usernameTaken') : message)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="centered-page auth-gradient">
            <Card className="auth-card">
                <h1>{t('auth.registerTitle')}</h1>
                <p className="muted">{t('auth.registerDescription')}</p>
                <form className="stack" onSubmit={onSubmit}>
                    <Input label={t('auth.firstName')} value={form.name} onChange={(event) => updateField('name', event.target.value)} autoComplete="given-name" />
                    <Input label={t('auth.lastName')} value={form.last_name} onChange={(event) => updateField('last_name', event.target.value)} autoComplete="family-name" />
                    <Input label={t('auth.email')} value={form.email} onChange={(event) => updateField('email', event.target.value)} autoComplete="email" />
                    <Input label={t('auth.username')} value={form.username} onChange={(event) => updateField('username', event.target.value)} autoComplete="username" />
                    <Input label={t('auth.password')} type="password" value={form.password} onChange={(event) => updateField('password', event.target.value)} autoComplete="new-password" />
                    {error ? <InlineError message={error} /> : null}
                    <Button type="submit" disabled={loading}>{loading ? t('auth.creating') : t('nav.createAccount')}</Button>
                    <Link className="text-link" to="/login">{t('auth.alreadyHaveAccount')}</Link>
                </form>
            </Card>
        </div>
    )
}
