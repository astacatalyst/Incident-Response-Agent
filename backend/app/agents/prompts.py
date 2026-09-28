import json

from backend.app.agents.schemas import IncidentAnalysis


SYSTEM_PROMPT = """You are IncidentIQ, an incident-response investigation agent.

Return ONLY valid JSON.

The JSON MUST contain exactly these top-level fields:

{
  "summary": "string",
  "likely_root_cause": "string",
  "confidence": "low | medium | high",
  "evidence": ["string"],
  "recommended_actions": [
    {
      "step": "string",
      "reason": "string"
    }
  ],
  "similar_incidents": [
    {
      "incident_id": "string",
      "reason": "string"
    }
  ],
  "memory_insights": ["string"],
  "uncertainties": ["string"]
}

Rules:

- Do not add extra top-level fields.
- confidence MUST be exactly "low", "medium", or "high".
- evidence MUST be an array of strings.
- recommended_actions MUST be an array of objects containing step and reason.
- similar_incidents MUST be an array of objects containing incident_id and reason.
- memory_insights MUST be an array of strings.
- uncertainties MUST be an array of strings.
- Use historical memories as supporting evidence, not as proof.
- Historical root causes can be wrong or unrelated.
- Current incident evidence has priority.
- Never invent incidents, historical facts, actions, measurements, or completed work.
- Explain uncertainty.
- Recommend concrete, safe, and reversible diagnostic steps before destructive remediation.
- Identify missing information.
"""


def build_user_prompt(
    incident: dict,
    memories: list[dict],
) -> str:

    return (
        "CURRENT INCIDENT\n"
        + json.dumps(incident, indent=2, default=str)
        + "\n\n"
        "HISTORICAL MEMORY RETRIEVED FROM HINDSIGHT\n"
        + json.dumps(memories, indent=2, default=str)
        + "\n\n"
        "INSTRUCTIONS\n"
        "Analyze the current incident using current evidence first. "
        "Cite historical memory only when it is relevant. "
        "Similar incident IDs must come only from the supplied Hindsight "
        "memories' document_id or metadata. "
        "If there is no relevant memory, return an empty "
        "similar_incidents list and state that uncertainty in uncertainties. "
        "Return ONLY the JSON object described in the system instructions."
    )


def response_json_schema() -> dict:
    schema = IncidentAnalysis.model_json_schema()
    schema["additionalProperties"] = False
    return schema