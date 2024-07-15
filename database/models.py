from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy import String, Integer, BigInteger, ForeignKey, Boolean

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id = mapped_column(BigInteger)
    search_history: Mapped[str] = mapped_column(String, nullable=True)
    notified_ads: Mapped[str] = mapped_column(String, ForeignKey('ads.id'), nullable=True)
    rating_bot_job: Mapped[int] = mapped_column(Integer, nullable=True)


class Ad(Base):
    __tablename__ = 'ads'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id = mapped_column(BigInteger)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(2000))
    price: Mapped[int] = mapped_column(Integer)
    location: Mapped[str] = mapped_column(String(255))
    contact = mapped_column(BigInteger)
    moderated = mapped_column(Boolean, default=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
