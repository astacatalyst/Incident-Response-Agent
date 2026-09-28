from fastapi import APIRouter, Request

from backend.app.agents.schemas import MemoryDashboardResponse
from backend.app.db.repositories import IncidentRepository

router = APIRouter(prefix="/api/memory", tags=["memory"])


@router.get("", response_model=MemoryDashboardResponse, summary="Get memory dashboard data")
async def memory_dashboard(request: Request) -> MemoryDashboardResponse:
    summary = IncidentRepository(request.state.session).summary()
    hindsight_health = await request.app.state.hindsight.health()
    hindsight_stats = None
    hindsight_status = hindsight_health.get("status", "unavailable")
    if hindsight_status == "ok":
        try:
            hindsight_stats = await request.app.state.hindsight.stats()
        except Exception:
            hindsight_status = "unavailable"
    return MemoryDashboardResponse(
        incident_count=summary["incident_count"],
        resolved_incident_count=summary["resolved_incident_count"],
        successful_resolutions=summary["successful_resolutions"],
        unsuccessful_resolutions=summary["unsuccessful_resolutions"],
        services=summary["services"],
        recurring_root_causes=summary["recurring_root_causes"],
        recent_resolved=summary["recent_resolved"],
        hindsight_status=hindsight_status,
        hindsight_stats=hindsight_stats,
    )