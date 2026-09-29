"""Seed data: 25 real, publicly documented production incidents.

Each record is summarised from the company's published postmortem (URL kept in
metrics["source"]). Log lines are reconstructed from the report text, since raw
logs are not public. Durations are approximate, taken from the reports.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

DATA_FILE = Path(__file__).with_name("real_incidents.json")


def real_incidents() -> list[dict]:
    rows = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    records = []
    for r in rows:
        created = datetime.fromisoformat(r["date"].replace("Z", "+00:00"))
        logs = "\n".join(
            [f"[reconstructed from public postmortem: {r['source']}]"]
            + [f"ALERT {r['service']}: {s}" for s in r["symptoms"]]
        )
        records.append(
            {
                "service": r["service"],
                "severity": r["severity"],
                "symptoms": r["symptoms"],
                "logs": logs,
                "metrics": {"company": r["company"], "source": r["source"]},
                "deployment_version": "public-postmortem",
                "description": f"{r['company']}: {r['description']}",
                "status": "resolved",
                "root_cause": r["root_cause"],
                "resolution": r["resolution"],
                "successful": True,
                "resolution_time_minutes": r["minutes"],
                "lessons_learned": r["lessons"],
                "is_synthetic": True,  # marks seed data; content itself is real
                "created_at": created,
                "resolved_at": created + timedelta(minutes=r["minutes"]),
            }
        )
    return records


# Backwards-compatible name used by seeding scripts.
synthetic_incidents = real_incidents
