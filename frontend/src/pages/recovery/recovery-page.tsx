import { useState, type FormEvent } from 'react'
import { useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'
import { LanguageSwitcher } from '../../components/i18n/language-switcher'
import { Button } from '../../components/ui/button'
import { Card } from '../../components/ui/card'
import { InlineError } from '../../components/ui/inline-error'
import { Input } from '../../components/ui/input'
import { ThemeToggle } from '../../components/ui/theme-toggle'
import { redeemRecoveryKey, requestRecoveryKey } from '../../features/auth/auth-service'
import {
    recoveryRedeemSchema,
    recoveryRequestSchema,
} from '../../lib/validation/auth-schemas'

export function RecoveryPage() {
    const { t } = useTranslation()
    const [username, setUsername] = useState('')
    const [key, setKey] = useState('')
    const [message, setMessage] = useState<string | null>(null)
    const [temporaryPassword, setTemporaryPassword] = useState<string | null>(null)
    const [error, setError] = useState<string | null>(null)
    const [loading, setLoading] = useState(false)

    const handleRequest = async (event: FormEvent) => {
        event.preventDefault()
        const parsed = recoveryRequestSchema.safeParse({ username })
        if (!parsed.success) {
            setError(parsed.error.issues[0]?.message ?? t('recovery.invalidUsername'))
            return
        }

        try {
            setLoading(true)
            setError(null)
            setTemporaryPassword(null)
            const response = await requestRecoveryKey(parsed.data)
            setMessage(response.message)
        } catch (err) {
            setError(err instanceof Error ? err.message : t('recovery.unableToRequest'))
        } finally {
            setLoading(false)
        }
    }

    const handleRedeem = async (event: FormEvent) => {
        event.preventDefault()
        const parsed = recoveryRedeemSchema.safeParse({ key })
        if (!parsed.success) {
            setError(parsed.error.issues[0]?.message ?? t('recovery.invalidKey'))
            return
        }

        try {
            setLoading(true)
            setError(null)
            const response = await redeemRecoveryKey(parsed.data)
            setTemporaryPassword(response.password)
        } catch (err) {
            setError(err instanceof Error ? err.message : t('recovery.unableToRedeem'))
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
                <Card className="auth-card stack">
                    <div>
                        <h1>{t('recovery.title')}</h1>
                        <p className="muted">{t('recovery.description')}</p>
                    </div>

                    <form className="stack auth-subcard" onSubmit={handleRequest}>
                        <h2>{t('recovery.requestTitle')}</h2>
                        <Input
                            label={t('recovery.username')}
                            value={username}
                            onChange={(event) => setUsername(event.target.value)}
                            autoComplete="username"
                        />
                        <Button type="submit" disabled={loading}>
                            {loading ? t('recovery.requesting') : t('recovery.requestButton')}
                        </Button>
                    </form>

                    <form className="stack auth-subcard" onSubmit={handleRedeem}>
                        <h2>{t('recovery.redeemTitle')}</h2>
                        <Input
                            label={t('recovery.key')}
                            value={key}
                            onChange={(event) => setKey(event.target.value)}
                            autoComplete="off"
                        />
                        <Button type="submit" disabled={loading} variant="ghost">
                            {loading ? t('recovery.checking') : t('recovery.redeemButton')}
                        </Button>
                    </form>

                    {message ? <p className="muted">{message}</p> : null}
                    {temporaryPassword ? (
                        <div className="result-panel">
                            <span className="label">{t('recovery.temporaryPassword')}</span>
                            <strong>{temporaryPassword}</strong>
                            <p className="muted">{t('recovery.temporaryPasswordHelp')}</p>
                        </div>
                    ) : null}
                    {error ? <InlineError message={error} /> : null}
                    <Link className="text-link" to="/login">
                        {t('recovery.returnToLogin')}
                    </Link>
                </Card>
            </div>
        </div>
    )
}
