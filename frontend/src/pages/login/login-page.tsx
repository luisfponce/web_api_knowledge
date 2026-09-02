import { useState, type FormEvent } from 'react'
import { useTranslation } from 'react-i18next'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { Card } from '../../components/ui/card'
import { InlineError } from '../../components/ui/inline-error'
import { Button } from '../../components/ui/button'
import { Input } from '../../components/ui/input'
import { LanguageSwitcher } from '../../components/i18n/language-switcher'
import { ThemeToggle } from '../../components/ui/theme-toggle'
import { useAuth } from '../../features/auth/auth-store'
import { useDocumentTitle } from '../../lib/hooks/use-document-title'
import { loginSchema } from '../../lib/validation/auth-schemas'

export function LoginPage() {
    const { t } = useTranslation()
    useDocumentTitle(t('titles.signIn'))
    const navigate = useNavigate()
    const [searchParams] = useSearchParams()
    const { login } = useAuth()
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState<string | null>(null)
    const [loading, setLoading] = useState(false)

    const onSubmit = async (event: FormEvent) => {
        event.preventDefault()

        const parsed = loginSchema.safeParse({ username, password })
        if (!parsed.success) {
            setError(parsed.error.issues[0]?.message ?? t('auth.invalidCredentials'))
            return
        }

        try {
            setLoading(true)
            setError(null)
            await login(parsed.data.username, parsed.data.password)
            navigate('/app/prompts', { replace: true })
        } catch (err) {
            setError(err instanceof Error ? err.message : t('auth.unableToLogin'))
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
                        <h1>{t('auth.loginTitle')}</h1>
                        <p className="muted">{t('auth.loginDescription')}</p>
                    </div>
                    <form className="stack" onSubmit={onSubmit}>
                        {searchParams.get('registered') ? (
                            <div className="success-panel">{t('auth.registered')}</div>
                        ) : null}
                        <Input
                            label={t('auth.username')}
                            value={username}
                            onChange={(event) => setUsername(event.target.value)}
                            autoComplete="username"
                        />
                        <Input
                            label={t('auth.password')}
                            value={password}
                            type="password"
                            onChange={(event) => setPassword(event.target.value)}
                            autoComplete="current-password"
                        />
                        {error ? <InlineError message={error} /> : null}
                        <Button type="submit" disabled={loading}>
                            {loading ? t('auth.signingIn') : t('nav.signIn')}
                        </Button>
                        <Link className="text-link" to="/recovery">
                            {t('auth.forgotPassword')}
                        </Link>
                        <Link className="text-link" to="/register">
                            {t('auth.needAccount')}
                        </Link>
                        <Link className="text-link" to="/">
                            {t('auth.backToLanding')}
                        </Link>
                    </form>
                </Card>
            </div>
        </div>
    )
}
