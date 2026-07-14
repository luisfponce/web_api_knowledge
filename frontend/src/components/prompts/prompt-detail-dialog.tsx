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
                <h2 id="prompt-detail-title">Prompt details</h2>
                <div className="prompt-detail-body">
                    <div className="prompt-detail-field">
                        <span className="label">Model</span>
                        <p>{prompt.model_name}</p>
                    </div>
                    <div className="prompt-detail-field">
                        <span className="label">Prompt</span>
                        <p className="prompt-detail-text">{prompt.prompt_text}</p>
                    </div>
                    <div className="prompt-detail-meta">
                        <span className="badge">{prompt.category}</span>
                        <span className="muted">Rating {prompt.rate}/5</span>
                    </div>
                </div>
                <div className="dialog-actions">
                    <Button variant="ghost" onClick={onClose}>
                        Close
                    </Button>
                    <Button variant="ghost" onClick={handleEdit}>
                        Edit
                    </Button>
                    <Button variant="danger" onClick={handleDelete}>
                        Delete
                    </Button>
                </div>
            </div>
        </div>
    )
}
