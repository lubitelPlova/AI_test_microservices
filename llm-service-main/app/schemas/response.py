from pydantic import BaseModel, Field, field_validator, ValidationInfo
from typing import List, Literal

class CheckResponse(BaseModel):
    suitable: Literal["yes", "no"]
    reason: str
    example_questions: list[str]
    confidence: float = Field(ge=0.0, le=1.0)


class QuestionItem(BaseModel):
    question: str
    ans: list[str]
    correct: str

    @field_validator('correct', mode='after')
    def validate_correct_in_ans(cls, v: str, info: ValidationInfo):
        ans_values = info.data.get('ans')
        if ans_values is None:
            raise ValueError('ans field is required for validation')

        if v not in ans_values:
            raise ValueError(
                f"Correct answer '{v}' must be present in ans list"
            )
        return v

class QuestionResponse(BaseModel):
    data: list[QuestionItem]

class LLMResponse(BaseModel):
    result: str