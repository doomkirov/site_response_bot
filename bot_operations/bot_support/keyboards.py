from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings.settings import settings

ROW_WIDTH_PARAMETER: int = 3
ROW_COUNT_PARAMETER: int = 2

delete_all_links_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🗑️ Да, удалить все ссылки", callback_data="shure_to_delete_all")],
    [InlineKeyboardButton(text="↩️ Нет", callback_data="links_list_actions_for_user")],
])
back_to_main_menu_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🏠 Назад в главное меню", callback_data="return_to_main_menu")],
])
back_to_links_actions_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔗 Назад к действиям со ссылками", callback_data="links_list_actions_for_user")],
])
user_links_actions_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⚠️ Показать все ошибочные ссылки", callback_data="bad_links")],
    [InlineKeyboardButton(text="➕ Добавить ссылку в список", callback_data="add_link_to_list")],
    [InlineKeyboardButton(text="📜 Просмотреть весь список", callback_data="show_all_links")],
    [InlineKeyboardButton(text="📝 Действия с отдельными ссылками", callback_data="show_single_link")],
    [InlineKeyboardButton(text="🗑️ Удалить весь список", callback_data="delete_all_links")],
    [InlineKeyboardButton(text="🏠 Назад в главное меню", callback_data="return_to_main_menu")],
])
get_admin_list_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="👥 Список всех пользователей", callback_data="admin_show_all_users")],
    [InlineKeyboardButton(text="📊 Вся таблица ссылок", callback_data="admin_show_all_links")],
    [InlineKeyboardButton(text="◀️ Назад в главное меню", callback_data="return_to_main_menu")],
])

def back_to_single_link_operations_keyboard(url: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📂 В меню ссылки", callback_data=f"link_structure_url:{url}~~|~~0")],
    ])
    return keyboard


def get_single_link_operations_keyboard(url: str, next_from_id: str) -> InlineKeyboardMarkup:
    """
    :param url: Ссылка с которой работает пользователь в данный момент.
    :param next_from_id: Вернуться к просмотру отдельных ссылок - число должно быть уменьшено так, чтобы
    вернуть пользователя обратно в ту часть списка, откуда он попал на конкретно эту URL
    :return:
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="♻️ Перепроверить доступность",
            callback_data=f"retry_status_for:{url}",
        )],
        [InlineKeyboardButton(
            text="🗑️ Удалить ссылку из списка",
            callback_data=f"delete_link:{url}",
        )],
        [InlineKeyboardButton(
            text="↩️ Вернуться к просмотру отдельных ссылок",
            callback_data=f"show_next_link_keyboard:{next_from_id}",
        )],
        [InlineKeyboardButton(
            text="◀️ Назад к действиям со ссылками",
            callback_data="links_list_actions_for_user",
        )],
    ])

    return keyboard

def create_links_keyboard(links: list, next_from_id: int = ROW_WIDTH_PARAMETER) -> InlineKeyboardMarkup:
    def split_by_size(seq, row_width):
        return [seq[i:i + row_width] for i in range(0, len(seq), row_width)]

    keyboard: list[list[InlineKeyboardButton]] = []

    rows = split_by_size(links, ROW_WIDTH_PARAMETER)

    for row in rows:
        buttons = [
            InlineKeyboardButton(
                text=f'🔗 {url}',
                callback_data=f"link_structure_url:{url}~~|~~"
                              f"{max(next_from_id-ROW_WIDTH_PARAMETER*ROW_COUNT_PARAMETER, 0)}") for url in row
        ]
        if buttons:
            keyboard.append(buttons)
    if not keyboard:
        keyboard.append(
            [InlineKeyboardButton(text="◀️ В начало", callback_data=f"show_next_link_keyboard:0")]
        )

    keyboard.append([])
    if next_from_id > ROW_WIDTH_PARAMETER*ROW_COUNT_PARAMETER:
        keyboard[-1].append(
            InlineKeyboardButton(
                text="🔙 Назад",
                callback_data=f"show_next_link_keyboard:{max(next_from_id-(ROW_WIDTH_PARAMETER*ROW_COUNT_PARAMETER)*2, 0)}"
            )
        )
    if len(links) == ROW_WIDTH_PARAMETER*ROW_COUNT_PARAMETER:
        keyboard[-1].append(InlineKeyboardButton(
            text="➡️ Далее",
            callback_data=f"show_next_link_keyboard:{next_from_id}"
        ))
    if not keyboard[-1]:
        del keyboard[-1]


    # Третий ряд (одна кнопка)
    keyboard.append([
        InlineKeyboardButton(text="⬇️ Назад к действиям со ссылками", callback_data="links_list_actions_for_user"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_start_menu_keyboard(send_results: int, user_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="☰ Действия со списком ссылок", callback_data=f"links_list_actions_for_user")],
    ])
    text = "🔔 Включить отправку уведомлений"
    if send_results == 1:
        text = "🔕 Остановить отправку уведомлений!"
    keyboard.inline_keyboard.insert(
        0,
        [InlineKeyboardButton(
            text=text,
            callback_data=f"user_change_notifications_{send_results}"
        )]
    )
    if user_id == settings.ADMIN_USER_ID:
        keyboard.inline_keyboard.insert(
            0,
            [InlineKeyboardButton(
                text='Функции администратора',
                callback_data=f"admin_operations"
            )]
        )
    return keyboard