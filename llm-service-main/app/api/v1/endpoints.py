from fastapi import APIRouter, HTTPException, Depends, Request
from app.schemas.request import LLMRequest
from app.schemas.response import LLMResponse, QuestionResponse, CheckResponse
from app.services.llm_service import generate_text
import json


router = APIRouter()

async def get_prompts(request: Request) -> dict:
    return request.app.state.prompts

@router.post("/generate", response_model=LLMResponse) #  response_model=LLMResponse
async def generate(request: LLMRequest):
    messages = [{
        'role': "user",
        'content': request.prompt
    }]
    result = await generate_text(messages)
    return {'result': result}

@router.post("/check_text", response_model=CheckResponse) #  response_model=LLMResponse
async def check(request: LLMRequest, prompts: dict = Depends(get_prompts)):
    messages = [
        {
          'role': 'system',
          'content': prompts['check']
        },
        {
        'role': "user",
        'content': request.prompt
        }
    ]
    raw_response = await generate_text(messages)
    try:
        parsed_data = json.loads(raw_response)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Модель вернула невалидный JSON")
    return parsed_data

@router.post("/extract_test", response_model=QuestionResponse) #  response_model=LLMResponse
async def extract(request: LLMRequest, prompts: dict = Depends(get_prompts)):
    messages = [
        {
            'role': 'system',
            'content': prompts['extract']
        },
        {
            'role': "user",
            'content': request.prompt
        }
    ]
    raw_response = await generate_text(messages)
    try:
        parsed_data = json.loads(raw_response)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Модель вернула невалидный JSON")
    return parsed_data