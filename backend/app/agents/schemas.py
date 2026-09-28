from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


Severity = Literal["low", "medium", "high", "critical"]
IncidentStatus = Literal["open", "resolved"]
Confidence = Literal["low", "medium", "high"]


class IncidentCreate(BaseModel):
    service: str = Field(min_length=1, max_length=120)
    severity: Severity
    symptoms: list[str] = Field(min_length=1, max_length=50)
    logs: str = Field(min_length=1, max_length=50_000)
    metrics: dict[str, float] = Field(default_factory=dict, max_length=100)
    deployment_version: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1, max_length=10_000)

    @field_validator("symptoms")
    @classmethod
    def validate_symptoms(cls, value: list[str]) -> list[str]:
        if any(not item.strip() or len(item) > 500 for item in value):
            raise ValueError("Each symptom must be 1-500 characters")
        return [item.strip() for item in value]

    @field_validator("metrics")
    @classmethod
    def validate_metrics(cls, value: dict[str, float]) -> dict[str, float]:
        for key, number in value.items():
            if not key.strip() or len(key) > 120:
                raise ValueError("Metric names must be 1-120 characters")
            if number != number or number in (float("inf"), float("-inf")):
                raise ValueError("Metric values must be finite numbers")
        return value


class IncidentResolution(BaseModel):
    root_cause: str = Field(min_length=1, max_length=10_000)
    resolution: str = Field(min_length=1, max_length=20_000)
    successful: bool
    resolution_time_minutes: int = Field(ge=0, le=1_000_000)
    lessons_learned: str = Field(min_length=1, max_length=10_000)


class IncidentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    service: str
    severity: Severity
    symptoms: list[str]
    logs: str
    metrics: dict[str, float]
    deployment_version: str
    description: str
    status: IncidentStatus
    root_cause: str | None
    resolution: str | None
    successful: bool | None
    resolution_time_minutes: int | None
    lessons_learned: str | None
    is_synthetic: bool
    created_at: datetime
    resolved_at: datetime | None


class RecommendedAction(BaseModel):
    step: str = Field(min_length=1, max_length=2_000)
    reason: str = Field(min_length=1, max_length=2_000)


class SimilarIncident(BaseModel):
    incident_id: str
    reason: str = Field(min_length=1, max_length=2_000)


class IncidentAnalysis(BaseModel):
    summary: str = Field(min_length=1, max_length=10_000)
    likely_root_cause: str = Field(min_length=1, max_length=10_000)
    confidence: Confidence
    evidence: list[str] = Field(max_length=30)
    recommended_actions: list[RecommendedAction] = Field(max_length=20)
    similar_incidents: list[SimilarIncident] = Field(max_length=20)
    memory_insights: list[str] = Field(max_length=30)
    uncertainties: list[str] = Field(max_length=30)


class MemoryRecord(BaseModel):
    id: str | None = None
    source: str | None = None
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    scores: dict[str, float | None] | None = None
    type: str | None = None


class MemoryTransparency(BaseModel):
    memory_used: bool
    memories_retrieved: int
    memories: list[MemoryRecord]
    status: Literal["ok", "unavailable", "not_configured", "error"]
    error: str | None = None


class AnalysisResponse(BaseModel):
    incident: IncidentRead
    analysis: IncidentAnalysis
    memory: MemoryTransparency
    request_id: str
    llm_status: Literal["ok"]


class ResolutionResponse(BaseModel):
    incident: IncidentRead
    memory_stored: bool
    memory_status: Literal["stored", "unavailable", "not_configured", "error"]
    memory_result: dict[str, Any] | None = None
    memory_error: str | None = None


class IncidentListResponse(BaseModel):
    items: list[IncidentRead]
    page: int
    page_size: int
    total: int
    pages: int


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    database: str
    hindsight: str
    llm: str


class MemoryDashboardResponse(BaseModel):
    incident_count: int
    resolved_incident_count: int
    successful_resolutions: int
    unsuccessful_resolutions: int
    services: list[str]
    recurring_root_causes: list[dict[str, Any]]
    recent_resolved: list[IncidentRead]
    hindsight_status: str
    hindsight_stats: dict[str, Any] | None = None