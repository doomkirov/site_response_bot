from aiogram import F
from aiogram.types import CallbackQuery

from bot_operations.bot_support.base_router import commands_router
from bot_operations.bot_support.keyboards import back_to_links_actions_keyboard, create_links_keyboard
from db_operations.links_dao.links_dao import LinksDAO


@commands_router.callback_query(F.data == 'show_single_link')
async def show_single_link(callback_query: CallbackQuery, next_from_id: int = 0):
    links_list: list = await LinksDAO.get_user_links(callback_query.from_user.id)
    if not links_list:
        await callback_query.message.edit_text(
            'У Вас не добавлено ни одной ссылки для отслеживания статуса',
            reply_markup=back_to_links_actions_keyboard
        )
        return
    links_to_keyboard = links_list[next_from_id:next_from_id+2]
    if not links_to_keyboard:
        await callback_query.message.edit_text(
            'Конец списка. Вернитесь в начало.',
            reply_markup=back_to_links_actions_keyboard
        )
        return
    await callback_query.message.edit_text(
        'Список ваших ссылок для отслеживания статуса',
        reply_markup=create_links_keyboard(links_to_keyboard, next_from_id+2)
    )
