from dataclasses import dataclass
from typing import Any

import httpx

from backend.app.config import Settings


class HindsightError(RuntimeError):
    def __init__(self, message: str, *, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class HindsightNotConfigured(HindsightError):
    pass


@dataclass
class HindsightRecall:
    memories: list[dict[str, Any]]
    raw: dict[str, Any]


@dataclass
class HindsightRetain:
    success: bool
    raw: dict[str, Any]


class HindsightClient:
    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None):
        self.settings = settings
        self._client = client

    def _require_config(self) -> tuple[str, str | None]:
        if not self.settings.hindsight_api_url or not self.settings.hindsight_bank_id:
            raise HindsightNotConfigured(
                "HINDSIGHT_API_URL and HINDSIGHT_BANK_ID are required for Hindsight"
            )
        return self.settings.hindsight_api_url.rstrip("/"), self.settings.hindsight_api_key

    def _url(self, suffix: str) -> str:
        base, _ = self._require_config()
        if base.endswith("/v1/default"):
            return f"{base}/banks/{self.settings.hindsight_bank_id}{suffix}"
        return f"{base}/v1/default/banks/{self.settings.hindsight_bank_id}{suffix}"

    def _headers(self) -> dict[str, str]:
        _, key = self._require_config()
        return {"Authorization": f"Bearer {key}"} if key else {}

    async def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        client = self._client
        owns_client = client is None
        if owns_client:
            client = httpx.AsyncClient(timeout=self.settings.request_timeout_seconds)
        try:
            response = await client.request(method, url, headers=self._headers(), **kwargs)
        except httpx.TimeoutException as exc:
            raise HindsightError("Hindsight request timed out") from exc
        except httpx.HTTPError as exc:
            raise HindsightError(f"Hindsight request failed: {exc}") from exc
        finally:
            if owns_client:
                await client.aclose()
        if response.status_code >= 400:
            detail = response.text[:500]
            raise HindsightError(
                f"Hindsight returned HTTP {response.status_code}: {detail}",
                status_code=response.status_code,
            )
        return response

    async def health(self) -> dict[str, Any]:
        if not self.settings.hindsight_api_url or not self.settings.hindsight_bank_id:
            return {"status": "not_configured"}
        base = self.settings.hindsight_api_url.rstrip("/")
        try:
            response = await self._request("GET", f"{base}/health")
            return {"status": "ok", "response": response.json()}
        except HindsightError as exc:
            return {"status": "unavailable", "error": str(exc)}

    async def recall(self, query: str) -> HindsightRecall:
        payload = {
            "query": query,
            "types": ["world", "experience", "observation"],
            "prefer_observations": True,
            "budget": "mid",
            "max_tokens": 4096,
        }
        response = await self._request(
            "POST",
            self._url("/memories/recall"),
            json=payload,
        )
        try:
            raw = response.json()
        except ValueError as exc:
            raise HindsightError("Hindsight recall returned invalid JSON") from exc
        memories = []
        for result in raw.get("results", []):
            scores = result.get("scores")
            memories.append(
                {
                    "id": result.get("id"),
                    "content": result.get("text", ""),
                    "source": result.get("document_id") or result.get("id"),
                    "metadata": {
                        key: value
                        for key, value in {
                            "document_id": result.get("document_id"),
                            "context": result.get("context"),
                            "type": result.get("type"),
                            "tags": result.get("tags"),
                            "occurred_start": result.get("occurred_start"),
                            "occurred_end": result.get("occurred_end"),
                            "mentioned_at": result.get("mentioned_at"),
                        }.items()
                        if value is not None
                    },
                    "scores": scores if isinstance(scores, dict) else None,
                    "type": result.get("type"),
                }
            )
        return HindsightRecall(memories=memories[: self.settings.max_recall_memories], raw=raw)

    async def retain(self, content: str, *, incident_id: int, tags: list[str]) -> HindsightRetain:
        payload = {
            "items": [
                {
                    "content": content,
                    "context": "IncidentIQ resolved incident experience",
                    "document_id": f"incident-{incident_id}",
                    "tags": tags,
                }
            ],
            "async": False,
        }
        response = await self._request("POST", self._url("/memories"), json=payload)
        try:
            raw = response.json()
        except ValueError as exc:
            raise HindsightError("Hindsight retain returned invalid JSON") from exc
        return HindsightRetain(success=raw.get("success") is True, raw=raw)

    async def stats(self) -> dict[str, Any]:
        response = await self._request("GET", self._url("/stats"))
        try:
            return response.json()
        except ValueError as exc:
            raise HindsightError("Hindsight stats returned invalid JSON") from exc