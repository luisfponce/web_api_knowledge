export type PromptRecord = {
    id: number
    user_id: number
    model_name: string
    prompt_text: string
    category: string
    rate: string
}

export type PromptInput = {
    model_name: string
    prompt_text: string
    category: string
    rate: string
}

