from app.core.config import settings
from huggingface_hub import InferenceClient


client = InferenceClient(
    provider=settings.PROVIDER,
    api_key=settings.API_KEY
)

def load_system_prompt(path: str = "prompts/prompt.txt") -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

def init_prompts() -> dict:
    prompts = {
        "check": load_system_prompt('prompts/check_prompt.txt'),
        "extract": load_system_prompt('prompts/extract_prompt.txt')
    }
    return prompts

async def generate_text(messages) -> str:
    """
    Отправляет запрос к модели через Hugging Face Inference API и возвращает ответ.

    :param prompt: Входной текст для генерации
    :return: Сгенерированный текст
    """

    try:
        completion = client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=messages,
            max_tokens=5000,
        )

        return completion.choices[0].message.content.strip()
    except Exception as e:
        raise RuntimeError(f"Ошибка при вызове модели: {e}")



