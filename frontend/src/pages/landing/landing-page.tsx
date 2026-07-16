import { useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'
import { LanguageSwitcher } from '../../components/i18n/language-switcher'
import { Badge } from '../../components/ui/badge'
import { Card } from '../../components/ui/card'
import { ThemeToggle } from '../../components/ui/theme-toggle'
import { landingSamples } from './landing-samples'

export function LandingPage() {
    const { t } = useTranslation()
    const benefits = t('landing.benefits', { returnObjects: true }) as Array<{ title: string; copy: string }>
    const workflow = t('landing.workflow', { returnObjects: true }) as string[]
    const creatorOffers = t('landing.creatorOffers.cards', { returnObjects: true }) as Array<{
        title: string
        category: string
        model: string
        rating: string
        outcome: string
        locked: string
    }>

    return (
        <main className="marketing-page">
            <nav className="marketing-nav">
                <Link className="brand-mark" to="/">
                    <span className="brand-dot" aria-hidden="true" />
                    <span>{t('app.name')}</span>
                </Link>
                <div className="topbar-actions">
                    <LanguageSwitcher />
                    <ThemeToggle />
                    <Link className="text-link" to="/login">{t('nav.signIn')}</Link>
                    <a href="#preview" className="button-link button-link-secondary">{t('landing.primaryCta')}</a>
                </div>
            </nav>
            <section className="hero-grid">
                <div className="stack hero-content">
                    <Badge tone="accent">{t('landing.badge')}</Badge>
                    <h1 className="hero-title">{t('landing.title')}</h1>
                    <p className="hero-copy">
                        {t('landing.copy')}
                    </p>
                    <div className="row gap-sm wrap">
                        <a href="#preview" className="button-link">{t('landing.primaryCta')}</a>
                        <Link to="/register" className="button-link button-link-secondary">{t('landing.secondaryCta')}</Link>
                    </div>
                </div>
                <div className="hero-notebook" aria-hidden="true">
                    <div className="notebook-line notebook-line-strong" />
                    <div className="notebook-line" />
                    <div className="notebook-chip-row">
                        <span />
                        <span />
                        <span />
                    </div>
                    <div className="notebook-card">
                        <strong>{t('landing.samples.writing.title')}</strong>
                        <p>{t('landing.samples.writing.context')}</p>
                    </div>
                </div>
            </section>

            <section id="preview" className="preview-section" aria-labelledby="preview-title" tabIndex={-1}>
                <div className="section-heading preview-heading">
                    <div>
                        <p className="eyebrow">{t('landing.previewEyebrow')}</p>
                        <h2 id="preview-title">{t('landing.previewTitle')}</h2>
                    </div>
                    <p className="muted preview-copy">{t('landing.previewCopy')}</p>
                </div>
                <div className="sample-grid">
                    {landingSamples.map((sample) => (
                        <Card key={sample.id} className={`sample-card sample-card-${sample.tone}`}>
                            <div className="section-heading">
                                <Badge tone="accent">{sample.model}</Badge>
                                <span className="badge">{t('common.rating', { value: sample.rating })}</span>
                            </div>
                            <div className="stack gap-tight">
                                <p className="sample-category">{t(sample.categoryKey)}</p>
                                <h3>{t(sample.titleKey)}</h3>
                                <p>{t(sample.excerptKey)}</p>
                                <p className="muted">{t(sample.contextKey)}</p>
                            </div>
                        </Card>
                    ))}
                </div>
            </section>

            <section className="preview-section creator-offer-section" aria-labelledby="creator-offer-title">
                <div className="section-heading preview-heading">
                    <div>
                        <p className="eyebrow">{t('landing.creatorOffers.eyebrow')}</p>
                        <h2 id="creator-offer-title">{t('landing.creatorOffers.title')}</h2>
                    </div>
                    <p className="muted preview-copy">{t('landing.creatorOffers.copy')}</p>
                </div>
                <div className="sample-grid">
                    {creatorOffers.map((offer) => (
                        <Card key={offer.title} className="sample-card creator-offer-card">
                            <div className="section-heading">
                                <Badge tone="accent">{offer.model}</Badge>
                                <span className="badge">{offer.rating}</span>
                            </div>
                            <div className="stack gap-tight">
                                <p className="sample-category">{offer.category}</p>
                                <h3>{offer.title}</h3>
                                <p>{offer.outcome}</p>
                                <p className="muted">{offer.locked}</p>
                            </div>
                        </Card>
                    ))}
                </div>
                <div className="creator-offer-cta">
                    <p className="muted">{t('landing.creatorOffers.included')}</p>
                    <Link to="/register" className="button-link">{t('landing.creatorOffers.cta')}</Link>
                </div>
            </section>

            <section className="feature-grid" aria-label={t('landing.benefitsLabel')}>
                {benefits.map((benefit) => (
                    <Card key={benefit.title} className="benefit-card">
                        <h3>{benefit.title}</h3>
                        <p className="muted">{benefit.copy}</p>
                    </Card>
                ))}
            </section>

            <section className="workflow-strip" aria-label={t('landing.workflowLabel')}>
                {workflow.map((step, index) => (
                    <span key={step}>
                        <strong>{index + 1}</strong>
                        {step}
                    </span>
                ))}
            </section>

            <section className="final-cta">
                <div>
                    <h2>{t('landing.finalCtaTitle')}</h2>
                    <p className="muted">{t('landing.finalCtaCopy')}</p>
                </div>
                <Link to="/register" className="button-link">{t('landing.finalCtaButton')}</Link>
            </section>

            <footer className="marketing-footer">
                <span>{t('landing.footerOwner')}</span>
                <a href="https://github.com/luisfponce/web_api_knowledge" target="_blank" rel="noreferrer">
                    {t('landing.footerGithub')}
                </a>
            </footer>
        </main>
    )
}
