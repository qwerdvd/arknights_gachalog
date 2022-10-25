import asyncio
import threading
from typing import Optional

from .db_config import Field, SQLModel, engine


class UidData(SQLModel, table=True):
    USERID: int = Field(default=100000000, primary_key=True)
    UID: Optional[str]


class NewCookiesTable(SQLModel, table=True):
    UID: int = Field(default=100000000, primary_key=True)
    Cookies: str
    QID: int
    NUM: Optional[int]
    Extra: Optional[str]
    token: Optional[str]


class CookiesCache(SQLModel, table=True):
    UID: Optional[str] = Field(default='100000000', primary_key=True)
    Cookies: str


class Config(SQLModel, table=True):
    Name: str = Field(default='Config', primary_key=True)
    Status: Optional[str]
    GroupList: Optional[str]
    Extra: Optional[str]


async def create_all():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


threading.Thread(target=lambda: asyncio.run(create_all()), daemon=True).start()
