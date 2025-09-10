# db_operations/links_dao.py
from sqlalchemy import select, delete, exists, and_, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import SQLAlchemyError

from db_operations.base_dao import BaseDao
from settings.database import async_session_maker
from db_operations.all_models import LinksModel, user_links  # user_links — association Table


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
    async def remove_links(cls, links: list[str]) -> None:
        """
        Удаляет записи из таблицы links по url.
        Если в схеме association 'user_links' задан ondelete='CASCADE', то связи у юзеров удалятся автоматически.
        """
        urls = list({l.strip() for l in links if l and l.strip()})
        if not urls:
            return

        async with async_session_maker() as session:
            try:
                qry = delete(cls.model).where(cls.model.url.in_(urls))
                await session.execute(qry)
                await session.commit()
            except SQLAlchemyError:
                await session.rollback()
                raise

    @classmethod
    async def cleanup_orphan_links(cls):
        """
        Удаляет все ссылки из таблицы links, которые не связаны ни с одним пользователем.
        Если dry_run=True — не удаляет, а возвращает список (id, url), которые бы были удалены.
        Возвращает список удалённых (или потенциально удаляемых) (id, url).
        """
        async with async_session_maker() as session:
            try:
                # условие: для каждой ссылки не существует записи в user_links с таким link_id
                orphan_cond = ~exists(select(user_links.c.link_id).where(and_(user_links.c.link_id == LinksModel.id)))

                del_stmt = (
                    delete(LinksModel)
                    .where(orphan_cond)
                )
                await session.execute(del_stmt)
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