import asyncio
import logging
import ssl
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import aiohttp

from app.app_support.response_data_class import ResponseData
from db_operations.all_models import LinksModel
from db_operations.incidents_dao import IncidentsDAO
from db_operations.links_dao.links_dao import LinksDAO
from settings import settings

from .utils import normalize_url


logger = logging.getLogger(__name__)
MOSCOW_TZ = ZoneInfo("Europe/Moscow")


def is_night_period(timestamp: int) -> bool:
    hour = datetime.fromtimestamp(timestamp, tz=MOSCOW_TZ).hour
    return hour >= 18 or hour < 8


async def send_text_to_chat(message: str, chat_id: str = "chat73069") -> bool:
    """Отправляет одно сообщение в чат и возвращает признак успеха."""
    url = settings.WEBHOOK_URL
    payload = {"DIALOG_ID": chat_id, "MESSAGE": message}

    async with aiohttp.ClientSession() as session:
        for attempt in range(1, 4):
            try:
                logger.debug("Отправляю сообщение в чат, попытка %d/3", attempt)
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        return True
                    logger.warning("Webhook вернул HTTP %d (попытка %d/3)", response.status, attempt)
            except aiohttp.ClientError as error:
                logger.warning("Не удалось отправить сообщение (попытка %d/3): %s", attempt, error)

            if attempt < 3:
                await asyncio.sleep(1)

    logger.error("Сообщение в чат не отправлено после 3 попыток")
    return False


async def get_status_code(url: str) -> ResponseData:
    url = normalize_url(url)
    timeout = aiohttp.ClientTimeout(total=15)
    try:
        logger.debug("Запрашиваю %s", url)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                status_code = response.status
                logger.debug("%s ответил HTTP %d", url, status_code)
                return ResponseData(url, status_code)
    except aiohttp.ClientConnectorCertificateError as error:
        logger.warning("Ошибка сертификата при запросе %s: %s", url, error)
        return ResponseData(url, status_code=900, explanation=str(error))
    except aiohttp.ClientConnectorSSLError as error:
        logger.warning("SSL-ошибка при запросе %s: %s", url, error)
        return ResponseData(url, status_code=901, explanation=str(error))
    except ssl.SSLCertVerificationError as error:
        logger.warning("Не удалось проверить SSL-сертификат %s: %s", url, error)
        return ResponseData(url, status_code=902, explanation=str(error))
    except asyncio.TimeoutError:
        logger.warning("Таймаут при запросе %s", url)
        return ResponseData(url, status_code=903)
    except Exception as error:
        logger.exception("Непредвиденная ошибка при запросе %s", url)
        return ResponseData(url, status_code=999, explanation=str(error))


async def validate_data(links_object: LinksModel):
    data = await get_status_code(links_object.url)
    timestamp = time.time()
    last_success_time = links_object.last_success_time
    last_error_status = links_object.last_error_status
    last_error_time = links_object.last_error_time
    status_changed = data.status_code not in (0, links_object.last_status)
    was_available = links_object.last_status == 200
    is_available = data.status_code == 200

    if (was_available or links_object.last_status == 0) and not is_available:
        await IncidentsDAO.open_incident(
            link_id=links_object.id,
            url=data.url,
            started_at=int(timestamp),
            status_code=data.status_code,
            description=data.explanation,
        )
        logger.info("Открыт инцидент для %s; жду повторной проверки", data.url)
    elif not is_available:
        confirmed = await IncidentsDAO.confirm_open_incident(
            link_id=links_object.id,
            confirmed_at=int(timestamp),
            status_code=data.status_code,
            description=data.explanation,
            alert_suppressed=is_night_period(int(timestamp)),
        )
        if confirmed:
            logger.info("Инцидент для %s подтверждён повторной ошибкой", data.url)
    elif not was_available and is_available:
        incident = await IncidentsDAO.close_open_incident(
            link_id=links_object.id,
            recovered_at=int(timestamp),
        )
        if incident:
            logger.info("Инцидент для %s закрыт", data.url)

    if status_changed:
        logger.info(
            "Изменился статус сайта id=%s, url=%s: %s -> %s",
            links_object.id,
            data.url,
            links_object.last_status,
            data.status_code,
        )
    if data.status_code == 200:
        last_success_time = timestamp
    else:
        logger.warning("Сайт %s недоступен: код %d", data.url, data.status_code)
        last_error_status = data.status_code
        last_error_time = timestamp

    updated_rows = await LinksDAO.update_fields_by_url_simple(
        url=links_object.url,
        last_checked=timestamp,
        last_status=data.status_code,
        last_error_status=last_error_status,
        last_error_time=last_error_time,
        last_success_time=last_success_time,
    )
    logger.debug("Обновлено строк БД для %s: %d", data.url, updated_rows)
