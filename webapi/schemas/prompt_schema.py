from pydantic import BaseModel


class PromptRead(BaseModel):
    id: int
    model_name: str
    prompt_text: str
    category: str
    rate: str

    class Config:
        from_attributes = True
