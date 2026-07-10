import asyncio
import logging
import os
import time

from app.alerts import send_pending_alerts
from app.checker import is_night_period, validate_data
from app.nightly_report import send_nightly_report_if_due
from app.utils import initialize_links
from db_operations.all_models import LinksModel
from db_operations.links_dao.links_dao import LinksDAO


logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    links_objects: list[LinksModel] = await LinksDAO.find_all()
    logger.info("Начинаю проверку %d сайтов", len(links_objects))

    tasks = [validate_data(link_object) for link_object in links_objects]
    if not tasks:
        logger.warning("В базе нет сайтов для проверки")
        return

    await asyncio.gather(*tasks)
    timestamp = int(time.time())
    if not is_night_period(timestamp):
        await send_pending_alerts(timestamp)
    logger.info("Проверка %d сайтов завершена", len(links_objects))


async def periodic_main(interval: int = 60):
    """Запускает main() каждые ``interval`` секунд от старта итерации."""
    logger.info("Инициализирую список сайтов")
    await initialize_links()
    logger.info("Планировщик запущен: интервал %d секунд", interval)

    while True:
        try:
            start = asyncio.get_running_loop().time()
            logger.debug("Начата очередная итерация проверки")
            await main()
            if await send_nightly_report_if_due():
                logger.info("Утренняя сводка по доступности отправлена")

            elapsed = asyncio.get_running_loop().time() - start
            sleep_time = max(0, interval - elapsed)
            logger.info(
                "Итерация выполнена за %.2f с; следующая проверка через %.2f с",
                elapsed,
                sleep_time,
            )
            await asyncio.sleep(sleep_time)
        except Exception:
            logger.exception("Непредвиденная ошибка в periodic_main")
            logger.info("Повторю проверку через %d секунд", interval)
            await asyncio.sleep(interval)


async def main_wrapper():
    await periodic_main()


if __name__ == "__main__":
    logger.info("Приложение запущено")
    asyncio.run(main_wrapper())
