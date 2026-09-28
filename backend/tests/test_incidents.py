import pytest


@pytest.mark.asyncio
async def test_validation_and_incident_creation(client, incident_payload):
    invalid = {**incident_payload, "severity": "urgent"}
    assert (await client.post("/api/incidents/analyze", json=invalid)).status_code == 422

    response = await client.post("/api/incidents/analyze", json=incident_payload)
    assert response.status_code == 201
    body = response.json()
    assert body["incident"]["id"] == 1
    assert body["incident"]["status"] == "open"


@pytest.mark.asyncio
async def test_retrieval_filtering_and_pagination(client, incident_payload):
    for service in ("payment-api", "auth-service", "payment-api"):
        await client.post("/api/incidents/analyze", json={**incident_payload, "service": service})
    response = await client.get("/api/incidents", params={"service": "payment-api", "page_size": 1})
    assert response.status_code == 200
    assert response.json()["total"] == 2
    assert len(response.json()["items"]) == 1
    assert (await client.get("/api/incidents/999")).status_code == 404