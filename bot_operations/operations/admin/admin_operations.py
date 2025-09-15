from aiogram import F
from aiogram.types import CallbackQuery

from bot_operations.bot_support.base_router import commands_router
from bot_operations.bot_support.keyboards import get_admin_list_keyboard, back_to_main_menu_keyboard
from bot_operations.bot_support.support_funcs import send_by_parts
from db_operations.links_dao.links_dao import LinksDAO
from db_operations.user_dao.user_dao import UserDAO


@commands_router.callback_query(F.data == 'admin_operations')
async def admin_operations(callback: CallbackQuery):
    await callback.message.edit_text(
        'Добро пожаловать, Администратор!\nВыберите действие',
        reply_markup=get_admin_list_keyboard
    )

@commands_router.callback_query(F.data == 'admin_show_all_users')
async def admin_show_all_users(callback: CallbackQuery):
    users: list = await UserDAO.get_column('id')
    text = f'Список всех пользователей:\n' + '\n'.join(map(str, users))
    await send_by_parts(callback=callback, text=text, base_reply_markup=back_to_main_menu_keyboard)

@commands_router.callback_query(F.data == 'admin_show_all_links')
async def admin_show_all_links(callback: CallbackQuery):
    links: list = await LinksDAO.get_column('url')
    text = f'Список всех ссылок всех пользователей:\n' + '\n'.join(links)
    await send_by_parts(callback=callback, text=text, base_reply_markup=back_to_main_menu_keyboard)