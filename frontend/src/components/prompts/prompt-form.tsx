import { useState, type FormEvent } from 'react'
import { useTranslation } from 'react-i18next'
import type { SelectOption } from '../../features/options/options-types'
import type { PromptInput, PromptRecord } from '../../features/prompts/prompts-types'
import { promptSchema } from '../../lib/validation/prompt-schemas'
import { Button } from '../ui/button'
import { ComboboxInput } from '../ui/combobox-input'
import { RatingInput } from '../ui/rating-input'
import { Select } from '../ui/select'
import { Textarea } from '../ui/textarea'

type PromptFormProps = {
    initialValue?: PromptRecord | null
    isSaving: boolean
    modelOptions: SelectOption[]
    categoryOptions: SelectOption[]
    optionsLoading: boolean
    onSubmit: (value: PromptInput) => Promise<void>
    onCancelEdit: () => void
}

type FieldErrors = Partial<Record<keyof PromptInput, string>>

export function PromptForm({
    initialValue,
    isSaving,
    modelOptions,
    categoryOptions,
    optionsLoading,
    onSubmit,
    onCancelEdit,
}: PromptFormProps) {
    const { t } = useTranslation()
    const [form, setForm] = useState<PromptInput>({
        model_name: initialValue?.model_name ?? '',
        prompt_text: initialValue?.prompt_text ?? '',
        category: initialValue?.category ?? '',
        rate: initialValue?.rate ?? 3,
    })
    const [error, setError] = useState<string | null>(null)
    const [fieldErrors, setFieldErrors] = useState<FieldErrors>({})

    const isEdit = Boolean(initialValue)

    const handleChange = (field: keyof PromptInput, value: string | number) => {
        setForm((prev) => ({ ...prev, [field]: value }))
    }

    const handleSubmit = async (event: FormEvent) => {
        event.preventDefault()
        const parsed = promptSchema.safeParse(form)
        if (!parsed.success) {
            const nextErrors: FieldErrors = {}
            for (const issue of parsed.error.issues) {
                const field = issue.path[0] as keyof PromptInput | undefined
                if (field) {
                    nextErrors[field] = issue.message
                }
            }
            setFieldErrors(nextErrors)
            setError(parsed.error.issues[0]?.message ?? t('prompts.form.invalid'))
            return
        }

        const selectedModel = modelOptions.find((option) => option.value === parsed.data.model_name)
        if (!selectedModel) {
            const message = t('prompts.form.knownModel')
            setFieldErrors({ model_name: message })
            setError(message)
            return
        }

        setError(null)
        setFieldErrors({})
        await onSubmit(parsed.data)
        if (!isEdit) {
            setForm({ model_name: '', prompt_text: '', category: '', rate: 3 })
        }
    }

    return (
        <form className="prompt-form" onSubmit={handleSubmit}>
            <ComboboxInput
                label={t('prompts.form.model')}
                options={modelOptions}
                value={form.model_name}
                disabled={optionsLoading || isSaving}
                onChange={(value) => handleChange('model_name', value)}
                error={fieldErrors.model_name}
            />
            <Textarea
                label={t('prompts.form.prompt')}
                value={form.prompt_text}
                onChange={(e) => handleChange('prompt_text', e.target.value)}
                error={fieldErrors.prompt_text}
                placeholder={t('prompts.form.promptPlaceholder')}
                rows={7}
            />
            <Select
                label={t('prompts.form.category')}
                options={categoryOptions}
                value={form.category}
                placeholder={t('common.selectOption')}
                disabled={optionsLoading || isSaving}
                onChange={(e) => handleChange('category', e.target.value)}
                error={fieldErrors.category}
            />
            <RatingInput
                label={t('prompts.form.rating')}
                value={form.rate}
                onChange={(value) => handleChange('rate', value)}
                disabled={isSaving}
                error={fieldErrors.rate}
            />

            {error ? <p className="field-error">{error}</p> : null}

            <div className="row gap-sm">
                <Button type="submit" disabled={optionsLoading || isSaving}>
                    {isSaving ? t('common.saving') : isEdit ? t('prompts.form.update') : t('prompts.form.add')}
                </Button>
                {isEdit ? (
                    <Button type="button" variant="ghost" onClick={onCancelEdit}>
                        {t('common.cancel')}
                    </Button>
                ) : null}
            </div>
        </form>
    )
}
