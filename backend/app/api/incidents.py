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
async def analyze_incident(
    payload: IncidentCreate,
    request: Request,
    use_memory: bool = Query(default=True, description="Set false to get a memory-less baseline answer"),
    exclude_incident_id: int | None = Query(default=None, description="Hide this incident's own memory when replaying it"),
) -> AnalysisResponse:
    try:
        return await service_for(request).analyze(payload, use_memory=use_memory, exclude_incident_id=exclude_incident_id)
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

from pydantic import BaseModel, Field as _Field


class AskRequest(BaseModel):
    question: str = _Field(min_length=3, max_length=500)


@router.post("/ask", summary="Ask a natural-language question about past incidents")
async def ask_incidents(payload: AskRequest, request: Request) -> dict:
    from sqlalchemy import select

    from backend.app.db.models import Incident
    from backend.app.services.ask_service import AskFailed, ask_gateway, retrieve

    incidents = list(request.state.session.scalars(select(Incident)))
    records = retrieve(incidents, payload.question)
    memories, memory_status = [], "skipped"
    try:
        recall = await request.app.state.hindsight.recall(payload.question)
        memories, memory_status = recall.memories, "ok"
    except Exception:
        memory_status = "unavailable"
    if not records and not memories:
        return {"question": payload.question, "answer": "No past incidents match this question yet.",
                "confidence": "low", "evidence": [], "follow_up": None, "sources": [], "memory_status": memory_status}
    try:
        result = await ask_gateway(payload.question, records, memories)
    except AskFailed as exc:
        raise HTTPException(status_code=exc.status, detail={"code": "ask_failed", "message": str(exc)}) from exc
    return {"question": payload.question, **result, "sources": records, "memory_status": memory_status,
            "memories_used": len(memories)}
