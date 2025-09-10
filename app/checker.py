import asyncio

import aiohttp, ssl, time
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

from app.app_support.response_data_class import ResponseData
from db_operations.all_models import LinksModel
from db_operations.links_dao.links_dao import LinksDAO
from db_operations.user_dao.user_dao import UserDAO
from logger.log_decorator import log_execution_time


async def send_user_message(user_id: int, data: ResponseData):
    from bot_operations.bot_main import bot
    try:
        await bot.send_message(
            user_id,
            f'Статус-код ответа у сайта {data.url} изменился!\n'
            f'Новый код - {data.status_code}\n\n'
            f'{data.explanation}',
            disable_web_page_preview=True
        )
        print(f"Пользователь {user_id} доступен ✅")
        return True
    except TelegramForbiddenError:
        # Бот заблокирован пользователем
        print(f"Пользователь {user_id} заблокировал бота ❌")
        await UserDAO.change_value_in_row('id', user_id, send_notifications=0)
        return False
    except TelegramBadRequest as e:
        # Например, если пользователь удалил аккаунт
        print(f"Проблема с пользователем {user_id}: {e}")
        await UserDAO.change_value_in_row('id', user_id, send_notifications=0)
        return False
    except Exception as e:
        # Любая другая ошибка
        print(f"Не удалось отправить сообщение: {e}")
        return False

@log_execution_time
async def get_status_code(url: str):
    timeout = aiohttp.ClientTimeout(total=15)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                await response.release()
                status_code = response.status
                return ResponseData(url, status_code)
    except aiohttp.ClientConnectorCertificateError as e:
        # Ошибка валидации сертификата
        return ResponseData(url, status_code=900,
                            explanation = str(e))
    except aiohttp.ClientConnectorSSLError as e:
        return ResponseData(url, status_code=901,
                            explanation = str(e))
    except ssl.SSLCertVerificationError as e:
        return ResponseData(url, status_code=902,
                            explanation = str(e))
    except asyncio.TimeoutError:
        # Ошибка по Тайм-Аут
        return ResponseData(url, status_code=903)
    except Exception as e:
        return ResponseData(url, status_code=999,
                            explanation = str(e))

async def validate_data(url: str):
    data: ResponseData = await get_status_code(url)
    timestamp = time.time()
    links_object: LinksModel = await LinksDAO.find_one_or_none(url=url)
    last_success_time = links_object.last_success_time
    last_error_status = links_object.last_error_status
    last_error_time = links_object.last_error_time
    all_users = links_object.users
    if not all_users:
        await LinksDAO.delete_row('url', url)
        return
    user_ids = [user.id for user in all_users if getattr(user, "send_results", 0) == 1]
    tasks: list = []
    if data.status_code not in (0, links_object.last_status):
        for user_id in user_ids:
            tasks.append(send_user_message(user_id, data))
        await asyncio.gather(*tasks)
    if data.status_code == 200:
        last_success_time = timestamp
    else:
        last_error_status = data.status_code
        last_error_time = timestamp
    await LinksDAO.update_fields_by_url_simple(
        url=url,
        last_checked=timestamp,
        last_status=data.status_code,
        last_error_status=last_error_status,
        last_error_time=last_error_time,
        last_success_time=last_success_time
    )

