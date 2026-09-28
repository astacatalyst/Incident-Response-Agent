import argparse
import sys

from sqlalchemy import delete

from backend.app.config import get_settings
from backend.app.db.database import Base, build_engine, build_session_factory, init_db
from backend.app.db.models import Incident
from backend.app.db.seed_data import synthetic_incidents


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed IncidentIQ's SQLite database with synthetic incidents.")
    parser.add_argument("--reset", action="store_true", help="Delete existing incidents before seeding.")
    args = parser.parse_args()
    settings = get_settings()
    engine = build_engine(settings.effective_database_url)
    init_db(engine)
    session_factory = build_session_factory(engine)
    with session_factory() as session:
        if args.reset:
            session.execute(delete(Incident))
            session.commit()
        existing = session.query(Incident).count()
        if existing:
            print(f"Database already contains {existing} incidents; use --reset to replace them.")
            return 0
        session.add_all([Incident(**record) for record in synthetic_incidents()])
        session.commit()
    print(f"Seeded {len(synthetic_incidents())} synthetic incidents into {settings.effective_database_url}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())