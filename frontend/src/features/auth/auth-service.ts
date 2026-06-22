import { apiRequest } from '../../lib/http/api-client'
import type {
    LoginInput,
    LoginResponse,
    RegisterInput,
    RecoveryGenerateInput,
    RecoveryGenerateResponse,
    RecoveryRedeemInput,
    RecoveryRedeemResponse,
    SignupResponse,
    UserRecord,
    UserRole,
} from './auth-types'

export type SessionResolved = {
    token: string
    username: string
    userId: number
    role: UserRole
}

export async function loginAndResolveUserId(
    input: LoginInput,
): Promise<SessionResolved> {
    const login = await apiRequest<LoginResponse>('/auth/login', {
        method: 'POST',
        body: JSON.stringify(input),
    })

    const currentUser = await getCurrentUser(login.access_token)

    return {
        token: login.access_token,
        username: currentUser.username,
        userId: currentUser.id,
        role: currentUser.role,
    }
}

export function signup(input: RegisterInput): Promise<SignupResponse> {
    return apiRequest<SignupResponse>('/auth/signup', {
        method: 'POST',
        body: JSON.stringify(input),
    })
}

export function getCurrentUser(token: string): Promise<UserRecord> {
    return apiRequest<UserRecord>('/auth/profile', {
        method: 'GET',
        token,
    })
}

export function requestRecoveryKey(
    input: RecoveryGenerateInput,
): Promise<RecoveryGenerateResponse> {
    return apiRequest<RecoveryGenerateResponse>('/auth/generate', {
        method: 'POST',
        body: JSON.stringify(input),
    })
}

export function redeemRecoveryKey(
    input: RecoveryRedeemInput,
): Promise<RecoveryRedeemResponse> {
    return apiRequest<RecoveryRedeemResponse>('/auth/recover', {
        method: 'POST',
        body: JSON.stringify(input),
    })
}
