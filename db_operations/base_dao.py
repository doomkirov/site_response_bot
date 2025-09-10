from pydantic import with_config
from sqlalchemy import select, insert, and_, delete, update
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
    async def get_column(cls, column: str):
        """
        Возвращает список из всех значений заданной колонки для
        :param column:
        :return:
        """
        async with async_session_maker() as session:
            column_attr = getattr(cls.model, column, None)
            if column_attr is None:
                raise ValueError(f"В модели {cls.model.__name__} нет колонки '{column}'")
            query = select(column_attr)
            result = await session.execute(query)
            return [row[0] for row in result.all()]

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

    @classmethod
    async def delete_row(cls, filter_field, filter_value):
        async with async_session_maker() as session:
            column_attr = getattr(cls.model, filter_field, None)
            if column_attr is None:
                raise ValueError(f"В модели {cls.model.__name__} нет колонки '{filter_field}'")
            stmt = delete(cls.model).where(and_(column_attr == filter_value))
            await session.execute(stmt)
            await session.commit()

    @classmethod
    async def change_value_in_row(cls, filter_field: str, filter_value, **kwargs):
        """
        Универсально меняет значения в строке по любому полю.
        Возвращает обновлённый объект или None, если не найдено.
        """

        async with async_session_maker() as session:
            column_attr = getattr(cls.model, filter_field)
            stmt = update(cls.model).where(column_attr == filter_value).values(**kwargs).returning(cls.model)
            result = await session.execute(stmt)
            await session.commit()
            obj = result.scalar_one_or_none()
            print(obj.send_results)
            return obj
