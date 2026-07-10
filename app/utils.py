from app.app_support import ResponseData
from db_operations.links_dao import LinksDAO
from db_operations.all_models import LinksModel
from urllib.parse import urlsplit, urlunsplit


def create_message(data: ResponseData) -> str:
    """
    Формирует сообщение для чата.

    Если status_code == 200 — уведомление о восстановлении сайта.
    Иначе — уведомление об ошибке.
    """

    if data.status_code == 200:
        return (
            "[B]✅ Сайт снова доступен[/B][BR][BR]"
            f"[URL={data.url}]{data.url}[/URL][BR][BR]"
            "Статус: [B]200 OK[/B]"
        )

    return (
        "[B]🚨 Обнаружена проблема с сайтом[/B][BR][BR]"
        f"Сайт: [URL={data.url}]{data.url}[/URL][BR][BR]"
        f"Статус: [B]{data.status_code}[/B][BR]"
        f"{data.explanation}"
    )


def normalize_url(url: str, default_scheme: str = "https") -> str:
    """
    Нормализует URL.
    Примеры:
        ps-gk.ru                    -> https://ps-gk.ru
        профстрой.рф                -> https://профстрой.рф
    """
    url = url.strip()

    if "://" not in url:
        url = f"{default_scheme}://{url}"

    parsed = urlsplit(url)

    return urlunsplit(
        (
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path,
            parsed.query,
            parsed.fragment,
        )
    )

ALL_SITES: list = [
    "ps-gk.ru",
    "профстрой.рф",
    "пс-недвижимость.рф",
    "щебень-профстрой.рф",
    "бетон-профстрой.рф",
    "профстрой-недвижимость.рф",
    "форт.рф",
    "профстрой-проект.рф",
    "zavod.ps-gk.ru",
    "ленина-106.рф",
    "мурашинский-7.рф",
    "домпрофстрой.рф",
    "жк-вдохновение.рф",
    "кд-капитал.рф",
    "дом-капитал.рф",
]

async def initialize_links():
    """Добавляет необходимые ссылки в бд
    Если они уже есть - не делает ничего.
    """
    await LinksDAO.add_links(ALL_SITES)
