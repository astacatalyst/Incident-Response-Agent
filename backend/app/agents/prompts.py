import json

from backend.app.agents.schemas import IncidentAnalysis


SYSTEM_PROMPT = """You are IncidentIQ, an incident-response investigation agent.
Return only JSON matching the supplied schema.

Use historical memories as supporting evidence, not as proof. Historical root
causes can be wrong or unrelated; current incident evidence has priority.
Never invent incidents, historical facts, actions, measurements, or completed
work. Explain uncertainty. Recommend concrete, safe, and reversible diagnostic
steps before destructive remediation. Identify missing information.
"""


def build_user_prompt(incident: dict, memories: list[dict]) -> str:
    return (
        "CURRENT INCIDENT\n"
        + json.dumps(incident, indent=2, default=str)
        + "\n\nHISTORICAL MEMORY RETRIEVED FROM HINDSIGHT\n"
        + json.dumps(memories, indent=2, default=str)
        + "\n\nINSTRUCTIONS\n"
        "Analyze the current incident using current evidence first. Cite the "
        "historical memory only when it is relevant. Similar incident IDs must "
        "come only from the supplied Hindsight memories' document_id or metadata. "
        "If there is no relevant memory, return an empty similar_incidents list "
        "and state that uncertainty in uncertainties."
    )


def response_json_schema() -> dict:
    schema = IncidentAnalysis.model_json_schema()
    schema["additionalProperties"] = False
    return schema