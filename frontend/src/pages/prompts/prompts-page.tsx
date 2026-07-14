import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Card } from '../../components/ui/card'
import { ConfirmDialog } from '../../components/ui/confirm-dialog'
import { InlineError } from '../../components/ui/inline-error'
import { PageHeader } from '../../components/ui/page-header'
import { PromptForm } from '../../components/prompts/prompt-form'
import { PromptList } from '../../components/prompts/prompt-list'
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
    const [editingPrompt, setEditingPrompt] = useState<PromptRecord | null>(null)
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
            setError(null)
        },
        onError: (err) => {
            setError(err instanceof Error ? err.message : t('prompts.errors.create'))
        },
    })

    const updateMutation = useMutation({
        mutationFn: async (value: PromptInput) => {
            if (!token || userId === null || !editingPrompt) {
                throw new Error(t('prompts.errors.selectedUnavailable'))
            }
            return updatePrompt(token, editingPrompt.id, userId, value)
        },
        onSuccess: async () => {
            await queryClient.invalidateQueries({ queryKey: ['prompts', userId] })
            setEditingPrompt(null)
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
        if (editingPrompt) {
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

    return (
        <section className="stack">
            <PageHeader
                eyebrow={t('prompts.eyebrow')}
                title={t('prompts.title')}
                description={t('prompts.description')}
            />
            <Card>
                <h1>{editingPrompt ? t('prompts.edit') : t('prompts.create')}</h1>
                <PromptForm
                    key={editingPrompt?.id ?? 'new-prompt'}
                    initialValue={editingPrompt}
                    isSaving={createMutation.isPending || updateMutation.isPending}
                    modelOptions={modelsQuery.data?.items ?? []}
                    categoryOptions={categoriesQuery.data?.items ?? []}
                    optionsLoading={categoriesQuery.isLoading || modelsQuery.isLoading}
                    onSubmit={handleSubmit}
                    onCancelEdit={() => setEditingPrompt(null)}
                />
                {categoriesQuery.error || modelsQuery.error ? (
                    <InlineError message={t('prompts.dropdownError')} />
                ) : null}
            </Card>

            <Card>
                <h2>{t('prompts.listTitle')}</h2>
                {promptsQuery.isLoading ? <p className="muted">{t('common.loading')}</p> : null}
                {error ? <InlineError message={error} /> : null}
                {promptsQuery.data ? (
                    <PromptList
                        prompts={promptsQuery.data}
                        onEdit={setEditingPrompt}
                        onDelete={setPromptToDelete}
                    />
                ) : null}
            </Card>
            <ConfirmDialog
                open={Boolean(promptToDelete)}
                title={t('prompts.deleteTitle')}
                description={t('prompts.deleteDescription')}
                confirmLabel={t('prompts.deleteConfirm')}
                busy={deleteMutation.isPending}
                onCancel={() => setPromptToDelete(null)}
                onConfirm={handleDelete}
            />
        </section>
    )
}
