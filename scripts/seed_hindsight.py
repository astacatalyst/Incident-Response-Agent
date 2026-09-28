import asyncio
import sys

from backend.app.config import get_settings
from backend.app.db.models import Incident
from backend.app.db.seed_data import synthetic_incidents
from backend.app.memory.hindsight_client import HindsightClient, HindsightError
from backend.app.memory.memory_service import build_retained_memory


async def main() -> int:
    settings = get_settings()
    client = HindsightClient(settings)
    count = 0
    for index, record in enumerate(synthetic_incidents(), start=1):
        # A transient model with the same retained fields avoids requiring the
        # SQLite seed to run first, while still using the production retain path.
        incident = Incident(id=index, **record)
        try:
            result = await client.retain(
                build_retained_memory(incident),
                incident_id=index,
                tags=[f"service:{incident.service}", f"severity:{incident.severity}"],
            )
        except HindsightError as exc:
            print(f"Retain failed for synthetic incident {index}: {exc}", file=sys.stderr)
            return 1
        if not result.success:
            print(f"Hindsight did not confirm retain for synthetic incident {index}: {result.raw}", file=sys.stderr)
            return 1
        count += 1
        print(f"Retained synthetic incident {index}: {result.raw}")
    print(f"Successfully retained {count} synthetic incidents in Hindsight.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))