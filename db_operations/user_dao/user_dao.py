from typing import List

from sqlalchemy import select, delete, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import SQLAlchemyError

from settings.database import async_session_maker
from db_operations.all_models import UserModel, LinksModel, user_links
from db_operations.base_dao import BaseDao  # если используешь базовый DAO


class UserDAO(BaseDao):
    model = UserModel

    @classmethod
    async def add_links_to_user(cls, user_id: int, new_links: List[str]):
        """
        Добавляет список ссылок new_links к пользователю:
         - Сначала вставляет (если нужно) записи в links (ON CONFLICT DO NOTHING)
         - Потом вставляет связи в user_links (ON CONFLICT DO NOTHING)
         - Возвращает список всех url, связанных с пользователем после операции
        """
        # очистка входных ссылок
        new_links = [s.strip() for s in new_links if s and s.strip()]
        if not new_links:
            return []

        async with async_session_maker() as session:
            try:
                # гарантируем, что пользователь существует
                result = await session.execute(select(cls.model).filter_by(id=user_id))
                user = result.scalar_one_or_none()
                if not user:
                    # create_if_not_exists из BaseDao — оно создаёт объект и возвращает его
                    user = await cls.create_if_not_exists(id=user_id)

                # 1) Вставляем ссылки в таблицу links (пакетно)
                docs = [{"url": url} for url in set(new_links)]
                stmt = pg_insert(LinksModel).values(docs).on_conflict_do_nothing(index_elements=["url"])
                await session.execute(stmt)
                await session.flush()  # чтобы новые записи стали видимы при следующем select

                # 2) Получаем id существующих/новых ссылок
                q = await session.execute(select(LinksModel).where(LinksModel.url.in_(new_links)))
                links_objs = q.scalars().all()
                url_to_id = {l.url: l.id for l in links_objs}

                # 3) Готовим вставку в association table user_links
                association_rows = []
                for url in new_links:
                    link_id = url_to_id.get(url)
                    if link_id is not None:
                        association_rows.append({"user_id": user_id, "link_id": link_id})

                if association_rows:
                    stmt2 = pg_insert(user_links).values(association_rows).on_conflict_do_nothing(
                        index_elements=["user_id", "link_id"]
                    )
                    await session.execute(stmt2)

                await session.commit()

                # 4) Обновим/подтянем user и вернём список URL
                await session.refresh(user)
                # если relationship lazy='selectin', user.links загружены; иначе селектим
                return [l.url for l in user.links]
            except SQLAlchemyError:
                await session.rollback()
                raise

    @classmethod
    async def remove_links_from_user(cls, user_id: int, urls: List[str]):
        """
        Убирает связи пользователя с переданными urls (не удаляет сами строки в таблице links).
        """
        urls = [s.strip() for s in urls if s and s.strip()]
        if not urls:
            return

        async with async_session_maker() as session:
            try:
                # получаем id ссылок, которые нужно удалить из связи
                q = await session.execute(select(LinksModel).where(LinksModel.url.in_(urls)))
                link_ids = [l.id for l in q.scalars().all()]
                if not link_ids:
                    return

                del_stmt = delete(user_links).where(and_(
                    user_links.c.user_id == user_id,
                    user_links.c.link_id.in_(link_ids)
                ))
                await session.execute(del_stmt)
                await session.commit()
            except SQLAlchemyError:
                await session.rollback()
                raise

    @classmethod
    async def drop_all_links(cls, user_id: int):
        """
        Удаляет все связи пользователя с links (очищает user_links для данного user_id).
        """
        async with async_session_maker() as session:
            try:
                stmt = delete(user_links).where(and_(user_links.c.user_id == user_id))
                await session.execute(stmt)
                await session.commit()
            except SQLAlchemyError:
                await session.rollback()
                raise

    @classmethod
    async def get_user_links(cls, user_id: int) -> List[str]:
        async with async_session_maker() as session:
            q = await session.execute(
                select(cls.model)
                .options(selectinload(cls.model.links))
                .filter_by(id=user_id)
            )
            user = q.scalar_one_or_none()
            if not user:
                return []
            return [link.url for link in user.links]
