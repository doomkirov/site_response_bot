from datetime import date

from sqlalchemy import and_, or_, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from db_operations.all_models import DailyReportModel, SiteIncidentModel
from settings.database import async_session_maker


class IncidentsDAO:
    @staticmethod
    async def open_incident(**data) -> SiteIncidentModel | None:
        async with async_session_maker() as session:
            existing = await session.execute(
                select(SiteIncidentModel).where(
                    SiteIncidentModel.link_id == data["link_id"],
                    SiteIncidentModel.recovered_at.is_(None),
                )
            )
            if existing.scalar_one_or_none() is not None:
                return None

            incident = SiteIncidentModel(**data)
            session.add(incident)
            await session.commit()
            await session.refresh(incident)
            return incident

    @staticmethod
    async def confirm_open_incident(
        *, link_id: int, confirmed_at: int, status_code: int, description: str, alert_suppressed: bool
    ) -> SiteIncidentModel | None:
        async with async_session_maker() as session:
            result = await session.execute(
                select(SiteIncidentModel).where(
                    SiteIncidentModel.link_id == link_id,
                    SiteIncidentModel.recovered_at.is_(None),
                    SiteIncidentModel.confirmed_at.is_(None),
                )
            )
            incident = result.scalar_one_or_none()
            if incident is None:
                return None

            incident.confirmed_at = confirmed_at
            incident.confirmed_status_code = status_code
            incident.confirmed_description = description
            incident.alert_suppressed = alert_suppressed
            await session.commit()
            return incident

    @staticmethod
    async def close_open_incident(*, link_id: int, recovered_at: int) -> SiteIncidentModel | None:
        async with async_session_maker() as session:
            result = await session.execute(
                select(SiteIncidentModel)
                .where(SiteIncidentModel.link_id == link_id, SiteIncidentModel.recovered_at.is_(None))
                .order_by(SiteIncidentModel.started_at.desc())
            )
            incident = result.scalar_one_or_none()
            if incident is None:
                return None

            incident.recovered_at = recovered_at
            await session.commit()
            return incident

    @staticmethod
    async def get_pending_alerts() -> list[SiteIncidentModel]:
        async with async_session_maker() as session:
            result = await session.execute(
                select(SiteIncidentModel).where(
                    SiteIncidentModel.confirmed_at.is_not(None),
                    SiteIncidentModel.alert_sent_at.is_(None),
                    SiteIncidentModel.alert_suppressed.is_(False),
                    SiteIncidentModel.recovered_at.is_(None),
                )
            )
            return list(result.scalars().all())

    @staticmethod
    async def mark_alerts_sent(incident_ids: list[int], sent_at: int) -> None:
        if not incident_ids:
            return
        async with async_session_maker() as session:
            result = await session.execute(
                select(SiteIncidentModel).where(SiteIncidentModel.id.in_(incident_ids))
            )
            for incident in result.scalars():
                incident.alert_sent_at = sent_at
            await session.commit()

    @staticmethod
    async def get_pending_recoveries() -> list[SiteIncidentModel]:
        async with async_session_maker() as session:
            result = await session.execute(
                select(SiteIncidentModel).where(
                    SiteIncidentModel.recovered_at.is_not(None),
                    SiteIncidentModel.alert_sent_at.is_not(None),
                    SiteIncidentModel.recovery_sent_at.is_(None),
                )
            )
            return list(result.scalars().all())

    @staticmethod
    async def mark_recoveries_sent(incident_ids: list[int], sent_at: int) -> None:
        if not incident_ids:
            return
        async with async_session_maker() as session:
            result = await session.execute(
                select(SiteIncidentModel).where(SiteIncidentModel.id.in_(incident_ids))
            )
            for incident in result.scalars():
                incident.recovery_sent_at = sent_at
            await session.commit()

    @staticmethod
    async def get_open_incidents() -> list[SiteIncidentModel]:
        async with async_session_maker() as session:
            result = await session.execute(
                select(SiteIncidentModel)
                .where(SiteIncidentModel.recovered_at.is_(None))
                .order_by(SiteIncidentModel.started_at)
            )
            return list(result.scalars().all())

    @staticmethod
    async def get_incidents_for_period(started_at: int, ended_at: int) -> list[SiteIncidentModel]:
        async with async_session_maker() as session:
            result = await session.execute(
                select(SiteIncidentModel)
                .where(
                    SiteIncidentModel.started_at <= ended_at,
                    or_(
                        SiteIncidentModel.recovered_at.is_(None),
                        SiteIncidentModel.recovered_at >= started_at,
                    ),
                )
                .order_by(SiteIncidentModel.started_at)
            )
            return list(result.scalars().all())


class DailyReportsDAO:
    @staticmethod
    async def was_sent(report_date: date) -> bool:
        async with async_session_maker() as session:
            result = await session.execute(
                select(DailyReportModel.id).where(DailyReportModel.report_date == report_date.isoformat())
            )
            return result.scalar_one_or_none() is not None

    @staticmethod
    async def mark_sent(report_date: date, sent_at: int) -> bool:
        async with async_session_maker() as session:
            statement = (
                pg_insert(DailyReportModel)
                .values(report_date=report_date.isoformat(), sent_at=sent_at)
                .on_conflict_do_nothing(index_elements=["report_date"])
            )
            result = await session.execute(statement)
            await session.commit()
            return result.rowcount == 1
