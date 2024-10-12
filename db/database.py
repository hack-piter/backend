
from sqlalchemy import select, MetaData
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    async_sessionmaker,
    create_async_engine,
    AsyncSession,
)
from sqlalchemy.orm import DeclarativeBase
from db.config import postgres_async_config

engine = create_async_engine(
    url=postgres_async_config.POSTGRES_URL,
    echo=True
)

SessionFactory = async_sessionmaker(engine, autoflush=False, expire_on_commit=False)

metadata = MetaData()


class Base(AsyncAttrs, DeclarativeBase):

    async def save(self, db: AsyncSession):
        """
        :param db:
        :return:
        """
        try:
            db.add(self)
            await db.commit()
            return self
        except SQLAlchemyError as ex:
            raise Exception(ex)

    async def delete(self, db: AsyncSession):
        """
        :param db:
        :return:
        """
        try:
            await db.delete(self)
            await db.commit()
            return self
        except SQLAlchemyError as ex:
            raise Exception(ex)

    async def is_exists(self, db: AsyncSession):
        """
        :param db:
        :return:
        """

    @classmethod
    async def find_by_id(cls, db: AsyncSession, id: str):
        query = select(cls).where(cls.id == id)
        result = await db.execute(query)
        return result.scalars().first()


async def get_db():
    async with SessionFactory() as db:
        yield db
