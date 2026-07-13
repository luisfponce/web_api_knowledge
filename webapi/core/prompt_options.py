MODEL_NAME_MAX_CHARS = 30

CATEGORY_OPTIONS = [
    {"value": "qa", "label": "QA"},
    {"value": "dev", "label": "Development"},
    {"value": "ops", "label": "Operations"},
    {"value": "writing", "label": "Writing"},
    {"value": "research", "label": "Research"},
]

MODEL_OPTIONS = [
    {"value": "gpt-4.1", "label": "GPT-4.1"},
    {"value": "gpt-4o-mini", "label": "GPT-4o mini"},
    {"value": "gpt-5", "label": "GPT-5"},
    {"value": "gpt-5-mini", "label": "GPT-5 mini"},
]

MODEL_OPTION_VALUES = frozenset(option["value"] for option in MODEL_OPTIONS)


def is_valid_model_name(value: str) -> bool:
    return value in MODEL_OPTION_VALUES
