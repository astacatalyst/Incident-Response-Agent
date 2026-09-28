import pytest


@pytest.mark.asyncio
async def test_health_endpoint(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "database": "ok",
        "hindsight": "ok",
        "llm": "ok",
    }


@pytest.mark.asyncio
async def test_docs_available(client):
    response = await client.get("/docs")
    assert response.status_code == 200
    assert "IncidentIQ Backend" in response.text