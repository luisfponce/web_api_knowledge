import { z } from 'zod'

export const promptSchema = z.object({
    model_name: z.string().min(1, 'Model name is required'),
    prompt_text: z
        .string()
        .min(1, 'Prompt text is required')
        .max(150, 'Prompt text must be at most 150 characters'),
    category: z.string().min(1, 'Category is required'),
    rate: z.coerce
        .number()
        .int('Rating must be a whole number')
        .min(1, 'Rating must be at least 1')
        .max(5, 'Rating must be at most 5'),
})

export type PromptFormValues = z.infer<typeof promptSchema>
