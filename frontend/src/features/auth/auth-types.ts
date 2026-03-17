export type LoginInput = {
    username: string
    password: string
}

export type LoginResponse = {
    access_token: string
    token_type: string
}

export type UserRecord = {
    id: number
    username: string
    name: string
    last_name: string
    phone: number | null
    email: string
}
