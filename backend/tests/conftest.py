import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from backend.app.config import Settings
from backend.app.main import create_app


class FakeHindsight:
    def __init__(self, memories=None, fail_recall=False, fail_retain=False):
        self.memories = memories or []
        self.fail_recall = fail_recall
        self.fail_retain = fail_retain
        self.retain_calls = []

    async def health(self):
        return {"status": "ok"}

    async def stats(self):
        return {"memory_count": len(self.memories)}

    async def recall(self, query):
        if self.fail_recall:
            from backend.app.memory.hindsight_client import HindsightError

            raise HindsightError("Hindsight unavailable")
        return type("Recall", (), {"memories": self.memories, "raw": {"results": self.memories}})()

    async def retain(self, content, *, incident_id, tags):
        if self.fail_retain:
            from backend.app.memory.hindsight_client import HindsightError

            raise HindsightError("Hindsight retain unavailable")
        self.retain_calls.append({"content": content, "incident_id": incident_id, "tags": tags})
        return type("Retain", (), {"success": True, "raw": {"success": True, "items_count": 1}})()


class FakeGroq:
    def __init__(self, fail=False):
        self.fail = fail
        self.calls = []

    async def health(self):
        return {"status": "ok"}

    async def analyze(self, incident, memories):
        if self.fail:
            from backend.app.llm.groq_client import GroqError

            raise GroqError("Groq unavailable")
        self.calls.append({"incident": incident, "memories": memories})
        from backend.app.agents.schemas import IncidentAnalysis

        return IncidentAnalysis(
            summary="Current evidence indicates a database saturation incident.",
            likely_root_cause="Database workload saturation; verify query plans.",
            confidence="medium",
            evidence=["database CPU is elevated"],
            recommended_actions=[
                {"step": "Inspect slow queries and query plans", "reason": "Confirm the active database bottleneck."}
            ],
            similar_incidents=[{"incident_id": "incident-42", "reason": "Same payment database symptom pattern."}]
            if memories
            else [],
            memory_insights=["A retrieved historical experience mentioned a related database issue."]
            if memories
            else [],
            uncertainties=["The active query plan is not yet available."],
        )


@pytest.fixture
def incident_payload():
    return {
        "service": "payment-api",
        "severity": "critical",
        "symptoms": ["latency above 9 seconds", "database CPU above 95%"],
        "logs": "database query timeout after 8000ms",
        "metrics": {"db_cpu": 96, "latency_ms": 9200, "error_rate": 17},
        "deployment_version": "v2.4.1",
        "description": "Payment requests are timing out.",
    }


@pytest.fixture
def app_factory(tmp_path):
    def factory(*, memories=None, fail_recall=False, fail_retain=False, fail_groq=False):
        settings = Settings(
            DATABASE_URL=f"sqlite:///{tmp_path / 'test.db'}",
            HINDSIGHT_API_URL="https://test-hindsight.invalid",
            HINDSIGHT_BANK_ID="incidentiq-test",
            GROQ_API_KEY="test-key",
        )
        hindsight = FakeHindsight(memories, fail_recall, fail_retain)
        groq = FakeGroq(fail_groq)
        return create_app(settings, hindsight=hindsight, groq=groq), hindsight, groq

    return factory


@pytest_asyncio.fixture
async def client(app_factory):
    app, _, _ = app_factory()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client