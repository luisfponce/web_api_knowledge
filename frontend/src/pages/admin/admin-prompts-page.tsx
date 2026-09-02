import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { PromptForm } from '../../components/prompts/prompt-form'
import { Button } from '../../components/ui/button'
import { Card } from '../../components/ui/card'
import { ConfirmDialog } from '../../components/ui/confirm-dialog'
import { InlineError } from '../../components/ui/inline-error'
import { Input } from '../../components/ui/input'
import { Select } from '../../components/ui/select'
import { useAuth } from '../../features/auth/auth-store'
import {
    listCategoryOptions,
    listModelOptions,
} from '../../features/options/options-service'
import {
    deletePrompt,
    listAllPrompts,
    updatePrompt,
} from '../../features/prompts/prompts-service'
import type {
    PromptFilters,
    PromptInput,
    PromptRecord,
} from '../../features/prompts/prompts-types'
import { useDocumentTitle } from '../../lib/hooks/use-document-title'

const ratingOptions = [1, 2, 3, 4, 5].map((rating) => ({
    value: String(rating),
    label: `${rating}/5`,
}))

export function AdminPromptsPage() {
    const { t } = useTranslation()
    useDocumentTitle(t('titles.admin'))
    const { session } = useAuth()
    const queryClient = useQueryClient()
    const [filters, setFilters] = useState<PromptFilters>({})
    const [userFilter, setUserFilter] = useState('')
    const [editingPrompt, setEditingPrompt] = useState<PromptRecord | null>(null)
    const [promptToDelete, setPromptToDelete] = useState<PromptRecord | null>(null)
    const [error, setError] = useState<string | null>(null)

    const token = session.token
    const isGod = session.role === 'god'

    const promptsQuery = useQuery({
        queryKey: ['admin-prompts', filters],
        queryFn: async () => {
            if (!token) {
                return []
            }
            return listAllPrompts(token, filters)
        },
        enabled: Boolean(token),
    })

    const categoriesQuery = useQuery({
        queryKey: ['options', 'categories'],
        queryFn: async () => {
            if (!token) return { items: [] }
            return listCategoryOptions(token)
        },
        enabled: Boolean(token),
    })

    const modelsQuery = useQuery({
        queryKey: ['options', 'models'],
        queryFn: async () => {
            if (!token) return { items: [] }
            return listModelOptions(token)
        },
        enabled: Boolean(token),
    })

    const updateMutation = useMutation({
        mutationFn: async (value: PromptInput) => {
            if (!token || !editingPrompt) {
                throw new Error(t('admin.errors.selectedUnavailable'))
            }
            return updatePrompt(token, editingPrompt.id, editingPrompt.user_id, value)
        },
        onSuccess: async () => {
            await queryClient.invalidateQueries({ queryKey: ['admin-prompts'] })
            setEditingPrompt(null)
            setError(null)
        },
        onError: (err) => {
            setError(err instanceof Error ? err.message : t('admin.errors.update'))
        },
    })

    const deleteMutation = useMutation({
        mutationFn: async (prompt: PromptRecord) => {
            if (!token) {
                throw new Error(t('admin.errors.sessionUnavailable'))
            }
            return deletePrompt(token, prompt.id)
        },
        onSuccess: async () => {
            await queryClient.invalidateQueries({ queryKey: ['admin-prompts'] })
            setError(null)
        },
        onError: (err) => {
            setError(err instanceof Error ? err.message : t('admin.errors.delete'))
        },
    })

    const applyUserFilter = () => {
        const trimmed = userFilter.trim()
        setFilters((prev) => ({
            ...prev,
            user_id: trimmed && Number.isFinite(Number(trimmed)) ? Number(trimmed) : undefined,
        }))
    }

    const handleDelete = () => {
        if (!promptToDelete) return
        deleteMutation.mutate(promptToDelete, {
            onSuccess: () => setPromptToDelete(null),
        })
    }

    return (
        <section className="stack">
            <Card className="stack">
                <div className="section-heading">
                    <div>
                        <h1>{t('admin.title')}</h1>
                        <p className="muted">
                            {t('admin.visibleCount', { count: promptsQuery.data?.length ?? 0, role: session.role })}
                        </p>
                    </div>
                    <span className="badge">{session.role}</span>
                </div>

                <div className="filter-grid">
                    <Input
                        label={t('admin.filters.userId')}
                        type="number"
                        min="1"
                        value={userFilter}
                        onChange={(event) => setUserFilter(event.target.value)}
                        onBlur={applyUserFilter}
                    />
                    <Select
                        label={t('admin.filters.model')}
                        options={modelsQuery.data?.items ?? []}
                        placeholder={t('common.selectOption')}
                        value={filters.model_name ?? ''}
                        onChange={(event) =>
                            setFilters((prev) => ({
                                ...prev,
                                model_name: event.target.value || undefined,
                            }))
                        }
                    />
                    <Select
                        label={t('admin.filters.category')}
                        options={categoriesQuery.data?.items ?? []}
                        placeholder={t('common.selectOption')}
                        value={filters.category ?? ''}
                        onChange={(event) =>
                            setFilters((prev) => ({
                                ...prev,
                                category: event.target.value || undefined,
                            }))
                        }
                    />
                    <Select
                        label={t('admin.filters.rating')}
                        options={ratingOptions}
                        placeholder={t('common.selectOption')}
                        value={filters.rate ? String(filters.rate) : ''}
                        onChange={(event) =>
                            setFilters((prev) => ({
                                ...prev,
                                rate: event.target.value ? Number(event.target.value) : undefined,
                            }))
                        }
                    />
                </div>
                <Button
                    type="button"
                    variant="ghost"
                    onClick={() => {
                        setFilters({})
                        setUserFilter('')
                    }}
                >
                    {t('admin.filters.clear')}
                </Button>
            </Card>

            {editingPrompt && isGod ? (
                <Card>
                    <h2>{t('admin.editTitle')}</h2>
                    <PromptForm
                        key={editingPrompt.id}
                        initialValue={editingPrompt}
                        isSaving={updateMutation.isPending}
                        modelOptions={modelsQuery.data?.items ?? []}
                        categoryOptions={categoriesQuery.data?.items ?? []}
                        optionsLoading={categoriesQuery.isLoading || modelsQuery.isLoading}
                        onSubmit={async (value) => {
                            await updateMutation.mutateAsync(value)
                        }}
                        onCancelEdit={() => setEditingPrompt(null)}
                    />
                </Card>
            ) : null}

            <Card>
                <h2>{t('admin.allPrompts')}</h2>
                {promptsQuery.isLoading ? <p className="muted">{t('common.loading')}</p> : null}
                {error || promptsQuery.error ? (
                    <InlineError
                        message={
                            error ??
                            (promptsQuery.error instanceof Error
                                ? promptsQuery.error.message
                                : t('admin.unableToLoad'))
                        }
                    />
                ) : null}
                <div className="list">
                    {(promptsQuery.data ?? []).map((prompt) => (
                        <article key={prompt.id} className="list-item">
                            <div>
                                <h3>{prompt.title}</h3>
                                <p>{prompt.prompt_text}</p>
                                <p className="muted">
                                    {t('admin.promptMeta', { userId: prompt.user_id, model: prompt.model_name, category: prompt.category, rating: prompt.rate })}
                                </p>
                            </div>
                            {isGod ? (
                                <div className="row gap-sm">
                                    <Button variant="ghost" onClick={() => setEditingPrompt(prompt)}>
                                        {t('common.edit')}
                                    </Button>
                                    <Button variant="danger" onClick={() => setPromptToDelete(prompt)}>
                                        {t('common.delete')}
                                    </Button>
                                </div>
                            ) : null}
                        </article>
                    ))}
                </div>
                {promptsQuery.data?.length === 0 ? <p className="muted">{t('admin.noPrompts')}</p> : null}
            </Card>
            <ConfirmDialog
                open={Boolean(promptToDelete)}
                title={t('admin.deleteTitle')}
                description={t('admin.deleteDescription')}
                confirmLabel={t('admin.deleteConfirm')}
                cancelLabel={t('common.cancel')}
                busy={deleteMutation.isPending}
                onCancel={() => setPromptToDelete(null)}
                onConfirm={handleDelete}
            />
        </section>
    )
}
