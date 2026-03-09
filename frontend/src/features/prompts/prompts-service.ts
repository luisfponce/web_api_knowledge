import { ApiError } from '../../lib/http/api-error'
import { apiRequest } from '../../lib/http/api-client'
import type { PromptInput, PromptRecord } from './prompts-types'

export async function listPrompts(
    token: string,
    userId: number,
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

            userPrompts.push(...prompts.filter((prompt) => prompt.user_id === userId))

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

export function createPrompt(
    token: string,
    userId: number,
    input: PromptInput,
): Promise<PromptRecord> {
    return apiRequest<PromptRecord>('/prompts', {
        method: 'POST',
        token,
        body: JSON.stringify({ ...input, user_id: userId }),
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
