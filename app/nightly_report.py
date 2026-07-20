from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from app.checker import send_text_to_chat
from db_operations.incidents_dao import DailyReportsDAO, IncidentsDAO
from db_operations.links_dao.links_dao import LinksDAO


MOSCOW_TZ = ZoneInfo("Europe/Moscow")
REPORT_TIME = time(hour=9)


def _format_time(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp, tz=MOSCOW_TZ).strftime("%d.%m.%Y %H:%M:%S")


def _format_duration(started_at: int, recovered_at: int) -> str:
    minutes = max(1, round((recovered_at - started_at) / 60))
    return f"{minutes} мин."


def build_nightly_report_message(links, incidents, period_start: datetime, period_end: datetime) -> str:
    header = (
        "[B]Отчёт по доступности сайтов[/B][BR]"
        f"Период: {period_start:%d.%m.%Y %H:%M} — {period_end:%d.%m.%Y %H:%M}"
    )
    incidents_by_link = {}
    for incident in incidents:
        incidents_by_link.setdefault(incident.link_id, []).append(incident)

    rows = [header, ""]
    period_end_timestamp = int(period_end.timestamp())
    for link in links:
        link_incidents = incidents_by_link.get(link.id, [])
        if not link_incidents:
            rows.append(f"• ✅ [URL={link.url}]{link.url}[/URL]")
            continue

        rows.append(f"• ❌ [URL={link.url}]{link.url}[/URL]")
        for incident in link_incidents:
            ended_at = min(incident.recovered_at or period_end_timestamp, period_end_timestamp)
            started_at = max(incident.started_at, int(period_start.timestamp()))
            status_code = incident.confirmed_status_code or incident.status_code
            description = (incident.confirmed_description or incident.description).rstrip(".")
            rows.append(
                f"  Код: {status_code}. {description} Недоступен {_format_duration(started_at, ended_at)}, "
                f"с {_format_time(started_at)} по {_format_time(ended_at)}."
            )
    return "[BR]".join(rows)


async def send_nightly_report_if_due(now: datetime | None = None) -> bool:
    now = now or datetime.now(MOSCOW_TZ)
    if now.timetz().replace(tzinfo=None) < REPORT_TIME:
        return False

    report_date = now.date()
    if await DailyReportsDAO.was_sent(report_date):
        return False

    period_end = datetime.combine(report_date, REPORT_TIME, tzinfo=MOSCOW_TZ)
    period_start = period_end - timedelta(days=1)
    incidents = await IncidentsDAO.get_incidents_for_period(
        int(period_start.timestamp()),
        int(period_end.timestamp()),
    )
    links = await LinksDAO.find_all()
    message = build_nightly_report_message(links, incidents, period_start, period_end)
    if not await send_text_to_chat(message):
        return False

    return await DailyReportsDAO.mark_sent(report_date, int(now.timestamp()))
