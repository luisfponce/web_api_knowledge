import { describe, expect, it } from 'vitest'
import {
    applyPromptCatalogControls,
    defaultPromptCatalogControls,
    hasActivePromptCatalogControls,
    type PromptCatalogControls,
} from './prompt-catalog-utils'
import type { PromptRecord } from './prompts-types'

const prompts: PromptRecord[] = [
    {
        id: 1,
        user_id: 10,
        title: 'Draft email',
        model_name: 'GPT',
        prompt_text: 'Write a short customer update',
        category: 'Writing',
        rate: 4,
    },
    {
        id: 3,
        user_id: 10,
        title: 'Plan week',
        model_name: 'Claude',
        prompt_text: 'Group related tasks and risks',
        category: 'Planning',
        rate: 5,
    },
    {
        id: 2,
        user_id: 10,
        title: 'Review API',
        model_name: 'GPT',
        prompt_text: 'Find authorization gaps',
        category: 'Code Review',
        rate: 3,
    },
]

function controls(overrides: Partial<PromptCatalogControls>): PromptCatalogControls {
    return { ...defaultPromptCatalogControls, ...overrides }
}

describe('applyPromptCatalogControls', () => {
    it('sorts by newest by default', () => {
        expect(applyPromptCatalogControls(prompts, defaultPromptCatalogControls).map((prompt) => prompt.id)).toEqual([3, 2, 1])
    })

    it('searches title, prompt text, model, and category', () => {
        expect(applyPromptCatalogControls(prompts, controls({ search: 'authorization' })).map((prompt) => prompt.id)).toEqual([2])
        expect(applyPromptCatalogControls(prompts, controls({ search: 'planning' })).map((prompt) => prompt.id)).toEqual([3])
    })

    it('filters by model, category, and rating', () => {
        const result = applyPromptCatalogControls(prompts, controls({ model: 'GPT', category: 'Writing', rating: '4' }))

        expect(result.map((prompt) => prompt.id)).toEqual([1])
    })

    it('sorts by rating descending', () => {
        expect(applyPromptCatalogControls(prompts, controls({ sort: 'rating' })).map((prompt) => prompt.id)).toEqual([3, 1, 2])
    })
})

describe('hasActivePromptCatalogControls', () => {
    it('is false for defaults', () => {
        expect(hasActivePromptCatalogControls(defaultPromptCatalogControls)).toBe(false)
    })

    it('is true when filtering or sorting changes', () => {
        expect(hasActivePromptCatalogControls(controls({ search: 'api' }))).toBe(true)
        expect(hasActivePromptCatalogControls(controls({ sort: 'title' }))).toBe(true)
    })
})
