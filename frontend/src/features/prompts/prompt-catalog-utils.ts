import type { PromptRecord } from './prompts-types'

export type PromptCatalogSort = 'newest' | 'title' | 'rating' | 'model' | 'category'

export type PromptCatalogControls = {
    search: string
    model: string
    category: string
    rating: string
    sort: PromptCatalogSort
}

export const defaultPromptCatalogControls: PromptCatalogControls = {
    search: '',
    model: '',
    category: '',
    rating: '',
    sort: 'newest',
}

export function hasActivePromptCatalogControls(controls: PromptCatalogControls) {
    return Boolean(
        controls.search.trim() ||
        controls.model ||
        controls.category ||
        controls.rating ||
        controls.sort !== defaultPromptCatalogControls.sort,
    )
}

export function applyPromptCatalogControls(prompts: PromptRecord[], controls: PromptCatalogControls) {
    const query = normalizeSearchValue(controls.search)
    const selectedRating = controls.rating ? Number(controls.rating) : null

    const filteredPrompts = prompts.filter((prompt) => {
            if (controls.model && prompt.model_name !== controls.model) {
                return false
            }

            if (controls.category && prompt.category !== controls.category) {
                return false
            }

            if (selectedRating !== null && prompt.rate !== selectedRating) {
                return false
            }

            if (!query) {
                return true
            }

            return [prompt.title, prompt.prompt_text, prompt.model_name, prompt.category]
                .some((value) => normalizeSearchValue(value).includes(query))
        })

    return [...filteredPrompts].sort((left, right) => comparePrompts(left, right, controls.sort))
}

function comparePrompts(left: PromptRecord, right: PromptRecord, sort: PromptCatalogSort) {
    switch (sort) {
        case 'title':
            return compareText(left.title, right.title) || compareNewest(left, right)
        case 'rating':
            return right.rate - left.rate || compareNewest(left, right)
        case 'model':
            return compareText(left.model_name, right.model_name) || compareNewest(left, right)
        case 'category':
            return compareText(left.category, right.category) || compareNewest(left, right)
        case 'newest':
        default:
            return compareNewest(left, right)
    }
}

function compareNewest(left: PromptRecord, right: PromptRecord) {
    return right.id - left.id
}

function compareText(left: string, right: string) {
    return left.localeCompare(right, undefined, { sensitivity: 'base' })
}

function normalizeSearchValue(value: string) {
    return value.trim().toLowerCase()
}
