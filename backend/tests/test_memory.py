import pytest


@pytest.mark.asyncio
async def test_memory_transparency_and_dashboard(app_factory, incident_payload):
    memory = {
        "id": "memory-1",
        "source": "incident-42",
        "content": "Payment database CPU was high and a missing index was fixed.",
        "metadata": {"document_id": "incident-42", "type": "experience"},
        "scores": {"final": 0.91},
        "type": "experience",
    }
    app, _, _ = app_factory(memories=[memory])
    from httpx import ASGITransport, AsyncClient

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/incidents/analyze", json=incident_payload)
        assert response.status_code == 201
        body = response.json()
        assert body["memory"]["memory_used"] is True
        assert body["memory"]["memories_retrieved"] == 1
        assert body["memory"]["memories"][0]["id"] == "memory-1"
        assert body["memory"]["memories"][0]["scores"]["final"] == 0.91

        dashboard = await client.get("/api/memory")
        assert dashboard.status_code == 200
        assert dashboard.json()["hindsight_status"] == "ok"


@pytest.mark.asyncio
async def test_hindsight_failure_is_reported_without_fake_memory(app_factory, incident_payload):
    app, _, groq = app_factory(fail_recall=True)
    from httpx import ASGITransport, AsyncClient

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/incidents/analyze", json=incident_payload)
        assert response.status_code == 201
        body = response.json()
        assert body["memory"]["memory_used"] is False
        assert body["memory"]["status"] == "unavailable"
        assert groq.calls[0]["memories"] == []