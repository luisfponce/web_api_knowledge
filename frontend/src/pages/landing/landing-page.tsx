import { Link } from 'react-router-dom'
import { Badge } from '../../components/ui/badge'
import { Card } from '../../components/ui/card'

const features = [
    'Search prompts by content, model, category, and rating',
    'Reuse proven prompts with copy, edit, duplicate, and delete actions',
    'Admin-ready RBAC with prompt monitoring and future analytics',
]

export function LandingPage() {
    return (
        <main className="marketing-page">
            <nav className="marketing-nav">
                <strong>Prompt Catalog</strong>
                <div className="row gap-sm">
                    <Link className="text-link" to="/login">Sign in</Link>
                    <Link to="/register" className="button-link">Create account</Link>
                </div>
            </nav>
            <section className="hero-grid">
                <div className="stack">
                    <Badge tone="accent">Portfolio-ready full-stack product</Badge>
                    <h1 className="hero-title">Build your personal catalog of prompts that actually work.</h1>
                    <p className="hero-copy">
                        Save, classify, rate, and reuse AI prompts with a focused catalog experience backed by FastAPI, JWT auth, MariaDB, Redis, and React Query.
                    </p>
                    <div className="row gap-sm wrap">
                        <Link to="/register" className="button-link">Create account</Link>
                        <Link to="/login" className="button-link button-link-secondary">Sign in</Link>
                    </div>
                </div>
                <Card className="showcase-card">
                    <div className="section-heading">
                        <Badge tone="accent">GPT-4</Badge>
                        <span className="badge">Rating 5/5</span>
                    </div>
                    <h2>Reusable Architecture Reviewer</h2>
                    <p>
                        Review this API endpoint for authorization gaps, unsafe schemas, and missing regression tests. Return findings by severity.
                    </p>
                    <p className="muted">Category: code-review · Owner: you</p>
                </Card>
            </section>
            <section className="feature-grid">
                {features.map((feature) => (
                    <Card key={feature}>
                        <h3>{feature}</h3>
                        <p className="muted">Designed to turn a basic CRUD into a product recruiters and users can understand quickly.</p>
                    </Card>
                ))}
            </section>
            <section className="architecture-strip">
                <span>React + TypeScript + Vite</span>
                <span>FastAPI JWT APIs</span>
                <span>MariaDB + Redis</span>
                <a href="http://127.0.0.1:8000/docs" target="_blank" rel="noreferrer">Local API docs</a>
            </section>
        </main>
    )
}
