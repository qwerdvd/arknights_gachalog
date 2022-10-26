from typing import Tuple, Optional

import aiofiles
from nonebot.log import logger
from aiohttp.client import ClientSession
from aiohttp.client_exceptions import ClientConnectorError

from .RESOURCE_PATH import (
    RESOURCE_PATH,
    AVATAR_PATH,
    ITEM_PATH,
    PORTRAIT_PATH,
    PROFESSION_PATH,
    BUILDING_SKILL_PATH,
    ENEMY_PATH,
    ITEM_RARITY_IMG_PATH,
    # MAP_PATH,
    SKIN_PATH,
    TEMP_PATH,
    PLAYER_PATH,
)

PATH_MAP = {
    1: AVATAR_PATH,
    # 2: CHAR_STAND_PATH,
    # 3: CHAR_SIDE_PATH,
    # 4: GACHA_IMG_PATH,
    # 5: WEAPON_PATH,
    # 6: CHAR_NAMECARD_PATH,
    # 7: REL_PATH,
    # 8: ICON_PATH,
}


async def download_file(
        sess: ClientSession, url: str, path: int, name: str
) -> Optional[Tuple[str, int, str]]:
    """
    :说明:
      下载URL保存入目录
    :参数:
      * url (str): 资源下载地址。
      * path (int): 资源保存路径
        '''
        1: AVATAR_PATH,
        # 2: CHAR_STAND_PATH,
        # 3: CHAR_SIDE_PATH,
        # 4: GACHA_IMG_PATH,
        # 5: WEAPON_PATH,
        # 6: CHAR_NAMECARD_PATH,
        # 7: REL_PATH,
        # 8: ICON_PATH,
        '''
      * name (str): 资源保存名称
    :返回:
        url (str) path (int) name (str)
    """
    try:
        async with sess.get(url) as res:
            content = await res.read()
    except ClientConnectorError:
        logger.warning(f"[prts.wiki]{name}下载失败")
        return url, path, name
    async with aiofiles.open(PATH_MAP[path] / name, "wb") as f:
        await f.write(content)
