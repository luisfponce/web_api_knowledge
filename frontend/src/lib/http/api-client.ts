import { ApiError } from './api-error'

const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL?.trim() || '/api/v1'

type RequestOptions = RequestInit & {
    token?: string | null
}

export async function apiRequest<T>(
    path: string,
    options: RequestOptions = {},
): Promise<T> {
    const headers = new Headers(options.headers)

    if (!headers.has('Content-Type') && options.body) {
        headers.set('Content-Type', 'application/json')
    }

    if (options.token) {
        headers.set('Authorization', `Bearer ${options.token}`)
    }

    const response = await fetch(`${API_BASE_URL}${path}`, {
        ...options,
        headers,
    })

    const raw = await response.text()
    const data = raw ? tryParseJson(raw) : null

    if (!response.ok) {
        const detail =
            typeof data === 'object' && data && 'detail' in data
                ? String(data.detail)
                : `Request failed with status ${response.status}`
        throw new ApiError(response.status, detail)
    }

    return data as T
}

function tryParseJson(value: string): unknown {
    try {
        return JSON.parse(value)
    } catch {
        return value
    }
}

