import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import type { PromptRecord } from '../../features/prompts/prompts-types'
import { EmptyState } from '../ui/empty-state'
import { PromptDetailDialog } from './prompt-detail-dialog'

type PromptListProps = {
    prompts: PromptRecord[]
    onEdit: (prompt: PromptRecord) => void
    onDelete: (prompt: PromptRecord) => void
}

function summarizePromptText(text: string, maxLength = 140) {
    const normalizedText = text.trim().replace(/\s+/g, ' ')

    if (normalizedText.length <= maxLength) {
        return normalizedText
    }

    return `${normalizedText.slice(0, maxLength).trimEnd()}...`
}

export function PromptList({ prompts, onEdit, onDelete }: PromptListProps) {
    const { t } = useTranslation()
    const [selectedPrompt, setSelectedPrompt] = useState<PromptRecord | null>(null)

    if (!prompts.length) {
        return (
            <EmptyState
                title={t('prompts.emptyTitle')}
                description={t('prompts.emptyDescription')}
            />
        )
    }

    return (
        <>
            <div className="list prompt-list">
                {prompts.map((prompt) => {
                    const summary = summarizePromptText(prompt.prompt_text)

                    return (
                        <button
                            key={prompt.id}
                            type="button"
                            className="prompt-list-item"
                            onClick={() => setSelectedPrompt(prompt)}
                        >
                            <span className="prompt-list-summary">{summary}</span>
                            <span className="prompt-list-meta">
                                <span className="badge">{prompt.category}</span>
                                <span className="muted">{t('common.rating', { value: prompt.rate })}</span>
                            </span>
                            <span className="sr-only">{t('prompts.viewDetails')}</span>
                        </button>
                    )
                })}
            </div>
            <PromptDetailDialog
                prompt={selectedPrompt}
                onClose={() => setSelectedPrompt(null)}
                onEdit={onEdit}
                onDelete={onDelete}
            />
        </>
    )
}
