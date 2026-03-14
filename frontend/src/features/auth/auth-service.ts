import { apiRequest } from '../../lib/http/api-client'
import { extractUsernameFromToken } from '../../lib/utils/jwt'
import type { LoginInput, LoginResponse, UserRecord } from './auth-types'

export type SessionResolved = {
    token: string
    username: string
    userId: number
}

export async function loginAndResolveUserId(
    input: LoginInput,
): Promise<SessionResolved> {
    const login = await apiRequest<LoginResponse>('/auth/login', {
        method: 'POST',
        body: JSON.stringify(input),
    })

    const username = extractUsernameFromToken(login.access_token)
    if (!username) {
        throw new Error('Unable to read username from token')
    }

    const currentUser = await resolveUserByUsername(login.access_token, username)

    return {
        token: login.access_token,
        username,
        userId: currentUser.id,
    }
}

const USERS_PAGE_SIZE = 100

async function resolveUserByUsername(
    token: string,
    username: string,
): Promise<UserRecord> {
    for (let skip = 0; ; skip += USERS_PAGE_SIZE) {
        const users = await apiRequest<UserRecord[]>(
            `/users?skip=${skip}&limit=${USERS_PAGE_SIZE}`,
            {
                method: 'GET',
                token,
            },
        )

        const match = users.find((user) => user.username === username)
        if (match) {
            return match
        }

        if (users.length < USERS_PAGE_SIZE) {
            break
        }
    }

    throw new Error('User id not found for authenticated username')
}
