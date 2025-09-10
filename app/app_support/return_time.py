from datetime import timezone, timedelta, datetime


def format_unix_utc_plus3(ts: int) -> str:
    """
    Форматирует UNIX-время в часовом поясе UTC+3.
    Формат: "HH:MM:SS DD:MM:YYYY"
    """
    tz = timezone(timedelta(hours=3))      # фиксированный сдвиг +3 часа
    dt = datetime.fromtimestamp(ts, tz)    # создаём datetime с нужной tz
    return dt.strftime("%H:%M:%S %d:%m:%Y")