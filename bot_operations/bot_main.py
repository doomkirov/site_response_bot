from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery

from bot_operations.bot_support.base_router import commands_router
from bot_operations.bot_support.keyboards import get_start_menu_keyboard
from db_operations.all_models import UserModel
from db_operations.user_dao.user_dao import UserDAO
from settings.settings import settings
from aiogram.fsm.storage.memory import MemoryStorage
# 👇 Required imports for correct work of dispatcher
from bot_operations.operations import (notifications, links_list_actions, # noqa
                                       single_link_actions, link_structure_operations) # noqa
from bot_operations.operations.admin import admin_operations # noqa
# for tests only from app import tester  # noqa

bot = Bot(token=settings.BOT_TOKEN)

dp = Dispatcher(storage=MemoryStorage())
dp.include_router(commands_router)


@commands_router.message(F.text == "/start")
async def show_main_menu(message: Message):
    user_id = message.from_user.id
    user: UserModel = await UserDAO.create_if_not_exists(id=user_id)
    await message.answer(
        'Выберите действие!',
        reply_markup=get_start_menu_keyboard(user.send_results, user_id)
    )


@commands_router.callback_query(F.data == 'return_to_main_menu')
async def return_to_main_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    user: UserModel = await UserDAO.create_if_not_exists(id=user_id)
    await callback.message.edit_text(
        'Выберите действие!',
        reply_markup=get_start_menu_keyboard(user.send_results, user_id),
    )


async def run_bot():
    await dp.start_polling(bot)