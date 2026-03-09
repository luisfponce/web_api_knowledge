import { useState, type FormEvent } from 'react'
import type { PromptInput, PromptRecord } from '../../features/prompts/prompts-types'
import { promptSchema } from '../../lib/validation/prompt-schemas'
import { Button } from '../ui/button'
import { Input } from '../ui/input'

type PromptFormProps = {
    initialValue?: PromptRecord | null
    isSaving: boolean
    onSubmit: (value: PromptInput) => Promise<void>
    onCancelEdit: () => void
}

export function PromptForm({
    initialValue,
    isSaving,
    onSubmit,
    onCancelEdit,
}: PromptFormProps) {
    const [form, setForm] = useState<PromptInput>({
        model_name: initialValue?.model_name ?? '',
        prompt_text: initialValue?.prompt_text ?? '',
        category: initialValue?.category ?? '',
        rate: initialValue?.rate ?? '',
    })
    const [error, setError] = useState<string | null>(null)

    const isEdit = Boolean(initialValue)

    const handleChange = (field: keyof PromptInput, value: string) => {
        setForm((prev) => ({ ...prev, [field]: value }))
    }

    const handleSubmit = async (event: FormEvent) => {
        event.preventDefault()
        const parsed = promptSchema.safeParse(form)
        if (!parsed.success) {
            setError(parsed.error.issues[0]?.message ?? 'Invalid form data')
            return
        }

        setError(null)
        await onSubmit(parsed.data)
        if (!isEdit) {
            setForm({ model_name: '', prompt_text: '', category: '', rate: '' })
        }
    }

    return (
        <form className="prompt-form" onSubmit={handleSubmit}>
            <Input
                label="Model"
                value={form.model_name}
                onChange={(e) => handleChange('model_name', e.target.value)}
            />
            <Input
                label="Prompt"
                value={form.prompt_text}
                onChange={(e) => handleChange('prompt_text', e.target.value)}
            />
            <Input
                label="Category"
                value={form.category}
                onChange={(e) => handleChange('category', e.target.value)}
            />
            <Input
                label="Rate"
                value={form.rate}
                onChange={(e) => handleChange('rate', e.target.value)}
            />

            {error ? <p className="field-error">{error}</p> : null}

            <div className="row gap-sm">
                <Button type="submit" disabled={isSaving}>
                    {isSaving ? 'Saving...' : isEdit ? 'Update prompt' : 'Add prompt'}
                </Button>
                {isEdit ? (
                    <Button type="button" variant="ghost" onClick={onCancelEdit}>
                        Cancel
                    </Button>
                ) : null}
            </div>
        </form>
    )
}
