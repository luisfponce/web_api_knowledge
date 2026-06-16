import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { PromptForm } from '../../components/prompts/prompt-form'
import { Button } from '../../components/ui/button'
import { Card } from '../../components/ui/card'
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

const ratingOptions = [1, 2, 3, 4, 5].map((rating) => ({
    value: String(rating),
    label: `${rating}/5`,
}))

export function AdminPromptsPage() {
    const { session } = useAuth()
    const queryClient = useQueryClient()
    const [filters, setFilters] = useState<PromptFilters>({})
    const [userFilter, setUserFilter] = useState('')
    const [editingPrompt, setEditingPrompt] = useState<PromptRecord | null>(null)
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
                throw new Error('Session or selected prompt is not available')
            }
            return updatePrompt(token, editingPrompt.id, editingPrompt.user_id, value)
        },
        onSuccess: async () => {
            await queryClient.invalidateQueries({ queryKey: ['admin-prompts'] })
            setEditingPrompt(null)
            setError(null)
        },
        onError: (err) => {
            setError(err instanceof Error ? err.message : 'Unable to update prompt')
        },
    })

    const deleteMutation = useMutation({
        mutationFn: async (prompt: PromptRecord) => {
            if (!token) {
                throw new Error('Session is not available')
            }
            return deletePrompt(token, prompt.id)
        },
        onSuccess: async () => {
            await queryClient.invalidateQueries({ queryKey: ['admin-prompts'] })
            setError(null)
        },
        onError: (err) => {
            setError(err instanceof Error ? err.message : 'Unable to delete prompt')
        },
    })

    const applyUserFilter = () => {
        const trimmed = userFilter.trim()
        setFilters((prev) => ({
            ...prev,
            user_id: trimmed && Number.isFinite(Number(trimmed)) ? Number(trimmed) : undefined,
        }))
    }

    const handleDelete = (prompt: PromptRecord) => {
        const confirmed = window.confirm('Delete this prompt?')
        if (!confirmed) return
        deleteMutation.mutate(prompt)
    }

    return (
        <section className="stack">
            <Card className="stack">
                <div className="section-heading">
                    <div>
                        <h1>Admin Monitor</h1>
                        <p className="muted">
                            {promptsQuery.data?.length ?? 0} prompts visible to {session.role}.
                        </p>
                    </div>
                    <span className="badge">{session.role}</span>
                </div>

                <div className="filter-grid">
                    <Input
                        label="User ID"
                        type="number"
                        min="1"
                        value={userFilter}
                        onChange={(event) => setUserFilter(event.target.value)}
                        onBlur={applyUserFilter}
                    />
                    <Select
                        label="Model"
                        options={modelsQuery.data?.items ?? []}
                        value={filters.model_name ?? ''}
                        onChange={(event) =>
                            setFilters((prev) => ({
                                ...prev,
                                model_name: event.target.value || undefined,
                            }))
                        }
                    />
                    <Select
                        label="Category"
                        options={categoriesQuery.data?.items ?? []}
                        value={filters.category ?? ''}
                        onChange={(event) =>
                            setFilters((prev) => ({
                                ...prev,
                                category: event.target.value || undefined,
                            }))
                        }
                    />
                    <Select
                        label="Rating"
                        options={ratingOptions}
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
                    Clear filters
                </Button>
            </Card>

            {editingPrompt && isGod ? (
                <Card>
                    <h2>Edit prompt as god</h2>
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
                <h2>All prompts</h2>
                {promptsQuery.isLoading ? <p className="muted">Loading...</p> : null}
                {error || promptsQuery.error ? (
                    <InlineError
                        message={
                            error ??
                            (promptsQuery.error instanceof Error
                                ? promptsQuery.error.message
                                : 'Unable to load prompts')
                        }
                    />
                ) : null}
                <div className="list">
                    {(promptsQuery.data ?? []).map((prompt) => (
                        <article key={prompt.id} className="list-item">
                            <div>
                                <h3>{prompt.model_name}</h3>
                                <p>{prompt.prompt_text}</p>
                                <p className="muted">
                                    User {prompt.user_id} · {prompt.category} · Rating {prompt.rate}/5
                                </p>
                            </div>
                            {isGod ? (
                                <div className="row gap-sm">
                                    <Button variant="ghost" onClick={() => setEditingPrompt(prompt)}>
                                        Edit
                                    </Button>
                                    <Button variant="danger" onClick={() => handleDelete(prompt)}>
                                        Delete
                                    </Button>
                                </div>
                            ) : null}
                        </article>
                    ))}
                </div>
                {promptsQuery.data?.length === 0 ? <p className="muted">No prompts found.</p> : null}
            </Card>
        </section>
    )
}
