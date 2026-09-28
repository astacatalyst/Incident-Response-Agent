import json

import httpx
import pytest

from backend.app.config import Settings
from backend.app.llm.groq_client import GroqClient
from backend.app.memory.hindsight_client import HindsightClient


@pytest.mark.asyncio
async def test_hindsight_client_uses_documented_recall_and_retain_api():
    calls = []

    async def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        if request.url.path.endswith("/recall"):
            return httpx.Response(
                200,
                json={
                    "results": [
                        {
                            "id": "memory-7",
                            "text": "A real prior incident experience",
                            "type": "experience",
                            "document_id": "incident-7",
                            "scores": {"final": 0.8},
                        }
                    ]
                },
            )
        return httpx.Response(200, json={"success": True, "items_count": 1, "bank_id": "bank"})

    settings = Settings(
        HINDSIGHT_API_URL="https://hindsight.example",
        HINDSIGHT_API_KEY="secret-for-test",
        HINDSIGHT_BANK_ID="bank",
    )
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        hindsight = HindsightClient(settings, client=client)
        recall = await hindsight.recall("payment database latency")
        retain = await hindsight.retain("resolved incident", incident_id=7, tags=["service:payment-api"])

    assert calls[0].method == "POST"
    assert calls[0].url.path == "/v1/default/banks/bank/memories/recall"
    assert json.loads(calls[0].content)["query"] == "payment database latency"
    assert recall.memories[0]["id"] == "memory-7"
    assert calls[1].url.path == "/v1/default/banks/bank/memories"
    assert json.loads(calls[1].content)["items"][0]["document_id"] == "incident-7"
    assert retain.success is True


@pytest.mark.asyncio
async def test_groq_client_uses_structured_output_contract():
    calls = []

    async def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "summary": "Database saturation is likely.",
                                    "likely_root_cause": "Query plan regression.",
                                    "confidence": "medium",
                                    "evidence": ["db_cpu=96"],
                                    "recommended_actions": [{"step": "Inspect plans", "reason": "Validate the hypothesis."}],
                                    "similar_incidents": [],
                                    "memory_insights": [],
                                    "uncertainties": ["The active plan is not available."],
                                }
                            )
                        }
                    }
                ]
            },
        )

    settings = Settings(GROQ_API_KEY="test-key", GROQ_MODEL="test-model")
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        groq = GroqClient(settings, client=client)
        analysis = await groq.analyze({"service": "payment-api"}, [])

    payload = json.loads(calls[0].content)
    assert calls[0].url.path == "/openai/v1/chat/completions"
    assert payload["model"] == "test-model"
    assert payload["response_format"]["type"] == "json_schema"
    assert analysis.confidence == "medium"