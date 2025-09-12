import asyncio

from aiogram import F
from aiogram.types import Message

from app.checker import validate_data
from bot_operations.bot_support.base_router import commands_router
from db_operations.links_dao.links_dao import LinksDAO


@commands_router.message(F.text == "test")
async def test(message: Message):
    user_id = message.from_user.id
    links = await LinksDAO.get_user_links(user_id)
    tasks: list = []
    for link in links:
        tasks.append(validate_data(link))
    await asyncio.gather(*tasks)