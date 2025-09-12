import asyncio
import traceback

from app.checker import validate_data
from bot_operations.bot_main import run_bot
from db_operations.all_models import LinksModel
from db_operations.links_dao.links_dao import LinksDAO
from logger.logger import logger


async def main():
    links_objects: list[LinksModel] = await LinksDAO.find_all()
    tasks: list = []
    for l_object in links_objects:
        tasks.append(validate_data(l_object))
    await asyncio.gather(*tasks)

async def periodic_main(interval: int = 30):
    """Запускает main() строго каждые interval секунд (от старта)"""
    while True:
        try:
            start = asyncio.get_event_loop().time()  # время начала
            await main()
            elapsed = asyncio.get_event_loop().time() - start
            sleep_time = max(0, interval - int(elapsed))
            await asyncio.sleep(sleep_time)
        except Exception as er:
            logger.warning(er)
            logger.warning(traceback.format_exc())


async def main_wrapper():
    await asyncio.gather(
        periodic_main(),
        run_bot()
    )


if __name__ == '__main__':
    asyncio.run(main_wrapper())