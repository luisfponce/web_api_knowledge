import { z } from 'zod'

export const loginSchema = z.object({
    username: z.string().min(1, 'Username is required'),
    password: z.string().min(1, 'Password is required'),
})

export const registerSchema = z.object({
    name: z.string().min(1, 'First name is required'),
    last_name: z.string().min(1, 'Last name is required'),
    email: z.string().email('Enter a valid email'),
    username: z.string().min(3, 'Username must be at least 3 characters'),
    password: z.string().min(6, 'Password must be at least 6 characters'),
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
