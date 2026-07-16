export type PromptRecord = {
    id: number
    user_id: number
    title: string
    model_name: string
    prompt_text: string
    category: string
    rate: number
}

export type PromptInput = {
    title: string
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
