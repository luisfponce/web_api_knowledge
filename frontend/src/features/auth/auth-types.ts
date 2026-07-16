export type LoginInput = {
    username: string
    password: string
}

export type LoginResponse = {
    access_token: string
    token_type: string
}

export type PreferredLanguage = 'es' | 'en'

export type RegisterInput = {
    username: string
    password: string
    name: string
    last_name: string
    email: string
    preferred_language: PreferredLanguage
}

export type UserRole = 'user' | 'admin' | 'god'

export type UserRecord = {
    id: number
    username: string
    name: string
    last_name: string
    email: string
    preferred_language: PreferredLanguage
    role: UserRole
}

export type SignupResponse = {
    message: string
    access_token: string
    token_type: string
    user: UserRecord
}

export type RecoveryGenerateInput = {
    username: string
}

export type RecoveryGenerateResponse = {
    message: string
}

export type RecoveryRedeemInput = {
    key: string
}

export type RecoveryRedeemResponse = {
    key: string
    password: string
}
