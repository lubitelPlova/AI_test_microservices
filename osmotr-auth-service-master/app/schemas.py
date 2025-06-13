from pydantic import BaseModel, EmailStr
from typing import Dict, List, Any

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True


class QuestionItem(BaseModel):
    question: str
    ans: list[str]
    correct: str

class SaveTest(BaseModel):
    title: str
    questions: List[QuestionItem]

# Схема для метаданных теста
class TestMetadata(BaseModel):
    id: str
    test_metadata: Dict[str, Any]
    owner_email: EmailStr

    class Config:
        orm_mode = True

# Схема для ответа с тестами
class TestsResponse(BaseModel):
    tests: List[TestMetadata]

