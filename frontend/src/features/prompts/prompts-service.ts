import { ApiError } from '../../lib/http/api-error'
import { apiRequest } from '../../lib/http/api-client'
import type { PromptFilters, PromptInput, PromptRecord } from './prompts-types'

export async function listPrompts(
    token: string,
    userId?: number,
): Promise<PromptRecord[]> {
    const pageSize = 100
    const userPrompts: PromptRecord[] = []

    for (let skip = 0; ; skip += pageSize) {
        try {
            const prompts = await apiRequest<PromptRecord[]>(
                `/prompts?skip=${skip}&limit=${pageSize}`,
                {
                    method: 'GET',
                    token,
                },
            )

            userPrompts.push(
                ...prompts.filter((prompt) => userId === undefined || prompt.user_id === userId),
            )

            if (prompts.length < pageSize) {
                break
            }
        } catch (error) {
            if (error instanceof ApiError && error.status === 404) {
                break
            }
            throw error
        }
    }

    return userPrompts
}

export async function listAllPrompts(
    token: string,
    filters: PromptFilters = {},
): Promise<PromptRecord[]> {
    const pageSize = 100
    const allPrompts: PromptRecord[] = []

    for (let skip = 0; ; skip += pageSize) {
        const params = new URLSearchParams({
            skip: String(skip),
            limit: String(pageSize),
        })
        if (filters.user_id !== undefined) params.set('user_id', String(filters.user_id))
        if (filters.category) params.set('category', filters.category)
        if (filters.model_name) params.set('model_name', filters.model_name)
        if (filters.rate !== undefined) params.set('rate', String(filters.rate))

        try {
            const prompts = await apiRequest<PromptRecord[]>(`/prompts?${params}`, {
                method: 'GET',
                token,
            })
            allPrompts.push(...prompts)

            if (prompts.length < pageSize) {
                break
            }
        } catch (error) {
            if (error instanceof ApiError && error.status === 404) {
                break
            }
            throw error
        }
    }

    return allPrompts
}

export function createPrompt(
    token: string,
    userId: number | null,
    input: PromptInput,
): Promise<PromptRecord> {
    const payload =
        userId === null ? input : { ...input, user_id: userId }

    return apiRequest<PromptRecord>('/prompts', {
        method: 'POST',
        token,
        body: JSON.stringify(payload),
    })
}

export function updatePrompt(
    token: string,
    promptId: number,
    userId: number,
    input: PromptInput,
): Promise<PromptRecord> {
    return apiRequest<PromptRecord>(`/prompts/${promptId}`, {
        method: 'PUT',
        token,
        body: JSON.stringify({ ...input, user_id: userId }),
    })
}

export function deletePrompt(token: string, promptId: number): Promise<PromptRecord> {
    return apiRequest<PromptRecord>(`/prompts/${promptId}`, {
        method: 'DELETE',
        token,
    })
}
