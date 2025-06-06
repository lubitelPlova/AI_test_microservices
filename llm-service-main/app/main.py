from fastapi import FastAPI
from .api.v1.endpoints import router as v1_router
from contextlib import asynccontextmanager
from .services.llm_service import init_prompts


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.prompts = init_prompts()
    print("Startup complete")
    yield
    print("Shutdown complete")

app = FastAPI(title="LLM Service", lifespan=lifespan)

app.include_router(v1_router, prefix="/api/v1")