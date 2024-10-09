import os

from typing import Annotated, Optional, List

from datetime import datetime

from uuid import uuid4

from fastapi import Depends

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

########################################################################################

POSTGRES_HOST = os.environ["POSTGRES_HOST"]
POSTGRES_DB = os.environ["POSTGRES_DB"]
POSTGRES_USER = os.environ["POSTGRES_USER"]
POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]
POSTGRES_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"

engine = create_async_engine(POSTGRES_URL)
SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

########################################################################################


class Base(DeclarativeBase):
    pass


class UserInDB(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(
        primary_key=True, index=True, default=lambda: str(uuid4())
    )
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    email: Mapped[str]
    hashed_password: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    disabled: Mapped[bool] = mapped_column(default=False)
    jobs: Mapped[List["JobInDB"]] = relationship(back_populates="user")


class JobInDB(Base):
    __tablename__ = "jobs"

    job_id: Mapped[str] = mapped_column(primary_key=True, index=True)
    task: Mapped[str]
    backend: Mapped[str]
    status: Mapped[str]
    result: Mapped[Optional[str]]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    user: Mapped["UserInDB"] = relationship(back_populates="jobs")


########################################################################################


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()


db_dependency = Annotated[AsyncSession, Depends(get_db)]
