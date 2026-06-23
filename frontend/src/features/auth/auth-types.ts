export type LoginInput = {
    username: string
    password: string
}

export type LoginResponse = {
    access_token: string
    token_type: string
}

export type RegisterInput = {
    username: string
    password: string
    name: string
    last_name: string
    email: string
    role: 'user'
}

export type UserRole = 'user' | 'admin' | 'god'

export type UserRecord = {
    id: number
    username: string
    name: string
    last_name: string
    email: string
    role: UserRole
}

export type SignupResponse = {
    message: string
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
