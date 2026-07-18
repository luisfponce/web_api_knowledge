import { useTranslation } from 'react-i18next'
import type { SelectOption } from '../../features/options/options-types'
import type { PromptInput, PromptRecord } from '../../features/prompts/prompts-types'
import { Button } from '../ui/button'
import { InlineError } from '../ui/inline-error'
import { PromptForm } from './prompt-form'

export type PromptEditorState =
    | { mode: 'create' }
    | { mode: 'edit'; prompt: PromptRecord }
    | null

type PromptEditorDrawerProps = {
    state: PromptEditorState
    isSaving: boolean
    errorMessage?: string | null
    modelOptions: SelectOption[]
    categoryOptions: SelectOption[]
    optionsLoading: boolean
    onSubmit: (value: PromptInput) => Promise<void>
    onClose: () => void
}

export function PromptEditorDrawer({
    state,
    isSaving,
    errorMessage,
    modelOptions,
    categoryOptions,
    optionsLoading,
    onSubmit,
    onClose,
}: PromptEditorDrawerProps) {
    const { t } = useTranslation()

    if (!state) return null

    const isEdit = state.mode === 'edit'
    const title = isEdit ? t('prompts.edit') : t('prompts.create')

    return (
        <div className="drawer-backdrop" role="presentation" onMouseDown={onClose}>
            <aside
                className="drawer-panel"
                role="dialog"
                aria-modal="true"
                aria-labelledby="prompt-editor-title"
                onMouseDown={(event) => event.stopPropagation()}
            >
                <div className="drawer-header">
                    <div>
                        <p className="eyebrow">{t('prompts.eyebrow')}</p>
                        <h2 id="prompt-editor-title">{title}</h2>
                    </div>
                    <Button type="button" variant="ghost" onClick={onClose}>
                        {t('common.close')}
                    </Button>
                </div>

                <div className="drawer-body">
                    {errorMessage ? <InlineError message={errorMessage} /> : null}
                    <PromptForm
                        key={isEdit ? state.prompt.id : 'create-prompt'}
                        initialValue={isEdit ? state.prompt : null}
                        isSaving={isSaving}
                        modelOptions={modelOptions}
                        categoryOptions={categoryOptions}
                        optionsLoading={optionsLoading}
                        showCancel
                        onSubmit={onSubmit}
                        onCancelEdit={onClose}
                    />
                </div>
            </aside>
        </div>
    )
}
