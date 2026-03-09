import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { Card } from '../../components/ui/card'
import { InlineError } from '../../components/ui/inline-error'
import { PromptForm } from '../../components/prompts/prompt-form'
import { PromptList } from '../../components/prompts/prompt-list'
import { useAuth } from '../../features/auth/auth-store'
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
    const { session } = useAuth()
    const queryClient = useQueryClient()
    const [editingPrompt, setEditingPrompt] = useState<PromptRecord | null>(null)
    const [error, setError] = useState<string | null>(null)

    const token = session.token
    const userId = session.userId

    const promptsQuery = useQuery({
        queryKey: ['prompts', userId],
        queryFn: async () => {
            if (!token || !userId) {
                return []
            }
            return listPrompts(token, userId)
        },
        enabled: Boolean(token && userId),
    })

    const createMutation = useMutation({
        mutationFn: async (value: PromptInput) => {
            if (!token || !userId) {
                throw new Error('Session is not available')
            }
            return createPrompt(token, userId, value)
        },
        onSuccess: async () => {
            await queryClient.invalidateQueries({ queryKey: ['prompts', userId] })
            setError(null)
        },
        onError: (err) => {
            setError(err instanceof Error ? err.message : 'Unable to create prompt')
        },
    })

    const updateMutation = useMutation({
        mutationFn: async (value: PromptInput) => {
            if (!token || !userId || !editingPrompt) {
                throw new Error('Session or selected prompt is not available')
            }
            return updatePrompt(token, editingPrompt.id, userId, value)
        },
        onSuccess: async () => {
            await queryClient.invalidateQueries({ queryKey: ['prompts', userId] })
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
            await queryClient.invalidateQueries({ queryKey: ['prompts', userId] })
            setError(null)
        },
        onError: (err) => {
            setError(err instanceof Error ? err.message : 'Unable to delete prompt')
        },
    })

    const handleSubmit = async (value: PromptInput) => {
        if (editingPrompt) {
            await updateMutation.mutateAsync(value)
            return
        }

        await createMutation.mutateAsync(value)
    }

    const handleDelete = (prompt: PromptRecord) => {
        const confirmed = window.confirm('Delete this prompt?')
        if (!confirmed) {
            return
        }
        deleteMutation.mutate(prompt)
    }

    return (
        <section className="stack">
            <Card>
                <h1>{editingPrompt ? 'Edit prompt' : 'Create prompt'}</h1>
                <PromptForm
                    initialValue={editingPrompt}
                    isSaving={createMutation.isPending || updateMutation.isPending}
                    onSubmit={handleSubmit}
                    onCancelEdit={() => setEditingPrompt(null)}
                />
            </Card>

            <Card>
                <h2>Your prompts</h2>
                {promptsQuery.isLoading ? <p className="muted">Loading...</p> : null}
                {error ? <InlineError message={error} /> : null}
                {promptsQuery.data ? (
                    <PromptList
                        prompts={promptsQuery.data}
                        onEdit={setEditingPrompt}
                        onDelete={handleDelete}
                    />
                ) : null}
            </Card>
        </section>
    )
}

