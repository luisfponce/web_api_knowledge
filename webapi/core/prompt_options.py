MODEL_NAME_MAX_CHARS = 30

CATEGORY_OPTIONS = [
    {"value": "others", "label": "Others"},
    {"value": "development", "label": "Software Development"},
    {"value": "data_analysis", "label": "Data Analysis"},
    {"value": "writing", "label": "Writing & Editing"},
    {"value": "research", "label": "Research"},
    {"value": "marketing_sales", "label": "Marketing & Sales"},
    {"value": "finance", "label": "Finance & Investing"},
    {"value": "science_education", "label": "Science & Education"},
    {"value": "personal_development", "label": "Personal Development"},
    {"value": "productivity_ops", "label": "Productivity & Operations"},
]

MODEL_OPTIONS = [
    {"value": "gpt", "label": "GPT"},
    {"value": "claude", "label": "Claude"},
    {"value": "gemini", "label": "Gemini"},
    {"value": "deepseek", "label": "DeepSeek"},
    {"value": "llama", "label": "Llama"},
    {"value": "qwen", "label": "Qwen"},
    {"value": "mistral", "label": "Mistral"},
    {"value": "grok", "label": "Grok"},
    {"value": "command", "label": "Command"},
    {"value": "kimi", "label": "Kimi"},
    {"value": "gemma", "label": "Gemma"},
    {"value": "phi", "label": "Phi"},
    {"value": "glm", "label": "GLM"},
    {"value": "nova", "label": "Nova"},
    {"value": "jamba", "label": "Jamba"},
    {"value": "yi", "label": "Yi"},
    {"value": "falcon", "label": "Falcon"},
    {"value": "mixtral", "label": "Mixtral"},
    {"value": "sonar", "label": "Sonar"},
    {"value": "dbrx", "label": "DBRX"},
]

MODEL_OPTION_VALUES = frozenset(option["value"] for option in MODEL_OPTIONS)


def is_valid_model_name(value: str) -> bool:
    return value in MODEL_OPTION_VALUES
