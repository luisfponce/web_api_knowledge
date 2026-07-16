import { useState, type FormEvent } from 'react'
import { useTranslation } from 'react-i18next'
import { Link, useNavigate } from 'react-router-dom'
import { Button } from '../../components/ui/button'
import { Card } from '../../components/ui/card'
import { LanguageSwitcher } from '../../components/i18n/language-switcher'
import { InlineError } from '../../components/ui/inline-error'
import { Input } from '../../components/ui/input'
import { Select } from '../../components/ui/select'
import { ThemeToggle } from '../../components/ui/theme-toggle'
import { useAuth } from '../../features/auth/auth-store'
import { ApiError } from '../../lib/http/api-error'
import { registerSchema } from '../../lib/validation/auth-schemas'

export function RegisterPage() {
    const { t, i18n } = useTranslation()
    const navigate = useNavigate()
    const { signup } = useAuth()
    const [form, setForm] = useState({
        name: '',
        last_name: '',
        email: '',
        username: '',
        password: '',
        preferred_language: i18n.resolvedLanguage === 'en' ? 'en' : 'es',
    })
    const [error, setError] = useState<string | null>(null)
    const [loading, setLoading] = useState(false)
    const languageOptions = [
        { value: 'es', label: t('language.spanish') },
        { value: 'en', label: t('language.english') },
    ]

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
            navigate('/app/prompts', { replace: true })
        } catch (err) {
            const message = err instanceof Error ? err.message : t('auth.unableToCreate')
            setError(err instanceof ApiError && err.status === 400 ? t('auth.usernameTaken') : message)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="centered-page auth-gradient">
            <div className="auth-frame">
                <div className="auth-public-bar">
                    <Link className="brand-mark" to="/">
                        <span className="brand-dot" aria-hidden="true" />
                        <span>{t('app.name')}</span>
                    </Link>
                    <div className="row gap-sm wrap">
                        <LanguageSwitcher />
                        <ThemeToggle />
                    </div>
                </div>
                <Card className="auth-card">
                    <div>
                        <h1>{t('auth.registerTitle')}</h1>
                        <p className="muted">{t('auth.registerDescription')}</p>
                    </div>
                    <form className="stack" onSubmit={onSubmit}>
                        <Input label={t('auth.firstName')} value={form.name} onChange={(event) => updateField('name', event.target.value)} autoComplete="given-name" />
                        <Input label={t('auth.lastName')} value={form.last_name} onChange={(event) => updateField('last_name', event.target.value)} autoComplete="family-name" />
                        <Input label={t('auth.email')} value={form.email} onChange={(event) => updateField('email', event.target.value)} autoComplete="email" />
                        <Input label={t('auth.username')} value={form.username} onChange={(event) => updateField('username', event.target.value)} autoComplete="username" />
                        <Input label={t('auth.password')} type="password" value={form.password} onChange={(event) => updateField('password', event.target.value)} autoComplete="new-password" />
                        <Select
                            label={t('auth.preferredLanguage')}
                            options={languageOptions}
                            value={form.preferred_language}
                            onChange={(event) => updateField('preferred_language', event.target.value)}
                        />
                        <p className="muted form-helper">{t('auth.preferredLanguageHelp')}</p>
                        {error ? <InlineError message={error} /> : null}
                        <Button type="submit" disabled={loading}>{loading ? t('auth.creating') : t('nav.createAccount')}</Button>
                        <Link className="text-link" to="/login">{t('auth.alreadyHaveAccount')}</Link>
                        <Link className="text-link" to="/">{t('auth.backToLanding')}</Link>
                    </form>
                </Card>
            </div>
        </div>
    )
}
