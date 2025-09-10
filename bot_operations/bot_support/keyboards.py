from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from db_operations.all_models import UserModel


delete_all_links_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="◀️ Да, удалить все ссылки", callback_data='shure_to_delete_all')],
    [InlineKeyboardButton(text="◀️ Нет", callback_data='links_list_actions_for_user')],
])
back_to_main_menu_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="◀️ Назад в главное меню", callback_data='return_to_main_menu')],
])
back_to_links_actions_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="◀️ Назад к действиям со списком ссылок", callback_data='links_list_actions_for_user')],
])

user_links_actions_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="◀️ Добавить ссылку в список", callback_data='add_link_to_list')],
    [InlineKeyboardButton(text="◀️ Просмотреть весь список", callback_data='show_all_links')],
    [InlineKeyboardButton(text="◀️ Удалить весь список", callback_data='delete_all_links')],
    [InlineKeyboardButton(text="◀️ Назад в главное меню", callback_data='return_to_main_menu')],
])


def get_start_menu_keyboard(send_results: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Действия со списком ссылок", callback_data=f"links_list_actions_for_user")],
    ])
    text = "Включить отправку уведомлений"
    if send_results == 1:
        text = "Остановить отправку уведомлений!"
    keyboard.inline_keyboard.insert(
        0,
        [InlineKeyboardButton(
            text=text,
            callback_data=f"user_change_notifications_{send_results}"
        )]
    )
    return keyboard