from typing import List, Union
from nonebot.log import logger

from .database.CookiesDAL import CookiesDAL
from .database.UidDataDAL import UidDataDAL
from .database.db_config import async_session


async def bind_db(userid, uid=None):
    logger.info(f'绑定数据库{userid} {uid}')
    async with async_session() as session:
        async with session.begin():
            UidData = UidDataDAL(session)
            im = await UidData.bind_db(userid, {'UID': uid})
            logger.info(im)
            return im


async def get_all_uid() -> List:
    async with async_session() as session:
        async with session.begin():
            UidData = UidDataDAL(session)
            lst = await UidData.get_all_uid_list()
            return lst


async def select_db(
        userid: int, mode: str = 'auto'
) -> Union[List[str], str, None]:
    """
    :说明:
      选择绑定uid库
    :参数:
      * userid (str): QQ号。
      * mode (str): 模式如下
        * auto(默认): 自动选择
        * uid: 选择uid库
        * list: 返回uid列表
    :返回:
      * data (list): 返回获取值
      mode为list时返回uid列表
      其他情况下data[0]为需要的uid
      data[1]表示data[0]是`uid`
    """
    async with async_session() as session:
        async with session.begin():
            UidData = UidDataDAL(session)
            if mode == 'auto':
                im = await UidData.get_anyid(userid)
            elif mode == 'uid':
                im = await UidData.get_uid(userid)
            elif mode == 'list':
                im = await UidData.get_uid_list(userid)
            else:
                return None
            return im


async def delete_db(userid: int, data: dict) -> str:
    """
    :说明:
      删除当前绑定的UID信息
      删除前 -> 12_13_14
      删除后 -> 13_14
    :参数:
      * userid (str): QQ号。
    :返回:
      * im (str): 回调信息。
    """
    async with async_session() as session:
        async with session.begin():
            UidData = UidDataDAL(session)
            im = await UidData.delete_db(userid, data)
            return im


async def cookies_db(uid: str, cookies: str, qid: int):
    async with async_session() as session:
        async with session.begin():
            Cookies = CookiesDAL(session)
            im = await Cookies.add_cookie_db(qid, uid, cookies)
            return im


async def error_db(cookies: str, error: str):
    async with async_session() as session:
        async with session.begin():
            Cookies = CookiesDAL(session)
            im = await Cookies.add_error_db(cookies, error)
            return im


async def owner_cookies(uid: str) -> str:
    async with async_session() as session:
        async with session.begin():
            Cookies = CookiesDAL(session)
            owner_ck = await Cookies.get_user_ck(uid)
            return str(owner_ck)


async def delete_cookies(uid: str) -> str:
    async with async_session() as session:
        async with session.begin():
            Cookies = CookiesDAL(session)
            result = await Cookies.delete_user(uid)
            if result:
                return '删除CK完成!'
            else:
                return '删除CK失败!'


async def get_token(uid: str) -> str:
    async with async_session() as session:
        async with session.begin():
            Cookies = CookiesDAL(session)
            token = await Cookies.get_user_token(uid)
            return str(token)


async def get_user_bind_data(uid: str) -> dict:
    async with async_session() as session:
        async with session.begin():
            Cookies = CookiesDAL(session)
            lst = await Cookies.get_user_data_dict(uid)
            return lst


async def token_db(s_cookies: str, uid: str) -> str:
    async with async_session() as session:
        async with session.begin():
            Cookies = CookiesDAL(session)
            im = await Cookies.add_token_db(uid, s_cookies)
            return im


async def empty_cache():
    async with async_session() as session:
        async with session.begin():
            Cookies = CookiesDAL(session)
            await Cookies.delete_cache()
