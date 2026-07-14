import { describe, expect, it } from 'vitest'
import { promptSchema } from './prompt-schemas'

const validPrompt = {
    model_name: 'gpt',
    prompt_text: 'Generate answer',
    category: 'qa',
    rate: 5,
}

describe('promptSchema', () => {
    it('trims model_name before submit', () => {
        const parsed = promptSchema.parse({
            ...validPrompt,
            model_name: ' gpt ',
        })

        expect(parsed.model_name).toBe('gpt')
    })

    it('rejects blank model_name', () => {
        const parsed = promptSchema.safeParse({
            ...validPrompt,
            model_name: '   ',
        })

        expect(parsed.success).toBe(false)
    })
})
