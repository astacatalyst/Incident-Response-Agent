from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from backend.app.agents.incident_agent import IncidentAgent
from backend.app.api.health import router as health_router
from backend.app.api.incidents import router as incidents_router
from backend.app.api.memory import router as memory_router
from backend.app.config import Settings, get_settings
from backend.app.db.database import build_engine, build_session_factory, get_db_session, init_db
from backend.app.llm.groq_client import GroqClient
from backend.app.memory.hindsight_client import HindsightClient
from backend.app.memory.memory_service import MemoryService
from backend.app.utils.logging import configure_logging


def create_app(
    settings: Settings | None = None,
    *,
    engine=None,
    hindsight=None,
    groq=None,
) -> FastAPI:
    settings = settings or get_settings()
    engine = engine or build_engine(settings.effective_database_url)
    init_db(engine)
    session_factory = build_session_factory(engine)
    hindsight = hindsight or HindsightClient(settings)
    groq = groq or GroqClient(settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        configure_logging()
        yield

    app = FastAPI(
        title="IncidentIQ Backend",
        version="1.0.0",
        description=(
            "AI-powered incident response API using SQLite, Hindsight persistent "
            "memory, and Groq structured analysis."
        ),
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )
    app.state.settings = settings
    app.state.engine = engine
    app.state.session_factory = session_factory
    app.state.hindsight = hindsight
    app.state.groq = groq
    app.state.memory_service = MemoryService(hindsight)
    app.state.agent = IncidentAgent(groq)

    @app.middleware("http")
    async def db_session_middleware(request: Request, call_next):
        with session_factory() as session:
            request.state.session = session
            return await call_next(request)

    app.include_router(health_router)
    app.include_router(incidents_router)
    app.include_router(memory_router)
    return app


app = create_app()