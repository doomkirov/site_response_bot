import time, asyncio
from functools import wraps
from datetime import datetime, timezone, timedelta

from logger.logger import logger

# Часовой пояс UTC+3
UTC_PLUS_3 = timezone(timedelta(hours=3))

def log_execution_time(func):
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = datetime.now(UTC_PLUS_3)
        result = await func(*args, **kwargs)
        end_time = datetime.now(UTC_PLUS_3)
        logger.debug(f'[START] {func.__name__} - {start_time.strftime("%Y-%m-%d %H:%M:%S")}\n'
              f'Время выполнения {func.__name__} - {(end_time - start_time).total_seconds()}'
              f' с аргументами args={args}, kwargs={kwargs}')
        return result

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = datetime.now(UTC_PLUS_3)
        result = func(*args, **kwargs)
        end_time = datetime.now(UTC_PLUS_3)
        logger.debug(f'[START] {func.__name__} - {start_time.strftime("%Y-%m-%d %H:%M:%S")}\n'
              f'Время выполнения {func.__name__} - {(end_time - start_time).total_seconds()}'
              f'с аргументами args={args}, kwargs={kwargs}')
        return result

    # Определяем, асинхронная функция или синхронная
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


if __name__ == '__main__':
    @log_execution_time
    def sync_task():
        time.sleep(1)
    sync_task()