type JwtPayload = {
    data?: {
        sub?: string
    }
}

export function extractUsernameFromToken(token: string): string | null {
    const parts = token.split('.')
    if (parts.length < 2) {
        return null
    }

    try {
        const payload = JSON.parse(decodeBase64Url(parts[1])) as JwtPayload
        return payload.data?.sub ?? null
    } catch {
        return null
    }
}

function decodeBase64Url(input: string): string {
    const normalized = input.replace(/-/g, '+').replace(/_/g, '/')
    const padded = normalized + '='.repeat((4 - (normalized.length % 4)) % 4)
    return atob(padded)
}
