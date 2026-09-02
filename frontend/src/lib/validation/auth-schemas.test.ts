import { describe, expect, it } from 'vitest'
import { registerSchema } from './auth-schemas'

const validRegistration = {
    name: 'Py',
    last_name: 'Tester',
    email: 'pytest@example.com',
    username: 'pytest_user',
    password: 'pytest_password',
    confirmPassword: 'pytest_password',
    preferred_language: 'es' as const,
}

describe('registerSchema', () => {
    it('rejects passwords shorter than 6 characters', () => {
        const parsed = registerSchema.safeParse({
            ...validRegistration,
            password: 'short',
            confirmPassword: 'short',
        })

        expect(parsed.success).toBe(false)
    })

    it('rejects mismatched password confirmation', () => {
        const parsed = registerSchema.safeParse({
            ...validRegistration,
            confirmPassword: 'different_password',
        })

        expect(parsed.success).toBe(false)
    })

    it('rejects common passwords', () => {
        const parsed = registerSchema.safeParse({
            ...validRegistration,
            password: 'password1234',
            confirmPassword: 'password1234',
        })

        expect(parsed.success).toBe(false)
    })

    it('accepts matching 6 character or longer passwords', () => {
        const parsed = registerSchema.safeParse(validRegistration)

        expect(parsed.success).toBe(true)
    })
})
