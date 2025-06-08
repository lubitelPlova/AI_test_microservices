from fastapi import FastAPI
from .api.v1.endpoints import router as v1_router
from contextlib import asynccontextmanager
from .services.llm_service import init_prompts
from fastapi.middleware.cors import CORSMiddleware



@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.prompts = init_prompts()
    print("Startup complete")
    yield
    print("Shutdown complete")

app = FastAPI(title="LLM Service", lifespan=lifespan)

origins = [
    "http://localhost",# Адрес вашего фронтенда
    "null"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router, prefix="/api/v1")