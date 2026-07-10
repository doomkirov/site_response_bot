from app.checker import send_text_to_chat
from db_operations.incidents_dao import IncidentsDAO


def _incident_description(incident) -> str:
    text = f"{incident.status_code}. {incident.description}"
    if incident.confirmed_status_code != incident.status_code:
        text += (
            f"[BR]  Повторная проверка: {incident.confirmed_status_code}. "
            f"{incident.confirmed_description}"
        )
    return text


def build_error_message(incidents) -> str:
    rows = ["[B]Обнаружены подтверждённые проблемы:[/B]"]
    for incident in incidents:
        rows.append(f"• [URL={incident.url}]{incident.url}[/URL][BR]  {_incident_description(incident)}")
    return "[BR]".join(rows)


def build_recovery_message(recovered, still_unavailable) -> str:
    rows = ["[B]Восстановили доступность:[/B]"]
    rows.extend(f"• [URL={incident.url}]{incident.url}[/URL]" for incident in recovered)
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

    recoveries = await IncidentsDAO.get_pending_recoveries()
    if recoveries:
        open_incidents = await IncidentsDAO.get_open_incidents()
        if await send_text_to_chat(build_recovery_message(recoveries, open_incidents)):
            await IncidentsDAO.mark_recoveries_sent([incident.id for incident in recoveries], timestamp)
