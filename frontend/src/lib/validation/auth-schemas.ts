import { z } from 'zod'

export const PASSWORD_MIN_LENGTH = 6
export const PASSWORD_MAX_LENGTH = 1024

export const COMMON_PASSWORDS = [
    'password',
    'password123',
    'password1234',
    '123456789012',
    'qwerty123456',
    'adminadmin123',
    'letmein123456',
    'welcome12345',
]

export function isCommonPassword(password: string) {
    return COMMON_PASSWORDS.includes(password.trim().toLowerCase())
}

export const loginSchema = z.object({
    username: z.string().min(1, 'Username is required'),
    password: z.string().min(1, 'Password is required'),
})

export const registerSchema = z.object({
    name: z.string().min(1, 'First name is required'),
    last_name: z.string().min(1, 'Last name is required'),
    email: z.string().email('Enter a valid email'),
    username: z.string().min(3, 'Username must be at least 3 characters'),
    password: z.string()
        .min(PASSWORD_MIN_LENGTH, `Password must be at least ${PASSWORD_MIN_LENGTH} characters`)
        .max(PASSWORD_MAX_LENGTH, 'Password does not meet the requirements')
        .refine((password) => !isCommonPassword(password), 'Password does not meet the requirements'),
    confirmPassword: z.string().min(1, 'Confirm password is required'),
    preferred_language: z.enum(['es', 'en']),
}).refine((data) => data.password === data.confirmPassword, {
    message: 'Passwords must match',
    path: ['confirmPassword'],
})

export const recoveryRequestSchema = z.object({
    username: z.string().min(1, 'Username is required'),
})

export const recoveryRedeemSchema = z.object({
    key: z.string().min(1, 'Recovery key is required'),
})

export type LoginFormValues = z.infer<typeof loginSchema>
export type RegisterFormValues = z.infer<typeof registerSchema>
export type RecoveryRequestFormValues = z.infer<typeof recoveryRequestSchema>
export type RecoveryRedeemFormValues = z.infer<typeof recoveryRedeemSchema>
