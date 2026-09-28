import json

from backend.app.db.models import Incident
from backend.app.memory.hindsight_client import HindsightClient, HindsightError


def build_recall_query(incident: Incident) -> str:
    metrics = ", ".join(f"{key}={value}" for key, value in incident.metrics.items())
    return (
        f"{incident.service} {incident.severity} incident: {incident.description}. "
        f"Symptoms: {', '.join(incident.symptoms)}. "
        f"Logs: {incident.logs[:4000]}. Metrics: {metrics}. "
        f"Deployment version: {incident.deployment_version}."
    )


def build_retained_memory(incident: Incident) -> str:
    return json.dumps(
        {
            "incident_id": incident.id,
            "service": incident.service,
            "severity": incident.severity,
            "symptoms": incident.symptoms,
            "metrics": incident.metrics,
            "logs": incident.logs[:8000],
            "deployment_version": incident.deployment_version,
            "description": incident.description,
            "root_cause": incident.root_cause,
            "resolution": incident.resolution,
            "successful": incident.successful,
            "resolution_time_minutes": incident.resolution_time_minutes,
            "lessons_learned": incident.lessons_learned,
            "source": "IncidentIQ synthetic development data"
            if incident.is_synthetic
            else "IncidentIQ engineer-resolved incident",
        },
        sort_keys=True,
    )


class MemoryService:
    def __init__(self, hindsight: HindsightClient):
        self.hindsight = hindsight

    async def recall(self, incident: Incident) -> tuple[list[dict], str, str | None]:
        try:
            result = await self.hindsight.recall(build_recall_query(incident))
            return result.memories, "ok", None
        except HindsightError as exc:
            status = "not_configured" if "required for Hindsight" in str(exc) else "unavailable"
            return [], status, str(exc)

    async def retain(self, incident: Incident) -> tuple[bool, str, dict | None, str | None]:
        try:
            result = await self.hindsight.retain(
                build_retained_memory(incident),
                incident_id=incident.id,
                tags=[f"service:{incident.service}", f"severity:{incident.severity}"],
            )
            if not result.success:
                return False, "error", result.raw, "Hindsight did not confirm retain success"
            return True, "stored", result.raw, None
        except HindsightError as exc:
            status = "not_configured" if "required for Hindsight" in str(exc) else "unavailable"
            return False, status, None, str(exc)