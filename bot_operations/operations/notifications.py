from aiogram import F
from aiogram.types import CallbackQuery

from bot_operations.bot_support.base_router import commands_router
from bot_operations.bot_support.keyboards import back_to_main_menu_keyboard
from db_operations.all_models import UserModel
from db_operations.user_dao.user_dao import UserDAO


@commands_router.callback_query(F.data == 'user_change_notifications')
async def user_stop_notifications(callback: CallbackQuery):
    try:
        user_id = callback.from_user.id
        user: UserModel = await UserDAO.find_one_or_none(id=user_id)
        if not user:
            raise ValueError
        current_send = user.send_results
        value = 0 if current_send == 1 else 1
        result = await UserDAO.update_notifications(user_id=user_id, value=value)
        if result:
            await callback.message.edit_text(
                text='Уведомления больше не будут приходить!' if current_send == 1 else 'Теперь вы будете получать уведомления!',
                reply_markup=back_to_main_menu_keyboard
            )
        else:
            raise ValueError
    except ValueError:
        await callback.message.edit_text(
            'Непредвиденная ошибка! --Такого пользователя не существует',
            reply_markup=back_to_main_menu_keyboard
        )
    except Exception:
        await callback.message.edit_text(
            'Непредвиденная ошибка!',
            reply_markup=back_to_main_menu_keyboard
        )