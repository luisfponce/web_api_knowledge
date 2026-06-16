import { z } from 'zod'

export const loginSchema = z.object({
    username: z.string().min(1, 'Username is required'),
    password: z.string().min(1, 'Password is required'),
})

export const recoveryRequestSchema = z.object({
    username: z.string().min(1, 'Username is required'),
})

export const recoveryRedeemSchema = z.object({
    key: z.string().min(1, 'Recovery key is required'),
})

export type LoginFormValues = z.infer<typeof loginSchema>
export type RecoveryRequestFormValues = z.infer<typeof recoveryRequestSchema>
export type RecoveryRedeemFormValues = z.infer<typeof recoveryRedeemSchema>
