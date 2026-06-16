import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '../../components/ui/button'
import { Card } from '../../components/ui/card'
import { InlineError } from '../../components/ui/inline-error'
import { Input } from '../../components/ui/input'
import { redeemRecoveryKey, requestRecoveryKey } from '../../features/auth/auth-service'
import {
    recoveryRedeemSchema,
    recoveryRequestSchema,
} from '../../lib/validation/auth-schemas'

export function RecoveryPage() {
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
            setError(parsed.error.issues[0]?.message ?? 'Invalid username')
            return
        }

        try {
            setLoading(true)
            setError(null)
            setTemporaryPassword(null)
            const response = await requestRecoveryKey(parsed.data)
            setMessage(response.message)
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Unable to request recovery key')
        } finally {
            setLoading(false)
        }
    }

    const handleRedeem = async (event: FormEvent) => {
        event.preventDefault()
        const parsed = recoveryRedeemSchema.safeParse({ key })
        if (!parsed.success) {
            setError(parsed.error.issues[0]?.message ?? 'Invalid recovery key')
            return
        }

        try {
            setLoading(true)
            setError(null)
            const response = await redeemRecoveryKey(parsed.data)
            setTemporaryPassword(response.password)
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Unable to redeem recovery key')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="centered-page">
            <Card className="auth-card stack">
                <div>
                    <h1>Recovery</h1>
                    <p className="muted">Request a recovery key, then redeem it for your temporary password.</p>
                </div>

                <form className="stack" onSubmit={handleRequest}>
                    <Input
                        label="Username"
                        value={username}
                        onChange={(event) => setUsername(event.target.value)}
                        autoComplete="username"
                    />
                    <Button type="submit" disabled={loading}>
                        {loading ? 'Requesting...' : 'Request recovery key'}
                    </Button>
                </form>

                <form className="stack" onSubmit={handleRedeem}>
                    <Input
                        label="Recovery key"
                        value={key}
                        onChange={(event) => setKey(event.target.value)}
                        autoComplete="off"
                    />
                    <Button type="submit" disabled={loading} variant="ghost">
                        {loading ? 'Checking...' : 'Redeem key'}
                    </Button>
                </form>

                {message ? <p className="muted">{message}</p> : null}
                {temporaryPassword ? (
                    <div className="result-panel">
                        <span className="label">Temporary password</span>
                        <strong>{temporaryPassword}</strong>
                        <p className="muted">Use this password to sign in, then update it.</p>
                    </div>
                ) : null}
                {error ? <InlineError message={error} /> : null}
                <Link className="text-link" to="/login">
                    Return to login
                </Link>
            </Card>
        </div>
    )
}
