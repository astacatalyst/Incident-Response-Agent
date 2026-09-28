import pytest


@pytest.mark.asyncio
async def test_learning_flow_passes_recalled_memory_to_llm(app_factory, incident_payload):
    memory = {
        "id": "hindsight-result-1",
        "source": "incident-1",
        "content": "A prior payment incident was resolved by adding a composite index.",
        "metadata": {"document_id": "incident-1", "type": "experience"},
        "scores": {"final": 0.88},
        "type": "experience",
    }
    app, hindsight, groq = app_factory(memories=[memory])
    from httpx import ASGITransport, AsyncClient

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        first = await client.post("/api/incidents/analyze", json=incident_payload)
        assert first.status_code == 201
        incident_id = first.json()["incident"]["id"]

        resolved = await client.post(
            f"/api/incidents/{incident_id}/resolve",
            json={
                "root_cause": "Missing index",
                "resolution": "Added composite index",
                "successful": True,
                "resolution_time_minutes": 37,
                "lessons_learned": "Check indexes when database CPU and latency rise together.",
            },
        )
        assert resolved.status_code == 200
        assert resolved.json()["memory_stored"] is True
        assert len(hindsight.retain_calls) == 1
        assert "Missing index" in hindsight.retain_calls[0]["content"]

        second = await client.post("/api/incidents/analyze", json=incident_payload)
        assert second.status_code == 201
        assert second.json()["memory"]["memories_retrieved"] == 1
        assert groq.calls[-1]["memories"][0]["id"] == "hindsight-result-1"


@pytest.mark.asyncio
async def test_groq_failure_does_not_create_fake_analysis(app_factory, incident_payload):
    app, _, _ = app_factory(fail_groq=True)
    from httpx import ASGITransport, AsyncClient

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/incidents/analyze", json=incident_payload)
        assert response.status_code == 502
        assert response.json()["detail"]["code"] == "llm_unavailable"


@pytest.mark.asyncio
async def test_retain_failure_is_not_reported_as_success(app_factory, incident_payload):
    app, _, _ = app_factory(fail_retain=True)
    from httpx import ASGITransport, AsyncClient

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        analyzed = await client.post("/api/incidents/analyze", json=incident_payload)
        incident_id = analyzed.json()["incident"]["id"]
        response = await client.post(
            f"/api/incidents/{incident_id}/resolve",
            json={
                "root_cause": "A real root cause",
                "resolution": "A real resolution",
                "successful": False,
                "resolution_time_minutes": 10,
                "lessons_learned": "A real lesson",
            },
        )
        assert response.status_code == 502
        assert response.json()["memory_stored"] is False