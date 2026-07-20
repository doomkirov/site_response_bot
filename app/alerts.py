from datetime import datetime
from zoneinfo import ZoneInfo

from app.checker import send_text_to_chat
from db_operations.incidents_dao import IncidentsDAO


REMINDER_DELAY_SECONDS = 60 * 60
MOSCOW_TZ = ZoneInfo("Europe/Moscow")


def _incident_description(incident) -> str:
    status_code = incident.confirmed_status_code or incident.status_code
    description = incident.confirmed_description or incident.description
    return f"{status_code}. {description.rstrip('.')}"


def build_error_message(incidents) -> str:
    rows = []
    for incident in incidents:
        rows.append(
            f"• [URL={incident.url}]{incident.url}[/URL][BR]"
            f"Код: {_incident_description(incident)}. Сайт недоступен в течение 5 минут"
        )
    return "[BR]".join(rows)


def build_reminder_message(incidents) -> str:
    return "[BR]".join(
        f"• [URL={incident.url}]{incident.url}[/URL][BR]"
        f"Код: {_incident_description(incident)}. Сайт недоступен в течение 60 минут"
        for incident in incidents
    )


def build_recovery_message(recovered, still_unavailable) -> str:
    rows = [
        f"• [URL={incident.url}]{incident.url}[/URL][BR]"
        f"Доступность восстановлена в "
        f"{datetime.fromtimestamp(incident.recovered_at, tz=MOSCOW_TZ):%d.%m.%Y %H:%M:%S}."
        for incident in recovered
    ]
    if still_unavailable:
        rows.append("")
        rows.append("[B]Всё ещё недоступны:[/B]")
        rows.extend(
            f"• [URL={incident.url}]{incident.url}[/URL] — {_incident_description(incident)}"
            for incident in still_unavailable
        )
    return "[BR]".join(rows)


async def send_pending_alerts(timestamp: int) -> None:
    incidents = await IncidentsDAO.get_pending_alerts()
    if incidents and await send_text_to_chat(build_error_message(incidents)):
        await IncidentsDAO.mark_alerts_sent([incident.id for incident in incidents], timestamp)

    reminders = await IncidentsDAO.get_pending_reminders(timestamp, REMINDER_DELAY_SECONDS)
    if reminders and await send_text_to_chat(build_reminder_message(reminders)):
        await IncidentsDAO.mark_reminders_sent([incident.id for incident in reminders], timestamp)

    recoveries = await IncidentsDAO.get_pending_recoveries()
    if recoveries:
        open_incidents = await IncidentsDAO.get_open_incidents()
        if await send_text_to_chat(build_recovery_message(recoveries, open_incidents)):
            await IncidentsDAO.mark_recoveries_sent([incident.id for incident in recoveries], timestamp)
