from datetime import datetime, timezone

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from backend.app.db.models import Incident


class IncidentRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, data: dict) -> Incident:
        incident = Incident(**data)
        self.session.add(incident)
        self.session.commit()
        self.session.refresh(incident)
        return incident

    def get(self, incident_id: int) -> Incident | None:
        return self.session.get(Incident, incident_id)

    def list(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        service: str | None = None,
        severity: str | None = None,
        status: str | None = None,
    ) -> tuple[list[Incident], int]:
        query: Select = select(Incident)
        count_query: Select = select(func.count()).select_from(Incident)
        filters = []
        if service:
            filters.append(Incident.service == service)
        if severity:
            filters.append(Incident.severity == severity)
        if status:
            filters.append(Incident.status == status)
        if filters:
            query = query.where(*filters)
            count_query = count_query.where(*filters)
        total = self.session.scalar(count_query) or 0
        incidents = list(
            self.session.scalars(
                query.order_by(Incident.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
            )
        )
        return incidents, total

    def update(self, incident: Incident, values: dict) -> Incident:
        for key, value in values.items():
            setattr(incident, key, value)
        self.session.commit()
        self.session.refresh(incident)
        return incident

    def resolve(self, incident: Incident, values: dict) -> Incident:
        values = {**values, "status": "resolved", "resolved_at": datetime.now(timezone.utc)}
        return self.update(incident, values)

    def summary(self) -> dict:
        total = self.session.scalar(select(func.count()).select_from(Incident)) or 0
        resolved = self.session.scalar(
            select(func.count()).select_from(Incident).where(Incident.status == "resolved")
        ) or 0
        successful = self.session.scalar(
            select(func.count()).select_from(Incident).where(Incident.successful.is_(True))
        ) or 0
        unsuccessful = self.session.scalar(
            select(func.count()).select_from(Incident).where(Incident.successful.is_(False))
        ) or 0
        services = list(self.session.scalars(select(Incident.service).distinct().order_by(Incident.service)))
        root_cause_rows = self.session.execute(
            select(Incident.root_cause, func.count())
            .where(Incident.root_cause.is_not(None))
            .group_by(Incident.root_cause)
            .order_by(func.count().desc())
        ).all()
        recent = list(
            self.session.scalars(
                select(Incident)
                .where(Incident.status == "resolved")
                .order_by(Incident.resolved_at.desc())
                .limit(10)
            )
        )
        return {
            "incident_count": total,
            "resolved_incident_count": resolved,
            "successful_resolutions": successful,
            "unsuccessful_resolutions": unsuccessful,
            "services": services,
            "recurring_root_causes": [
                {"root_cause": root_cause, "count": count} for root_cause, count in root_cause_rows
            ],
            "recent_resolved": recent,
        }