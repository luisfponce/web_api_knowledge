import { Link } from 'react-router-dom'
import { Card } from '../../components/ui/card'

export function NotFoundPage() {
    return (
        <div className="centered-page">
            <Card className="auth-card stack">
                <p className="eyebrow">404</p>
                <h1>Page not found</h1>
                <p className="muted">This route does not exist in Prompt Catalog.</p>
                <Link to="/" className="button-link">Back to landing</Link>
            </Card>
        </div>
    )
}
