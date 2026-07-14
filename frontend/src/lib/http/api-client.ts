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
        const detail = getErrorDetail(data, response.status)
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

function getErrorDetail(data: unknown, status: number): string {
    if (isRecord(data) && 'detail' in data) {
        return formatDetail(data.detail, status)
    }

    return fallbackMessage(status)
}

function formatDetail(detail: unknown, status: number): string {
    if (typeof detail === 'string') {
        return detail
    }

    if (Array.isArray(detail)) {
        const messages = detail
            .map(formatValidationItem)
            .filter((message): message is string => Boolean(message))

        return messages.length > 0 ? messages.join('; ') : fallbackMessage(status)
    }

    if (isRecord(detail)) {
        const json = safeStringify(detail)
        return json ?? fallbackMessage(status)
    }

    return fallbackMessage(status)
}

function formatValidationItem(item: unknown): string | null {
    if (typeof item === 'string') {
        return item
    }

    if (!isRecord(item)) {
        return null
    }

    const message = typeof item.msg === 'string' ? item.msg : null
    const location = formatLocation(item.loc)

    if (message && location) {
        return `${location}: ${message}`
    }

    return message ?? safeStringify(item)
}

function formatLocation(loc: unknown): string | null {
    if (!Array.isArray(loc)) {
        return null
    }

    const parts = loc
        .filter((part): part is string | number => typeof part === 'string' || typeof part === 'number')
        .filter((part) => part !== 'body')

    return parts.length > 0 ? parts.join('.') : null
}

function safeStringify(value: unknown): string | null {
    try {
        const json = JSON.stringify(value)
        return typeof json === 'string' ? json : null
    } catch {
        return null
    }
}

function isRecord(value: unknown): value is Record<string, unknown> {
    return typeof value === 'object' && value !== null
}

function fallbackMessage(status: number): string {
    return `Request failed with status ${status}`
}
