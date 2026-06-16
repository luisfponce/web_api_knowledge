import { apiRequest } from '../../lib/http/api-client'
import type { OptionsResponse } from './options-types'

export function listCategoryOptions(token: string): Promise<OptionsResponse> {
    return apiRequest<OptionsResponse>('/options/categories', {
        method: 'GET',
        token,
    })
}

export function listModelOptions(token: string): Promise<OptionsResponse> {
    return apiRequest<OptionsResponse>('/options/models', {
        method: 'GET',
        token,
    })
}
