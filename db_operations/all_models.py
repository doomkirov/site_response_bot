from sqlalchemy import Column, BigInteger, Integer, ForeignKey, String
from sqlalchemy.orm import relationship

from settings.database import Base

class User(Base):
    __tablename__ = 'users'

    # Primary key — telegram id
    id = Column(BigInteger, primary_key=True)

    # Связь один-ко-многим с таблицей ссылок
    links = relationship("Link", back_populates="user", cascade="all, delete-orphan")

    class Config:
        orm_mode = True


class Link(Base):
    __tablename__ = 'links'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign key на пользователя
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    user = relationship("User", back_populates="links")

    # Сама ссылка
    url = Column(String, nullable=False)

    # Время последней проверки (Unix timestamp)
    last_checked = Column(BigInteger, default=0)

    # Последний полученный статус
    last_status = Column(Integer, default=0)

    # Время последней ошибки (Unix timestamp)
    last_error_time = Column(BigInteger, default=0)

    # Время последнего успеха (status 200)
    last_success_time = Column(BigInteger, default=0)

    class Config:
        orm_mode = True