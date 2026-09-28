import json
from typing import Any

import httpx

from backend.app.agents.prompts import SYSTEM_PROMPT, build_user_prompt, response_json_schema
from backend.app.agents.schemas import IncidentAnalysis
from backend.app.config import Settings
from backend.app.memory.hindsight_client import HindsightError


class GroqError(RuntimeError):
    def __init__(self, message: str, *, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class GroqNotConfigured(GroqError):
    pass


class GroqClient:
    base_url = "https://api.groq.com/openai/v1"

    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None):
        self.settings = settings
        self._client = client

    def _require_key(self) -> str:
        if not self.settings.groq_api_key:
            raise GroqNotConfigured("GROQ_API_KEY is required for Groq")
        return self.settings.groq_api_key

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._require_key()}",
            "Content-Type": "application/json",
        }

    async def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        client = self._client
        owns_client = client is None
        if owns_client:
            client = httpx.AsyncClient(timeout=self.settings.request_timeout_seconds)
        try:
            response = await client.request(method, url, headers=self._headers(), **kwargs)
        except httpx.TimeoutException as exc:
            raise GroqError("Groq request timed out") from exc
        except httpx.HTTPError as exc:
            raise GroqError(f"Groq request failed: {exc}") from exc
        finally:
            if owns_client:
                await client.aclose()
        if response.status_code >= 400:
            detail = response.text[:500]
            raise GroqError(
                f"Groq returned HTTP {response.status_code}: {detail}",
                status_code=response.status_code,
            )
        return response

    async def health(self) -> dict[str, Any]:
        if not self.settings.groq_api_key:
            return {"status": "not_configured"}
        try:
            response = await self._request("GET", f"{self.base_url}/models")
            return {"status": "ok", "response": response.json()}
        except GroqError as exc:
            return {"status": "unavailable", "error": str(exc)}

    async def analyze(self, incident: dict[str, Any], memories: list[dict[str, Any]]) -> IncidentAnalysis:
        payload = {
            "model": self.settings.groq_model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(incident, memories)},
            ],
            "temperature": 0.1,
            "max_completion_tokens": 2048,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "incident_analysis",
                    "strict": True,
                    "schema": response_json_schema(),
                },
            },
        }
        response = await self._request(
            "POST",
            f"{self.base_url}/chat/completions",
            json=payload,
        )
        try:
            body = response.json()
            content = body["choices"][0]["message"]["content"]
            parsed = json.loads(content)
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise GroqError("Groq returned a malformed structured response") from exc
        try:
            return IncidentAnalysis.model_validate(parsed)
        except Exception as exc:
            raise GroqError("Groq response failed IncidentAnalysis validation") from exc