import { ApiError } from '../../lib/http/api-error'

export type RegistrationErrorMessageKey =
    | 'auth.usernameTaken'
    | 'auth.emailTaken'
    | 'auth.registrationInfoTaken'
    | 'auth.unableToCreate'

export function getRegistrationErrorMessageKey(error: unknown): RegistrationErrorMessageKey | null {
    if (!(error instanceof ApiError) || error.status !== 400) {
        return null
    }

    const detail = error.detail.toLowerCase()

    if (detail.includes('username')) {
        return 'auth.usernameTaken'
    }

    if (detail.includes('email')) {
        return 'auth.emailTaken'
    }

    if (detail.includes('already in use') || detail.includes('already taken')) {
        return 'auth.registrationInfoTaken'
    }

    return 'auth.unableToCreate'
}
