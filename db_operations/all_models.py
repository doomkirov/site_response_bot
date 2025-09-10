from sqlalchemy import Column, BigInteger, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import UniqueConstraint

from settings.database import Base

user_links = Table(
    "user_links",
    Base.metadata,
    Column("user_id", BigInteger, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("link_id", Integer, ForeignKey("links.id", ondelete="CASCADE"), primary_key=True),
    UniqueConstraint("user_id", "link_id", name="uq_user_link"),
)


class UserModel(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)

    links = relationship(
        "LinksModel",
        secondary=user_links,
        back_populates="users",
        lazy="selectin",
        cascade="save-update",
    )

    send_results = Column(Integer, default=0)

    class Config:
        orm_mode = True


class LinksModel(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, nullable=False, unique=True)

    last_checked = Column(BigInteger, default=0)
    last_status = Column(Integer, default=0)
    last_error_status = Column(Integer, default=0)
    last_error_time = Column(BigInteger, default=0)
    last_success_time = Column(BigInteger, default=0)

    users = relationship(
        "UserModel",
        secondary=user_links,
        back_populates="links",
        lazy="selectin",
    )

    class Config:
        orm_mode = True