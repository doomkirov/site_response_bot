from urllib.parse import urlparse

from aiogram.types import CallbackQuery, InlineKeyboardMarkup

from bot_operations.bot_support.keyboards import back_to_links_actions_keyboard


async def send_by_parts(
        callback: CallbackQuery,
        text: str,
        base_reply_markup: InlineKeyboardMarkup = back_to_links_actions_keyboard):
    parts = split_text_by_limit(text=text)
    if len(parts) == 1:
        await callback.message.edit_text(
            parts[0],
            reply_markup=base_reply_markup,
            disable_web_page_preview=True
        )
    else:
        await callback.message.edit_text(parts.pop(0))
        reply_markup = None
        for i, part in enumerate(parts):
            if i+1 == len(parts):
                reply_markup = base_reply_markup
            await callback.message.answer(
                text=part,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )

def normalize_url(url: str) -> str:
    url = url.strip()  # убираем лишние пробелы
    parsed = urlparse(url)

    # Если нет схемы (http/https), добавляем https
    if not parsed.scheme:
        url = "https://" + url
        parsed = urlparse(url)

    # проверяем, что есть домен
    if not parsed.netloc:
        raise ValueError(f"Неверный URL: {url}")

    return url

def split_text_by_limit(text: str, limit: int = 4096) -> list[str]:
    """
    Делит текст на части, не превышающие limit,
    разрезая по границам строк.
    """
    lines = text.split('\n')
    parts = []
    current_part = ""

    for line in lines:
        # +1 для символа '\n', если он будет добавлен
        add_line = line if current_part == "" else "\n" + line

        if len(current_part) + len(add_line) > limit:
            # если следующая строка не помещается — сохраняем текущую часть
            parts.append(current_part)
            current_part = line  # начинаем новую часть
        else:
            current_part += add_line

    if current_part:
        parts.append(current_part)

    return parts
