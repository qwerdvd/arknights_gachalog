from typing import List, Optional
from nonebot.log import logger

from sqlalchemy.future import select
from sqlalchemy import delete, update
from sqlalchemy.sql.expression import func
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.models import CookiesCache, NewCookiesTable


class CookiesDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_user_data(self, uid: str) -> Optional[NewCookiesTable]:
        try:
            await self.db_session.execute(
                ("ALTER TABLE NewCookiesTable " "ADD COLUMN token TEXT")  # type: ignore
            )
        except Exception:
            pass
        sql = select(NewCookiesTable).where(NewCookiesTable.UID == uid)
        result = await self.db_session.execute(sql)
        data = result.scalars().all()
        if data:
            return data[0]
        else:
            return None

    async def get_user_data_dict(self, uid: str) -> dict:
        data = await self.get_user_data(uid)
        if data:
            return data.__dict__
        else:
            return {}

    async def get_user_ck(self, uid: str) -> str:
        """
        :说明:
          获取Cookies
        :参数:
          * uid (int): UID。
        :返回:
          * cookies (str): Cookies。
        """
        data = await self.get_user_data(uid)
        if data:
            return data.Cookies
        else:
            return "该用户没有绑定过Cookies噢~"

    async def get_user_ck_valid(self, uid: str) -> bool:
        data = await self.get_user_data(uid)
        if data and data.Extra:
            return False
        elif data is None:
            return False
        else:
            return True

    async def get_user_token(self, uid: str) -> Optional[str]:
        """
        :说明:
          获取token
        :参数:
          * cookies (str): Cookies。
        :返回:
          * token (str): Token。
        """
        data = await self.get_user_data(uid)
        if data:
            # 有可能返回None
            return data.token
        else:
            return "该用户没有绑定过token噢~"

    async def get_user_channelMasterId(self, uid: str) -> Optional[str]:
        """
        :说明:
          获取channelMasterId
        :参数:
          * uid (str): UID。
        :返回:
          * channelMasterId (str): channelMasterId。
        """
        data = await self.get_user_data(uid)
        logger.info(data)
        if data:
            # 有可能返回None
            logger.info(f"获取到的channelMasterId为{data.ChannelMasterId}")
            data_raw = str(data.ChannelMasterId)
            return data_raw
        else:
            return "该用户没有绑定过channelMasterId噢~"

    async def user_exists(self, uid: str) -> bool:
        data = await self.get_user_data(uid)
        if data:
            return True
        else:
            return False

    async def add_cookie_db(self, userid: int, uid: str, cookies: str) -> bool:
        """
        :说明:
          绑定Cookies
        :参数:
          * userid (int): QQ号。
          * uid (int): UID。
          * cookies (str): Cookies。
        :返回:
          * msg (str): 绑定文字信息。
        """
        if await self.user_exists(uid):
            sql = (
                update(NewCookiesTable)
                .where(NewCookiesTable.UID == uid)
                .values(Cookies=cookies, Extra=None)
            )
            await self.db_session.execute(sql)
        else:
            new_data = NewCookiesTable(
                UID=int(uid),
                Cookies=cookies,
                QID=userid,
                Extra=None,
            )
            self.db_session.add(new_data)
        await self.db_session.flush()
        return True

    async def add_token_db(self, uid: str, token: str) -> str:
        """
        :说明:
          绑定token
        :参数:
          * uid (int): UID。
          * token (str): token。
        :返回:
          * msg (str): 绑定文字信息。
        """
        if await self.user_exists(uid):
            sql = (
                update(NewCookiesTable)
                .where(NewCookiesTable.UID == uid)
                .values(token=token)
            )
            await self.db_session.execute(sql)
            msg = f"UID{uid}账户的token绑定成功!"
        else:
            msg = f"UID{uid}的token绑定失败\n请先绑定Cookies~"
        await self.db_session.flush()
        return msg

    async def add_channelMasterId_db(self, uid: str, channelMasterId: int) -> str:
        """
        :说明:
          绑定channelMasterId
        :参数:
          * uid (int): UID。
          * channelMasterId (int): channelMasterId。
        :返回:
          * msg (str): 绑定文字信息。
        """
        if await self.user_exists(uid):
            sql = (
                update(NewCookiesTable)
                .where(NewCookiesTable.UID == uid)
                .values(ChannelMasterId=channelMasterId)
            )
            await self.db_session.execute(sql)
            msg = f"UID{uid}账户的channelMasterId绑定成功!"
        else:
            msg = f"UID{uid}的channelMasterId绑定失败\n请先绑定Cookies~"
        await self.db_session.flush()
        return msg

    async def delete_user(self, uid: str) -> bool:
        """
        :说明:
          从NewCookiesTable中删除一行用户数据
        :参数:
          * uid (int): UID。
        :返回:
          * msg (str): 更新文字信息。
        """
        if await self.user_exists(uid):
            sql = delete(NewCookiesTable).where(NewCookiesTable.UID == int(uid))
            await self.db_session.execute(sql)
            return True
        else:
            return False

    async def delete_cache(self):
        sql = (
            update(NewCookiesTable)
            .where(NewCookiesTable.Extra == "limit30")
            .values(Extra=None)
        )
        empty_sql = delete(CookiesCache)
        await self.db_session.execute(sql)
        await self.db_session.execute(empty_sql)

    async def add_error_db(self, cookies: str, err: str) -> bool:
        """
        :说明:
          为绑定的Cookies添加错误信息
        :参数:
          * cookies (str): Cookies。
          * err (str): 错误信息。
            ['limit30', 'error']
        :返回:
          * msg (str): 绑定文字信息。
        """
        sql = (
            update(NewCookiesTable)
            .where(NewCookiesTable.Cookies == cookies)
            .values(Extra=err)
        )
        await self.db_session.execute(sql)
        await self.db_session.flush()
        return True
