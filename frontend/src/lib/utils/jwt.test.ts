import { describe, expect, it } from 'vitest'
import { extractUsernameFromToken } from './jwt'

function createToken(payload: object): string {
    const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }))
    const body = btoa(JSON.stringify(payload))
    return `${header}.${body}.signature`
}

describe('extractUsernameFromToken', () => {
    it('returns username from nested payload data', () => {
        const token = createToken({ data: { sub: 'luis' } })
        expect(extractUsernameFromToken(token)).toBe('luis')
    })

    it('returns null for invalid token', () => {
        expect(extractUsernameFromToken('invalid')).toBeNull()
    })
})

