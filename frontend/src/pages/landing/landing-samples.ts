export type LandingSample = {
    id: string
    titleKey: string
    excerptKey: string
    categoryKey: string
    contextKey: string
    model: string
    rating: number
    tone: 'amber' | 'coral' | 'violet' | 'blue'
}

export const landingSamples: LandingSample[] = [
    {
        id: 'writing-draft',
        titleKey: 'landing.samples.writing.title',
        excerptKey: 'landing.samples.writing.excerpt',
        categoryKey: 'landing.samples.writing.category',
        contextKey: 'landing.samples.writing.context',
        model: 'GPT-4',
        rating: 5,
        tone: 'amber',
    },
    {
        id: 'planning-focus',
        titleKey: 'landing.samples.planning.title',
        excerptKey: 'landing.samples.planning.excerpt',
        categoryKey: 'landing.samples.planning.category',
        contextKey: 'landing.samples.planning.context',
        model: 'Claude',
        rating: 5,
        tone: 'coral',
    },
    {
        id: 'api-review',
        titleKey: 'landing.samples.codeReview.title',
        excerptKey: 'landing.samples.codeReview.excerpt',
        categoryKey: 'landing.samples.codeReview.category',
        contextKey: 'landing.samples.codeReview.context',
        model: 'GPT-4',
        rating: 5,
        tone: 'violet',
    },
    {
        id: 'learning-quiz',
        titleKey: 'landing.samples.learning.title',
        excerptKey: 'landing.samples.learning.excerpt',
        categoryKey: 'landing.samples.learning.category',
        contextKey: 'landing.samples.learning.context',
        model: 'Gemini',
        rating: 4,
        tone: 'blue',
    },
]
