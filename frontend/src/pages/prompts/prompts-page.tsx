import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { PromptEditorDrawer, type PromptEditorState } from '../../components/prompts/prompt-editor-drawer'
import { PromptList } from '../../components/prompts/prompt-list'
import { Button } from '../../components/ui/button'
import { Card } from '../../components/ui/card'
import { ConfirmDialog } from '../../components/ui/confirm-dialog'
import { InlineError } from '../../components/ui/inline-error'
import { PageHeader } from '../../components/ui/page-header'
import { useAuth } from '../../features/auth/auth-store'
import {
    listCategoryOptions,
    listModelOptions,
} from '../../features/options/options-service'
import {
    createPrompt,
    deletePrompt,
    listPrompts,
    updatePrompt,
} from '../../features/prompts/prompts-service'
import type {
    PromptInput,
    PromptRecord,
} from '../../features/prompts/prompts-types'

export function PromptsPage() {
    const { t } = useTranslation()
    const { session } = useAuth()
    const queryClient = useQueryClient()
    const [editorState, setEditorState] = useState<PromptEditorState>(null)
    const [promptToDelete, setPromptToDelete] = useState<PromptRecord | null>(null)
    const [error, setError] = useState<string | null>(null)

    const token = session.token
    const userId = session.userId

    const promptsQuery = useQuery({
        queryKey: ['prompts', userId],
        queryFn: async () => {
            if (!token || userId === null) {
                return []
            }
            return listPrompts(token, userId)
        },
        enabled: Boolean(token) && userId !== null,
    })

    const categoriesQuery = useQuery({
        queryKey: ['options', 'categories'],
        queryFn: async () => {
            if (!token) {
                return { items: [] }
            }
            return listCategoryOptions(token)
        },
        enabled: Boolean(token),
    })

    const modelsQuery = useQuery({
        queryKey: ['options', 'models'],
        queryFn: async () => {
            if (!token) {
                return { items: [] }
            }
            return listModelOptions(token)
        },
        enabled: Boolean(token),
    })

    const createMutation = useMutation({
        mutationFn: async (value: PromptInput) => {
            if (!token) {
                throw new Error(t('prompts.errors.sessionUnavailable'))
            }
            return createPrompt(token, userId, value)
        },
        onSuccess: async () => {
            await queryClient.invalidateQueries({ queryKey: ['prompts', userId] })
            setEditorState(null)
            setError(null)
        },
        onError: (err) => {
            setError(err instanceof Error ? err.message : t('prompts.errors.create'))
        },
    })

    const updateMutation = useMutation({
        mutationFn: async (value: PromptInput) => {
            if (!token || userId === null || editorState?.mode !== 'edit') {
                throw new Error(t('prompts.errors.selectedUnavailable'))
            }
            return updatePrompt(token, editorState.prompt.id, userId, value)
        },
        onSuccess: async () => {
            await queryClient.invalidateQueries({ queryKey: ['prompts', userId] })
            setEditorState(null)
            setError(null)
        },
        onError: (err) => {
            setError(err instanceof Error ? err.message : t('prompts.errors.update'))
        },
    })

    const deleteMutation = useMutation({
        mutationFn: async (prompt: PromptRecord) => {
            if (!token) {
                throw new Error(t('prompts.errors.sessionUnavailable'))
            }
            return deletePrompt(token, prompt.id)
        },
        onSuccess: async () => {
            await queryClient.invalidateQueries({ queryKey: ['prompts', userId] })
            setError(null)
        },
        onError: (err) => {
            setError(err instanceof Error ? err.message : t('prompts.errors.delete'))
        },
    })

    const handleSubmit = async (value: PromptInput) => {
        if (editorState?.mode === 'edit') {
            await updateMutation.mutateAsync(value)
            return
        }

        await createMutation.mutateAsync(value)
    }

    const handleDelete = () => {
        if (!promptToDelete) return
        deleteMutation.mutate(promptToDelete, {
            onSuccess: () => setPromptToDelete(null),
        })
    }

    const openCreateDrawer = () => {
        setError(null)
        setEditorState({ mode: 'create' })
    }

    const openEditDrawer = (prompt: PromptRecord) => {
        setError(null)
        setEditorState({ mode: 'edit', prompt })
    }

    const closeEditorDrawer = () => {
        setEditorState(null)
    }

    const prompts = promptsQuery.data ?? []
    const averageRating = prompts.length
        ? prompts.reduce((total, prompt) => total + prompt.rate, 0) / prompts.length
        : 0
    const categoryCount = new Set(prompts.map((prompt) => prompt.category)).size
    const optionErrorMessage = categoriesQuery.error || modelsQuery.error ? t('prompts.dropdownError') : null
    const drawerErrorMessage = error ?? optionErrorMessage

    return (
        <section className="stack">
            <PageHeader
                eyebrow={t('prompts.eyebrow')}
                title={t('prompts.title')}
                description={t('prompts.description')}
                actions={(
                    <Button type="button" onClick={openCreateDrawer}>
                        {t('prompts.newPrompt')}
                    </Button>
                )}
            />

            <div className="stats-grid">
                <Card className="stat-card">
                    <span className="label">{t('prompts.stats.total')}</span>
                    <strong>{prompts.length}</strong>
                </Card>
                <Card className="stat-card">
                    <span className="label">{t('prompts.stats.averageRating')}</span>
                    <strong>{prompts.length ? t('common.rating', { value: averageRating.toFixed(1) }) : t('prompts.stats.emptyRating')}</strong>
                </Card>
                <Card className="stat-card">
                    <span className="label">{t('prompts.stats.categories')}</span>
                    <strong>{categoryCount}</strong>
                </Card>
            </div>

            <Card className="library-card">
                <div className="section-heading">
                    <div>
                        <h2>{t('prompts.listTitle')}</h2>
                        <p className="muted">{t('prompts.listDescription')}</p>
                    </div>
                </div>
                {promptsQuery.isLoading ? <p className="muted">{t('common.loading')}</p> : null}
                {error && !editorState ? <InlineError message={error} /> : null}
                {optionErrorMessage && !editorState ? <InlineError message={optionErrorMessage} /> : null}
                {promptsQuery.data ? (
                    <PromptList
                        prompts={prompts}
                        onEdit={openEditDrawer}
                        onDelete={setPromptToDelete}
                    />
                ) : null}
            </Card>
            <PromptEditorDrawer
                state={editorState}
                isSaving={createMutation.isPending || updateMutation.isPending}
                errorMessage={drawerErrorMessage}
                modelOptions={modelsQuery.data?.items ?? []}
                categoryOptions={categoriesQuery.data?.items ?? []}
                optionsLoading={categoriesQuery.isLoading || modelsQuery.isLoading}
                onSubmit={handleSubmit}
                onClose={closeEditorDrawer}
            />
            <ConfirmDialog
                open={Boolean(promptToDelete)}
                title={t('prompts.deleteTitle')}
                description={t('prompts.deleteDescription')}
                confirmLabel={t('prompts.deleteConfirm')}
                cancelLabel={t('common.cancel')}
                busy={deleteMutation.isPending}
                onCancel={() => setPromptToDelete(null)}
                onConfirm={handleDelete}
            />
        </section>
    )
}
