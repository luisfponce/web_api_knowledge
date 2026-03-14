import type { PromptRecord } from '../../features/prompts/prompts-types'
import { Button } from '../ui/button'

type PromptListProps = {
    prompts: PromptRecord[]
    onEdit: (prompt: PromptRecord) => void
    onDelete: (prompt: PromptRecord) => void
}

export function PromptList({ prompts, onEdit, onDelete }: PromptListProps) {
    if (!prompts.length) {
        return <p className="muted">No prompts yet.</p>
    }

    return (
        <div className="list">
            {prompts.map((prompt) => (
                <article key={prompt.id} className="list-item">
                    <div>
                        <h3>{prompt.model_name}</h3>
                        <p>{prompt.prompt_text}</p>
                        <p className="muted">
                            {prompt.category} · Rate {prompt.rate}
                        </p>
                    </div>
                    <div className="row gap-sm">
                        <Button variant="ghost" onClick={() => onEdit(prompt)}>
                            Edit
                        </Button>
                        <Button variant="danger" onClick={() => onDelete(prompt)}>
                            Delete
                        </Button>
                    </div>
                </article>
            ))}
        </div>
    )
}

