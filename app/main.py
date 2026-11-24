from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.database import Base, engine
from app.routers import analyses


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.app_name,
    description=(
        "API que analisa a compatibilidade entre currículos e vagas de emprego, "
        "identifica competências faltantes e gera sugestões de melhoria com IA."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(analyses.router)


@app.get("/health", tags=["Status"])
def health():
    return {"status": "ok", "ia_configurada": bool(settings.llm_api_key)}
