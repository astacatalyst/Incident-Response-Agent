from backend.app.agents.schemas import IncidentAnalysis
from backend.app.db.models import Incident
from backend.app.llm.groq_client import GroqClient


class IncidentAgent:
    def __init__(self, groq: GroqClient):
        self.groq = groq

    async def analyze(self, incident: Incident, memories: list[dict]) -> IncidentAnalysis:
        current = {
            "incident_id": incident.id,
            "service": incident.service,
            "severity": incident.severity,
            "symptoms": incident.symptoms,
            "logs": incident.logs,
            "metrics": incident.metrics,
            "deployment_version": incident.deployment_version,
            "description": incident.description,
        }
        return await self.groq.analyze(current, memories)