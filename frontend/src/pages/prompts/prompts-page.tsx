import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useMemo, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { PromptEditorDrawer, type PromptEditorState } from '../../components/prompts/prompt-editor-drawer'
import { PromptList } from '../../components/prompts/prompt-list'
import { Button } from '../../components/ui/button'
import { Card } from '../../components/ui/card'
import { ConfirmDialog } from '../../components/ui/confirm-dialog'
import { Input } from '../../components/ui/input'
import { InlineError } from '../../components/ui/inline-error'
import { PageHeader } from '../../components/ui/page-header'
import { Select } from '../../components/ui/select'
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
import {
    applyPromptCatalogControls,
    defaultPromptCatalogControls,
    hasActivePromptCatalogControls,
    type PromptCatalogSort,
} from '../../features/prompts/prompt-catalog-utils'
import type {
    PromptInput,
    PromptRecord,
} from '../../features/prompts/prompts-types'
import { useDocumentTitle } from '../../lib/hooks/use-document-title'

const ratingOptions = [1, 2, 3, 4, 5].map((rating) => ({
    value: String(rating),
    label: `${rating}/5`,
}))

const emptyPrompts: PromptRecord[] = []

export function PromptsPage() {
    const { t } = useTranslation()
    useDocumentTitle(t('titles.promptLibrary'))
    const { session } = useAuth()
    const queryClient = useQueryClient()
    const [editorState, setEditorState] = useState<PromptEditorState>(null)
    const [promptToDelete, setPromptToDelete] = useState<PromptRecord | null>(null)
    const [catalogControls, setCatalogControls] = useState(defaultPromptCatalogControls)
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

    const prompts = promptsQuery.data ?? emptyPrompts
    const visiblePrompts = useMemo(
        () => applyPromptCatalogControls(prompts, catalogControls),
        [catalogControls, prompts],
    )
    const hasActiveControls = hasActivePromptCatalogControls(catalogControls)
    const averageRating = visiblePrompts.length
        ? visiblePrompts.reduce((total, prompt) => total + prompt.rate, 0) / visiblePrompts.length
        : 0
    const categoryCount = new Set(visiblePrompts.map((prompt) => prompt.category)).size
    const optionErrorMessage = categoriesQuery.error || modelsQuery.error ? t('prompts.dropdownError') : null
    const drawerErrorMessage = error ?? optionErrorMessage
    const sortOptions = [
        { value: 'newest', label: t('prompts.sort.newest') },
        { value: 'title', label: t('prompts.sort.title') },
        { value: 'rating', label: t('prompts.sort.rating') },
        { value: 'model', label: t('prompts.sort.model') },
        { value: 'category', label: t('prompts.sort.category') },
    ]

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
                    <strong>{visiblePrompts.length}</strong>
                </Card>
                <Card className="stat-card">
                    <span className="label">{t('prompts.stats.averageRating')}</span>
                    <strong>{visiblePrompts.length ? t('common.rating', { value: averageRating.toFixed(1) }) : t('prompts.stats.emptyRating')}</strong>
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
                <div className="catalog-controls">
                    <Input
                        id="prompt-search"
                        label={t('prompts.filters.search')}
                        placeholder={t('prompts.filters.searchPlaceholder')}
                        value={catalogControls.search}
                        onChange={(event) => setCatalogControls((current) => ({ ...current, search: event.target.value }))}
                    />
                    <Select
                        id="prompt-model-filter"
                        label={t('prompts.filters.model')}
                        options={modelsQuery.data?.items ?? []}
                        placeholder={t('common.selectOption')}
                        value={catalogControls.model}
                        onChange={(event) => setCatalogControls((current) => ({ ...current, model: event.target.value }))}
                    />
                    <Select
                        id="prompt-category-filter"
                        label={t('prompts.filters.category')}
                        options={categoriesQuery.data?.items ?? []}
                        placeholder={t('common.selectOption')}
                        value={catalogControls.category}
                        onChange={(event) => setCatalogControls((current) => ({ ...current, category: event.target.value }))}
                    />
                    <Select
                        id="prompt-rating-filter"
                        label={t('prompts.filters.rating')}
                        options={ratingOptions}
                        placeholder={t('common.selectOption')}
                        value={catalogControls.rating}
                        onChange={(event) => setCatalogControls((current) => ({ ...current, rating: event.target.value }))}
                    />
                    <Select
                        id="prompt-sort"
                        label={t('prompts.filters.sort')}
                        options={sortOptions}
                        placeholder={t('common.selectOption')}
                        value={catalogControls.sort}
                        onChange={(event) => setCatalogControls((current) => ({
                            ...current,
                            sort: (event.target.value || defaultPromptCatalogControls.sort) as PromptCatalogSort,
                        }))}
                    />
                    <Button
                        type="button"
                        variant="ghost"
                        className="catalog-clear-button"
                        disabled={!hasActiveControls}
                        onClick={() => setCatalogControls(defaultPromptCatalogControls)}
                    >
                        {t('prompts.filters.clear')}
                    </Button>
                </div>
                <p className="muted">
                    {hasActiveControls
                        ? t('prompts.filters.visibleCount', { visible: visiblePrompts.length, total: prompts.length })
                        : t('prompts.filters.allVisible', { count: prompts.length })}
                </p>
                {promptsQuery.isLoading ? <p className="muted">{t('common.loading')}</p> : null}
                {error && !editorState ? <InlineError message={error} /> : null}
                {optionErrorMessage && !editorState ? <InlineError message={optionErrorMessage} /> : null}
                {promptsQuery.data ? (
                    <PromptList
                        prompts={visiblePrompts}
                        onEdit={openEditDrawer}
                        onDelete={setPromptToDelete}
                        emptyTitle={hasActiveControls ? t('prompts.noResultsTitle') : undefined}
                        emptyDescription={hasActiveControls ? t('prompts.noResultsDescription') : undefined}
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
