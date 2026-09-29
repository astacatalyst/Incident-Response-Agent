"""Answer natural-language questions about past incidents with cited evidence.

Retrieval: keyword scoring over SQLite incident records plus a Hindsight recall.
Generation: Lovable AI Gateway (OpenAI Responses API, streamed).
"""

import json
import os
import re

import httpx

GATEWAY_URL = "https://ai.gateway.lovable.dev/v1/responses"
MODEL = "openai/gpt-6-astra"
STOP = set("the a an of to in on for and or is was were what why how when which did do does with any have has our we us all past incidents incident".split())


class AskFailed(Exception):
    def __init__(self, message: str, status: int = 502):
        super().__init__(message)
        self.status = status


def _tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9_\-]{3,}", (text or "").lower()) if t not in STOP}


def _record(i) -> dict:
    return {
        "id": i.id,
        "service": i.service,
        "severity": i.severity,
        "status": i.status,
        "created_at": i.created_at.isoformat() if i.created_at else None,
        "description": i.description,
        "symptoms": i.symptoms,
        "root_cause": i.root_cause,
        "resolution": i.resolution,
        "successful": i.successful,
        "resolution_time_minutes": i.resolution_time_minutes,
        "lessons_learned": i.lessons_learned,
        "logs": (i.logs or "")[:600],
    }


def retrieve(incidents, question: str, limit: int = 8) -> list[dict]:
    q = _tokens(question)
    scored = []
    for i in incidents:
        rec = _record(i)
        hay = _tokens(" ".join(str(v) for v in rec.values() if v))
        score = len(q & hay) + (2 if i.service and i.service.lower() in question.lower() else 0)
        if score:
            scored.append((score, rec))
    scored.sort(key=lambda s: (-s[0], -(s[1]["id"])))
    return [r | {"match_score": s} for s, r in scored[:limit]]


PROMPT = """You are an incident-response analyst. Answer the responder's question using ONLY the incident records and memories provided.
Return a single JSON object, no markdown fences:
{"answer": string (2-6 sentences, direct), "confidence": "high"|"medium"|"low",
 "evidence": [{"incident_id": number, "quote": short exact phrase copied from that record, "why": one sentence}],
 "follow_up": string or null}
Cite at most 5 incidents. If the records do not answer the question, say so plainly and set confidence to "low"."""


async def ask_gateway(question: str, records: list[dict], memories: list[dict]) -> dict:
    key = os.environ.get("LOVABLE_API_KEY")
    if not key:
        raise AskFailed("LOVABLE_API_KEY is not set on the backend, so the question feature is off.", 503)
    context = json.dumps({"incidents": records, "memories": [m.get("content", m) for m in memories][:6]}, default=str)
    body = {
        "model": MODEL,
        "stream": True,
        "store": False,
        "reasoning": {"effort": "low"},
        "instructions": PROMPT,
        "input": f"Question: {question}\n\nData:\n{context}",
    }
    headers = {
        "Authorization": f"Bearer {key}",
        "Lovable-API-Key": key,
        "X-Lovable-AIG-SDK": "fetch",
        "Content-Type": "application/json",
    }
    text = ""
    async with httpx.AsyncClient(timeout=httpx.Timeout(120, connect=15)) as client:
        async with client.stream("POST", GATEWAY_URL, json=body, headers=headers) as res:
            if res.status_code != 200:
                raw = (await res.aread()).decode(errors="ignore")
                try:
                    msg = json.loads(raw).get("error", {}).get("message") or raw
                except Exception:
                    msg = raw
                if res.status_code == 402:
                    msg = "AI credits are used up. Add credits in the Lovable workspace, then try again."
                elif res.status_code == 429:
                    msg = "Too many questions at once. Wait a moment and try again."
                raise AskFailed(msg[:300], res.status_code)
            async for line in res.aiter_lines():
                if not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    break
                try:
                    evt = json.loads(data)
                except ValueError:
                    continue
                if evt.get("type") == "response.output_text.delta":
                    text += evt.get("delta", "")
                elif evt.get("type") in ("response.failed", "error"):
                    raise AskFailed("The AI could not answer this question.")
    if not text.strip():
        raise AskFailed("The AI returned no answer for this question.")
    match = re.search(r"\{.*\}", text, re.S)
    try:
        parsed = json.loads(match.group(0)) if match else {}
    except ValueError:
        parsed = {}
    if not parsed.get("answer"):
        parsed = {"answer": text.strip(), "confidence": "low", "evidence": [], "follow_up": None}
    known = {r["id"] for r in records}
    parsed["evidence"] = [e for e in parsed.get("evidence") or [] if e.get("incident_id") in known][:5]
    return parsed
