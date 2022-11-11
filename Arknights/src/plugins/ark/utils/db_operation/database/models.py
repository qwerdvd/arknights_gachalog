import asyncio
import threading
from typing import Optional

from .db_config import Field, SQLModel, engine


class UidData(SQLModel, table=True):
    USERID: int = Field(default=100000000, primary_key=True, title="QQ号")
    UID: Optional[str] = Field(title="UID")


class NewCookiesTable(SQLModel, table=True):
    UID: int = Field(default=100000000, primary_key=True, title="UID")
    Cookies: str = Field(title="CK")
    QID: int = Field(title="QQ号")
    ChannelMasterId: int = Field(default=1, title="服务器")
    Extra: Optional[str] = Field(title="备注")
    token: Optional[str] = Field(title="token")


class CookiesCache(SQLModel, table=True):
    UID: Optional[str] = Field(default="100000000", primary_key=True)
    Cookies: str


class Config(SQLModel, table=True):
    Name: str = Field(default="Config", primary_key=True, title="设置项")
    Status: Optional[str] = Field(title="开启状态")
    GroupList: Optional[str] = Field(title="群组")
    Extra: Optional[str] = Field(title="额外选项")


async def create_all():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


threading.Thread(target=lambda: asyncio.run(create_all()), daemon=True).start()
