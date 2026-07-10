from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from app.checker import send_text_to_chat
from db_operations.incidents_dao import DailyReportsDAO, IncidentsDAO


MOSCOW_TZ = ZoneInfo("Europe/Moscow")
NIGHT_START = time(hour=18)
REPORT_TIME = time(hour=8)


def _format_time(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp, tz=MOSCOW_TZ).strftime("%d.%m.%Y %H:%M:%S")


def build_nightly_report_message(incidents, period_start: datetime, period_end: datetime) -> str:
    header = (
        "[B]Отчёт по доступности сайтов[/B][BR]"
        f"Период: {period_start:%d.%m.%Y %H:%M} — {period_end:%d.%m.%Y %H:%M}"
    )
    if not incidents:
        return f"{header}[BR][BR]Проблем в этом периоде не было. Все сайты были доступны."

    rows = [header, "", "[B]Зафиксированные проблемы:[/B]"]
    for incident in incidents:
        rows.append(
            f"• [URL={incident.url}]{incident.url}[/URL] был недоступен с {_format_time(incident.started_at)}."
        )
        rows.append(f"  Код: {incident.status_code}. {incident.description}")
        if incident.confirmed_status_code and incident.confirmed_status_code != incident.status_code:
            rows.append(
                f"  Повторная проверка: {incident.confirmed_status_code}. "
                f"{incident.confirmed_description}"
            )
        if incident.recovered_at is None or incident.recovered_at > int(period_end.timestamp()):
            rows.append("  На момент отчёта сайт всё ещё недоступен.")
        else:
            rows.append(f"  Доступность восстановлена в {_format_time(incident.recovered_at)}.")
    return "[BR]".join(rows)


async def send_nightly_report_if_due(now: datetime | None = None) -> bool:
    now = now or datetime.now(MOSCOW_TZ)
    if now.timetz().replace(tzinfo=None) < REPORT_TIME:
        return False

    report_date = now.date()
    if await DailyReportsDAO.was_sent(report_date):
        return False

    period_start = datetime.combine(report_date - timedelta(days=1), NIGHT_START, tzinfo=MOSCOW_TZ)
    incidents = await IncidentsDAO.get_incidents_for_period(
        int(period_start.timestamp()),
        int(now.timestamp()),
    )
    message = build_nightly_report_message(incidents, period_start, now)
    if not await send_text_to_chat(message):
        return False

    return await DailyReportsDAO.mark_sent(report_date, int(now.timestamp()))
