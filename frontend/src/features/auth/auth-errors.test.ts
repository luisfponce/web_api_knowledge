import { describe, expect, it } from 'vitest'
import { ApiError } from '../../lib/http/api-error'
import { getRegistrationErrorMessageKey } from './auth-errors'

describe('getRegistrationErrorMessageKey', () => {
    it('maps duplicate username responses', () => {
        expect(getRegistrationErrorMessageKey(new ApiError(400, 'username already taken'))).toBe('auth.usernameTaken')
    })

    it('maps duplicate email responses', () => {
        expect(getRegistrationErrorMessageKey(new ApiError(400, 'email already taken'))).toBe('auth.emailTaken')
    })

    it('maps integrity fallback responses to a generic duplicate message', () => {
        expect(getRegistrationErrorMessageKey(new ApiError(400, 'registration information already in use'))).toBe('auth.registrationInfoTaken')
    })

    it('ignores non-registration status codes', () => {
        expect(getRegistrationErrorMessageKey(new ApiError(500, 'email already taken'))).toBeNull()
    })
})
