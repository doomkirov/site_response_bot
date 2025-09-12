from aiogram import F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup

from app.app_support.response_data_class import ResponseData
from app.app_support.return_time import format_unix_utc_plus3
from app.checker import validate_data
from bot_operations.bot_support.base_router import commands_router
from bot_operations.bot_support.keyboards import back_to_links_actions_keyboard, get_single_link_operations_keyboard
from db_operations.all_models import LinksModel
from db_operations.links_dao.links_dao import LinksDAO
from db_operations.user_dao.user_dao import UserDAO


@commands_router.callback_query(F.data.startswith('link_structure_url:'))
async def link_structure_url(callback: CallbackQuery):
    prefix = 'link_structure_url:'
    url, next_from_id = callback.data[len(prefix):].split('~~|~~', 1)
    url_object: LinksModel = await LinksDAO.find_one_or_none(url=url)
    if not url_object:
        await callback.message.edit_text(
            f'Произошла ошибка при обработке ссылки {url}\n'
            f'Свяжитесь с разработчиком',
            reply_markup=back_to_links_actions_keyboard
        )
        return
    url_data: ResponseData = ResponseData(url, url_object.last_status)
    response_text = (
        f'Страница - {url}\n\n'
        f'Последний статус - {url_object.last_status if url_object.last_status != 0 else 'Нет данных'}\n'
        f'{url_data.get_status_explanation()}\n'
        f'Время последней проверки - '
        f'{format_unix_utc_plus3(url_object.last_checked) if url_object.last_checked != 0 else 'Нет данных'}\n\n'
        f'{f'Последняя полученная ошибка - {url_object.last_error_status}\n' if url_object.last_status not in (url_object.last_error_status, 0) else ''}'
        f'{f'Описание последней полученной ошибки - {url_data.get_status_explanation(status_code=url_object.last_error_status)}\n' if url_object.last_status not in (url_object.last_error_status, 0) else ''}'
        f'{f'Время последней ошибки - {format_unix_utc_plus3(url_object.last_error_time)}\n\n' if url_object.last_error_time != url_object.last_checked else ''}'
        f'{f'Время последнего успешного (200) статуса - {format_unix_utc_plus3(url_object.last_success_time) if url_object.last_success_time != 0 else 'Нет данных'}' if url_object.last_success_time not in (url_object.last_checked, 0) else ''}'
    )
    await callback.message.edit_text(
        response_text,
        reply_markup=get_single_link_operations_keyboard(url, next_from_id),
        disable_web_page_preview=False
    )


@commands_router.callback_query(F.data.startswith('retry_status_for:'))
async def retry_status_for(callback_query: CallbackQuery):
    prefix = 'retry_status_for:'
    url = callback_query.data[len(prefix):]
    links_object: LinksModel = await LinksDAO.find_one_or_none(url=url)
    await validate_data(links_object, user_bulk_id=callback_query.from_user.id)

@commands_router.callback_query(F.data.startswith('delete_link:'))
async def delete_link(callback_query: CallbackQuery):
    prefix = 'delete_link:'
    url = callback_query.data[len(prefix):]
    user_id = callback_query.from_user.id
    await UserDAO.delete_link(user_id=user_id, url=url)
    await LinksDAO.cleanup_orphan_links()
    await callback_query.message.edit_text(
        f'Ссылка {url} удалена!',
        reply_markup=back_to_links_actions_keyboard
    )