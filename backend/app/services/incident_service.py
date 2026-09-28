import logging
import time
from uuid import uuid4

from backend.app.agents.incident_agent import IncidentAgent
from backend.app.agents.schemas import (
    AnalysisResponse,
    IncidentCreate,
    IncidentListResponse,
    IncidentRead,
    IncidentResolution,
    MemoryRecord,
    MemoryTransparency,
    ResolutionResponse,
)
from backend.app.db.models import Incident
from backend.app.db.repositories import IncidentRepository
from backend.app.llm.groq_client import GroqError
from backend.app.memory.memory_service import MemoryService

logger = logging.getLogger(__name__)


class IncidentNotFound(LookupError):
    pass


class AnalysisFailed(RuntimeError):
    pass


class IncidentService:
    def __init__(
        self,
        repository: IncidentRepository,
        memory: MemoryService,
        agent: IncidentAgent,
    ):
        self.repository = repository
        self.memory = memory
        self.agent = agent

    async def analyze(self, request: IncidentCreate) -> AnalysisResponse:
        request_id = str(uuid4())
        started = time.perf_counter()

        incident = self.repository.create(
            {
                **request.model_dump(),
                "status": "open",
                "is_synthetic": False,
            }
        )

        memories, memory_status, memory_error = await self.memory.recall(incident)

        logger.info(
            "incident_analysis request_id=%s incident_id=%s "
            "service=%s hindsight_status=%s memories_retrieved=%d",
            request_id,
            incident.id,
            incident.service,
            memory_status,
            len(memories),
        )

        try:
            analysis = await self.agent.analyze(
                incident,
                memories,
            )

        except GroqError as exc:
            logger.exception(
                "incident_analysis FAILED request_id=%s "
                "incident_id=%s error=%s",
                request_id,
                incident.id,
                exc,
            )

            raise AnalysisFailed(str(exc)) from exc

        except Exception as exc:
            logger.exception(
                "incident_analysis UNEXPECTED ERROR "
                "request_id=%s incident_id=%s error=%s",
                request_id,
                incident.id,
                exc,
            )

            raise AnalysisFailed(str(exc)) from exc

        logger.info(
            "incident_analysis request_id=%s incident_id=%s "
            "service=%s hindsight_status=%s memories_retrieved=%d "
            "llm_status=ok duration_ms=%.0f",
            request_id,
            incident.id,
            incident.service,
            memory_status,
            len(memories),
            (time.perf_counter() - started) * 1000,
        )

        transparency = MemoryTransparency(
            memory_used=bool(memories),
            memories_retrieved=len(memories),
            memories=[
                MemoryRecord.model_validate(memory)
                for memory in memories
            ],
            status=memory_status,
            error=memory_error,
        )

        return AnalysisResponse(
            incident=IncidentRead.model_validate(incident),
            analysis=analysis,
            memory=transparency,
            request_id=request_id,
            llm_status="ok",
        )

    def list_incidents(
        self,
        *,
        page: int,
        page_size: int,
        service: str | None,
        severity: str | None,
        status: str | None,
    ) -> IncidentListResponse:

        incidents, total = self.repository.list(
            page=page,
            page_size=page_size,
            service=service,
            severity=severity,
            status=status,
        )

        return IncidentListResponse(
            items=[
                IncidentRead.model_validate(item)
                for item in incidents
            ],
            page=page,
            page_size=page_size,
            total=total,
            pages=(total + page_size - 1) // page_size
            if total
            else 0,
        )

    def get_incident(self, incident_id: int) -> IncidentRead:
        incident = self.repository.get(incident_id)

        if not incident:
            raise IncidentNotFound(
                f"Incident {incident_id} was not found"
            )

        return IncidentRead.model_validate(incident)

    async def resolve(
        self,
        incident_id: int,
        request: IncidentResolution,
    ) -> ResolutionResponse:

        incident = self.repository.get(incident_id)

        if not incident:
            raise IncidentNotFound(
                f"Incident {incident_id} was not found"
            )

        incident = self.repository.resolve(
            incident,
            request.model_dump(),
        )

        stored, status, result, error = await self.memory.retain(
            incident
        )

        logger.info(
            "incident_resolution incident_id=%s "
            "memory_status=%s memory_stored=%s",
            incident.id,
            status,
            stored,
        )

        return ResolutionResponse(
            incident=IncidentRead.model_validate(incident),
            memory_stored=stored,
            memory_status=status,
            memory_result=result,
            memory_error=error,
        )