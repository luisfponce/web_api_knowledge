import { z } from 'zod'

const PROMPT_TEXT_MAX_CHARS = 1_000_000

export const promptSchema = z.object({
    model_name: z.string().min(1, 'Model name is required'),
    prompt_text: z
        .string()
        .min(1, 'Prompt text is required')
        .max(
            PROMPT_TEXT_MAX_CHARS,
            `Prompt text must be at most ${PROMPT_TEXT_MAX_CHARS.toLocaleString()} characters`,
        ),
    category: z.string().min(1, 'Category is required'),
    rate: z.coerce
        .number()
        .int('Rating must be a whole number')
        .min(1, 'Rating must be at least 1')
        .max(5, 'Rating must be at most 5'),
})

export type PromptFormValues = z.infer<typeof promptSchema>
