from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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
    # Первый ряд
    keyboard: list[list[InlineKeyboardButton]] = []
    buttons = [InlineKeyboardButton(text=url, callback_data=f"link_structure_url:{url}") for url in links]

    # Добавляем все кнопки одним вызовом
    # Второй ряд
    if buttons:
        keyboard.append(buttons)
    else:
        keyboard.append(
            [InlineKeyboardButton(text="В начало", callback_data=f"show_next_link_keyboard:0")]
        )

    keyboard.append([])
    if next_from_id > ROW_WIDTH_PARAMETER:
        keyboard[1].append(
            InlineKeyboardButton(
                text="Назад",
                callback_data=f"show_next_link_keyboard:{next_from_id-ROW_WIDTH_PARAMETER}"
            )
        )
    if len(buttons) == ROW_WIDTH_PARAMETER:
        keyboard[1].append(InlineKeyboardButton(
            text="Далее",
            callback_data=f"show_next_link_keyboard:{next_from_id}"
        ))
    if not keyboard[1]:
        del keyboard[1]


    # Третий ряд (одна кнопка)
    keyboard.append([
        InlineKeyboardButton(text="◀️ Назад к действиям со ссылками", callback_data='links_list_actions_for_user'),
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


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