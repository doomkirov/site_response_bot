from optparse import Option
from typing import Optional

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from db_operations.all_models import UserModel
ROW_WIDTH_PARAMETER: int = 2

delete_all_links_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="◀️ Да, удалить все ссылки", callback_data='shure_to_delete_all')],
    [InlineKeyboardButton(text="◀️ Нет", callback_data='links_list_actions_for_user')],
])
back_to_main_menu_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="◀️ Назад в главное меню", callback_data='return_to_main_menu')],
])
back_to_links_actions_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="◀️ Назад к действиям со ссылками", callback_data='links_list_actions_for_user')],
])

user_links_actions_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="◀️ Добавить ссылку в список", callback_data='add_link_to_list')],
    [InlineKeyboardButton(text="◀️ Просмотреть весь список", callback_data='show_all_links')],
    [InlineKeyboardButton(text="◀️ Действия с отдельными ссылками", callback_data='show_single_link')],
    [InlineKeyboardButton(text="◀️ Удалить весь список", callback_data='delete_all_links')],
    [InlineKeyboardButton(text="◀️ Назад в главное меню", callback_data='return_to_main_menu')],
])

def create_links_keyboard(links: list, next_from_id: int = ROW_WIDTH_PARAMETER) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=ROW_WIDTH_PARAMETER, inline_keyboard=[])

    # Первый ряд
    buttons = [[InlineKeyboardButton(text=url, callback_data=f"link_structure_url:{url}")] for url in links]

    # Добавляем все кнопки одним вызовом
    # Второй ряд
    if buttons:
        for button in buttons:
            keyboard.inline_keyboard.append(button)
    else:
        keyboard.inline_keyboard.append(
            [InlineKeyboardButton(text="В начало", callback_data=f"show_next_link_keyboard:0")]
        )

    row = []
    if next_from_id > ROW_WIDTH_PARAMETER:
        row.append([
            InlineKeyboardButton(
                text="Назад",
                callback_data=f"show_next_link_keyboard:{next_from_id-ROW_WIDTH_PARAMETER}"
            )]
        )
    if len(buttons) >= ROW_WIDTH_PARAMETER:
        row.append(InlineKeyboardButton(
            text="Далее",
            callback_data=f"show_next_link_keyboard:{next_from_id}"
        ))
    keyboard.inline_keyboard.append(*row)

    # Третий ряд (одна кнопка)
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="◀️ Назад к действиям со ссылками", callback_data='links_list_actions_for_user'),
    ])
    return keyboard


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