export type PromptRecord = {
    id: number
    user_id: number
    model_name: string
    prompt_text: string
    category: string
    rate: number
}

export type PromptInput = {
    model_name: string
    prompt_text: string
    category: string
    rate: number
}

export type PromptFilters = {
    user_id?: number
    category?: string
    model_name?: string
    rate?: number
}
