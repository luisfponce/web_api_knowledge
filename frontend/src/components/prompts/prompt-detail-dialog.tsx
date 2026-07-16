import { useTranslation } from 'react-i18next'
import type { PromptRecord } from '../../features/prompts/prompts-types'
import { Button } from '../ui/button'

type PromptDetailDialogProps = {
    prompt: PromptRecord | null
    onClose: () => void
    onEdit: (prompt: PromptRecord) => void
    onDelete: (prompt: PromptRecord) => void
}

export function PromptDetailDialog({
    prompt,
    onClose,
    onEdit,
    onDelete,
}: PromptDetailDialogProps) {
    const { t } = useTranslation()

    if (!prompt) return null

    const handleEdit = () => {
        onClose()
        onEdit(prompt)
    }

    const handleDelete = () => {
        onClose()
        onDelete(prompt)
    }

    return (
        <div className="dialog-backdrop" role="presentation" onMouseDown={onClose}>
            <div
                className="dialog-panel prompt-detail-dialog"
                role="dialog"
                aria-modal="true"
                aria-labelledby="prompt-detail-title"
                onMouseDown={(event) => event.stopPropagation()}
            >
                <h2 id="prompt-detail-title">{prompt.title}</h2>
                <div className="prompt-detail-body">
                    <div className="prompt-detail-meta prompt-detail-summary">
                        <div className="prompt-detail-field">
                            <span className="label">{t('prompts.detail.titleLabel')}</span>
                            <strong>{prompt.title}</strong>
                        </div>
                        <div className="prompt-detail-field">
                            <span className="label">{t('prompts.detail.model')}</span>
                            <strong>{prompt.model_name}</strong>
                        </div>
                        <div className="prompt-detail-field">
                            <span className="label">{t('prompts.detail.category')}</span>
                            <span className="badge">{prompt.category}</span>
                        </div>
                        <div className="prompt-detail-field">
                            <span className="label">{t('prompts.detail.rating')}</span>
                            <span>{t('common.rating', { value: prompt.rate })}</span>
                        </div>
                    </div>
                    <div className="prompt-detail-field">
                        <span className="label">{t('prompts.detail.prompt')}</span>
                        <p className="prompt-detail-text">{prompt.prompt_text}</p>
                    </div>
                </div>
                <div className="dialog-actions">
                    <Button variant="ghost" onClick={onClose}>
                        {t('common.close')}
                    </Button>
                    <Button variant="ghost" onClick={handleEdit}>
                        {t('common.edit')}
                    </Button>
                    <Button variant="danger" onClick={handleDelete}>
                        {t('common.delete')}
                    </Button>
                </div>
            </div>
        </div>
    )
}
