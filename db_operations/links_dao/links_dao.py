from sqlalchemy import  update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import SQLAlchemyError

from db_operations.base_dao import BaseDao
from settings.database import async_session_maker
from db_operations.all_models import LinksModel


class LinksDAO(BaseDao):
    model = LinksModel

    @classmethod
    async def add_links(cls, links: list[str]) -> None:
        """
        Пакетно добавляет ссылки в таблицу links.
        Поведение: добавляет все ссылки, которые ещё не существуют (ON CONFLICT DO NOTHING).
        """
        links = list({l.strip() for l in links if l and l.strip()})  # очистка и уникализация входа
        if not links:
            return

        docs = [{"url": l} for l in links]

        async with async_session_maker() as session:
            try:
                stmt = pg_insert(cls.model).values(docs).on_conflict_do_nothing(index_elements=["url"])
                await session.execute(stmt)
                await session.commit()
            except SQLAlchemyError:
                await session.rollback()
                raise

    @classmethod
    async def update_fields_by_url_simple(cls, url: str, **fields) -> int:
        if not fields:
            raise ValueError("Нет полей для обновления")

        # Оставляем только те, что существуют в модели (проверка через hasattr)
        payload = {}
        for name, value in fields.items():
            if hasattr(cls.model, name):
                payload[name] = value
            else:
                raise ValueError(f"В модели {cls.model.__name__} нет атрибута '{name}'")

        if not payload:
            raise ValueError("Нет допустимых полей для обновления")

        stmt = (
            update(cls.model)
            .where(cls.model.url == url)
            .values(**payload)
            .execution_options(synchronize_session="fetch")
        )

        try:
            async with async_session_maker() as session:
                result = await session.execute(stmt)
                await session.commit()
                return result.rowcount
        except SQLAlchemyError:
            raise