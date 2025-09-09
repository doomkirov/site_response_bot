import time
from functools import wraps
from datetime import datetime, timezone, timedelta

# Часовой пояс UTC+3
UTC_PLUS_3 = timezone(timedelta(hours=3))

def log_execution_time(func):
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = datetime.now(UTC_PLUS_3).strftime("%Y-%m-%d %H:%M:%S")
        print(f"[START] {func.__name__} - {start_time}")
        result = await func(*args, **kwargs)
        end_time = datetime.now(UTC_PLUS_3).strftime("%Y-%m-%d %H:%M:%S")
        print(f"[END] {func.__name__} - {end_time}")
        return result

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = datetime.now(UTC_PLUS_3)
        print(f"[START] {func.__name__} - {start_time.strftime("%Y-%m-%d %H:%M:%S")}")
        result = func(*args, **kwargs)
        end_time = datetime.now(UTC_PLUS_3)
        print(f"[END] {func.__name__} - {end_time.strftime("%Y-%m-%d %H:%M:%S")}")
        print(f'Время выполнения {func.__name__} - {(end_time - start_time).total_seconds()}')
        return result

    # Определяем, асинхронная функция или синхронная
    if hasattr(func, "__await__"):
        return async_wrapper
    return sync_wrapper


if __name__ == '__main__':
    @log_execution_time
    def sync_task():
        time.sleep(1)
    sync_task()