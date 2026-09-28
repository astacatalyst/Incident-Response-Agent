from math import ceil

from fastapi import APIRouter, HTTPException, Query, Request, status

from backend.app.agents.schemas import (
    AnalysisResponse,
    IncidentCreate,
    IncidentListResponse,
    IncidentRead,
    IncidentResolution,
    ResolutionResponse,
)
from backend.app.llm.groq_client import GroqNotConfigured
from backend.app.services.incident_service import AnalysisFailed, IncidentNotFound

router = APIRouter(prefix="/api/incidents", tags=["incidents"])


def service_for(request: Request):
    from backend.app.db.repositories import IncidentRepository
    from backend.app.services.incident_service import IncidentService

    return IncidentService(
        IncidentRepository(request.state.session),
        request.app.state.memory_service,
        request.app.state.agent,
    )


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Persist and analyze a new incident",
)
async def analyze_incident(payload: IncidentCreate, request: Request) -> AnalysisResponse:
    try:
        return await service_for(request).analyze(payload)
    except AnalysisFailed as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"code": "llm_unavailable", "message": str(exc)},
        ) from exc


@router.post(
    "/{incident_id}/resolve",
    response_model=ResolutionResponse,
    summary="Resolve an incident and retain its experience in Hindsight",
)
async def resolve_incident(
    incident_id: int,
    payload: IncidentResolution,
    request: Request,
) -> ResolutionResponse:
    try:
        result = await service_for(request).resolve(incident_id, payload)
    except IncidentNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if not result.memory_stored:
        # The SQLite resolution is intentionally retained, but the API signals
        # the external memory failure rather than pretending the learning step worked.
        from fastapi.responses import JSONResponse

        return JSONResponse(status_code=502, content=result.model_dump(mode="json"))
    return result


@router.get("", response_model=IncidentListResponse, summary="List incidents")
def list_incidents(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    service: str | None = Query(default=None, max_length=120),
    severity: str | None = Query(default=None),
    incident_status: str | None = Query(default=None, alias="status"),
) -> IncidentListResponse:
    return service_for(request).list_incidents(
        page=page,
        page_size=page_size,
        service=service,
        severity=severity,
        status=incident_status,
    )


@router.get("/{incident_id}", response_model=IncidentRead, summary="Get an incident")
def get_incident(incident_id: int, request: Request) -> IncidentRead:
    try:
        return service_for(request).get_incident(incident_id)
    except IncidentNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc