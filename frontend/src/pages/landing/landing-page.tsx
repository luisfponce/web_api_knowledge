import { useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'
import { LanguageSwitcher } from '../../components/i18n/language-switcher'
import { Badge } from '../../components/ui/badge'
import { Card } from '../../components/ui/card'

export function LandingPage() {
    const { t } = useTranslation()
    const features = t('landing.features', { returnObjects: true }) as string[]

    return (
        <main className="marketing-page">
            <nav className="marketing-nav">
                <strong>{t('app.name')}</strong>
                <div className="row gap-sm">
                    <LanguageSwitcher />
                    <Link className="text-link" to="/login">{t('nav.signIn')}</Link>
                    <Link to="/register" className="button-link">{t('nav.createAccount')}</Link>
                </div>
            </nav>
            <section className="hero-grid">
                <div className="stack">
                    <Badge tone="accent">{t('landing.badge')}</Badge>
                    <h1 className="hero-title">{t('landing.title')}</h1>
                    <p className="hero-copy">
                        {t('landing.copy')}
                    </p>
                    <div className="row gap-sm wrap">
                        <Link to="/register" className="button-link">{t('nav.createAccount')}</Link>
                        <Link to="/login" className="button-link button-link-secondary">{t('nav.signIn')}</Link>
                    </div>
                </div>
                <Card className="showcase-card">
                    <div className="section-heading">
                        <Badge tone="accent">GPT-4</Badge>
                        <span className="badge">{t('common.rating', { value: 5 })}</span>
                    </div>
                    <h2>{t('landing.showcaseTitle')}</h2>
                    <p>
                        {t('landing.showcasePrompt')}
                    </p>
                    <p className="muted">{t('landing.showcaseMeta')}</p>
                </Card>
            </section>
            <section className="feature-grid">
                {features.map((feature) => (
                    <Card key={feature}>
                        <h3>{feature}</h3>
                        <p className="muted">{t('landing.featureDescription')}</p>
                    </Card>
                ))}
            </section>
            <section className="architecture-strip">
                <span>React + TypeScript + Vite</span>
                <span>FastAPI JWT APIs</span>
                <span>MariaDB + Redis</span>
                <a href="http://127.0.0.1:8000/docs" target="_blank" rel="noreferrer">{t('landing.apiDocs')}</a>
            </section>
        </main>
    )
}
