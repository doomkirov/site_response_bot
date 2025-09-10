import traceback

from aiogram import F
from aiogram.types import CallbackQuery

from bot_operations.bot_support.base_router import commands_router
from bot_operations.bot_support.keyboards import back_to_main_menu_keyboard
from db_operations.user_dao.user_dao import UserDAO
from logger.logger import logger


@commands_router.callback_query(F.data.startswith('user_change_notifications_'))
async def user_stop_notifications(callback: CallbackQuery):
    try:
        prefix = 'user_change_notifications_'
        value = int(callback.data[len(prefix):]) # Отражает True и False на поле send_notifications
        user_id = callback.from_user.id
        result = await UserDAO.change_value_in_row('id', user_id, send_results=0 if value == 1 else 1)
        if result:
            await callback.message.edit_text(
                text='Уведомления больше не будут приходить!' if value == 1 else 'Теперь вы будете получать уведомления!',
                reply_markup=back_to_main_menu_keyboard
            )
        else:
            raise ValueError
    except ValueError as er:
        await callback.message.edit_text(
            'Непредвиденная ошибка! --Такого пользователя не существует',
            reply_markup=back_to_main_menu_keyboard
        )
        logger.error(er)
    except Exception as er:
        await callback.message.edit_text(
            'Непредвиденная ошибка!',
            reply_markup=back_to_main_menu_keyboard
        )
        logger.error(traceback.format_exc())