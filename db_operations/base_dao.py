from sqlalchemy import select, insert
from sqlalchemy.exc import IntegrityError

from settings.database import async_session_maker


class BaseDao:
    model = None

    @classmethod
    async def find_by_id(cls, model_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(id=model_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def find_all(cls):
        async with async_session_maker() as session:
            query = select(cls.model)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def put(cls, **data):
        async with async_session_maker() as session:
            query = insert(cls.model).values(**data)
            await session.execute(query)
            await session.commit()

    @classmethod
    async def create_if_not_exists(cls, **data):
        async with async_session_maker() as session:
            # сначала проверяем, есть ли такой объект
            query = select(cls.model).filter_by(**data)
            result = await session.execute(query)
            obj = result.scalar_one_or_none()
            if obj:
                return obj  # объект уже существует, возвращаем его

            # если нет — создаём новый
            obj = cls.model(**data)
            session.add(obj)
            try:
                await session.commit()
                await session.refresh(obj)  # подтягиваем сгенерированные поля (например, id)
            except IntegrityError:
                # на случай гонки (другой процесс вставил объект между select и insert)
                await session.rollback()
                result = await session.execute(query)
                obj = result.scalar_one_or_none()
            return obj
