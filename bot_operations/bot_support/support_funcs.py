from urllib.parse import urlparse


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
