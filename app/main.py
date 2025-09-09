import asyncio

from bot_operations.bot_main import run_bot


async def main():
    pass


async def main_wrapper():
    await asyncio.gather(
        main(),
        run_bot()
    )


if __name__ == '__main__':
    asyncio.run(main_wrapper())