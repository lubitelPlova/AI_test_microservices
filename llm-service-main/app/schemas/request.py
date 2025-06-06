from pydantic import BaseModel

class LLMRequest(BaseModel):
    prompt: str