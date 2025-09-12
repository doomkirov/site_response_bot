import traceback

from aiogram import F
from aiogram.types import CallbackQuery

from bot_operations.bot_support.base_router import commands_router
from bot_operations.bot_support.keyboards import back_to_links_actions_keyboard, create_links_keyboard, \
    ROW_WIDTH_PARAMETER, ROW_COUNT_PARAMETER
from db_operations.links_dao.links_dao import LinksDAO
from logger.logger import logger


@commands_router.callback_query(F.data == 'show_single_link')
async def show_single_link(callback_query: CallbackQuery, next_from_id: int = 0):
    try:
        links_list: list = await LinksDAO.get_user_links(callback_query.from_user.id)
        if not links_list:
            await callback_query.message.edit_text(
                'У Вас не добавлено ни одной ссылки для отслеживания статуса',
                reply_markup=back_to_links_actions_keyboard
            )
            return
        max_links = ROW_WIDTH_PARAMETER*ROW_COUNT_PARAMETER
        links_to_keyboard = links_list[next_from_id:next_from_id+max_links]
        if not links_to_keyboard:
            await callback_query.message.edit_text(
                'Конец списка. Вернитесь в начало.',
                reply_markup=create_links_keyboard(links_to_keyboard, (min(len(links_to_keyboard), max_links)))
            )
            return
        await callback_query.message.edit_text(
            'Список ваших ссылок для отслеживания статуса',
            reply_markup=create_links_keyboard(links_to_keyboard, (min(len(links_to_keyboard), max_links)))
        )
    except Exception as e:
        await callback_query.answer()
        logger.warning(traceback.format_exc())

@commands_router.callback_query(F.data.startswith('show_next_link_keyboard'))
async def show_next_link(callback_query: CallbackQuery):
    try:
        next_from_id: int = int(callback_query.data.split(':')[-1])
    except ValueError:
        next_from_id: int = 0
    await show_single_link(callback_query, next_from_id)
