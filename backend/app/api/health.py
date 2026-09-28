from fastapi import APIRouter, Request

from backend.app.agents.schemas import HealthResponse
from backend.app.db.database import check_database

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, summary="Check backend and dependency health")
async def health(request: Request) -> HealthResponse:
    database_status = "ok" if check_database(request.app.state.engine) else "unavailable"
    hindsight_status = (await request.app.state.hindsight.health()).get("status", "unavailable")
    llm_status = (await request.app.state.groq.health()).get("status", "unavailable")
    statuses = {database_status, hindsight_status, llm_status}
    return HealthResponse(
        status="ok" if statuses == {"ok"} else "degraded",
        database=database_status,
        hindsight=hindsight_status,
        llm=llm_status,
    )