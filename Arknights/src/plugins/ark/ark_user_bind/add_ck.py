from pathlib import Path
from http.cookies import SimpleCookie
from nonebot.log import logger

from ..utils.db_operation.db_cache_and_check import refresh_ck
from ..utils.db_operation.db_operation import (
    select_db,
    token_db,
    cookies_db,
    get_channelMasterId,
    channelMasterId_db,
)
from ..utils.ark_api.get_ark_data import get_token_by_cookie, usr_ark_basic_info


async def deal_ck(mes, qid):
    im = await _deal_ck(mes, qid)
    return im


async def _deal_ck(mes, qid) -> str:
    simp_dict = SimpleCookie(mes)
    uid = await select_db(qid, "uid")
    if isinstance(uid, str):
        pass
    else:
        return "该用户没有绑定过UID噢~"
    im_list = []
    is_add_token = False
    if "ACCOUNT" in simp_dict:
        # 寻找ACCOUNT
        cookie = simp_dict["ACCOUNT"].value
        channelMasterId = 1
    elif "ACCOUNT_AK_B" in simp_dict:
        # 寻找ACCOUNT_AK_B
        cookie = simp_dict["ACCOUNT_AK_B"].value
        channelMasterId = 2
    else:
        return "该CK字段出错, 缺少ACCOUNT或者ACCOUNT_AK_B字段!"
    await cookies_db(uid, cookie, qid)
    await channelMasterId_db(uid, channelMasterId)
    token_rawdata = await get_token_by_cookie(cookie, qid)
    token = str(token_rawdata)
    is_add_token = True
    if is_add_token:
        await token_db(token, uid)
    im_list.append(
        f"添加Cookies成功，uid={uid}, channelMasterId={channelMasterId},ACCOUNT_COOKIE={cookie},token={token}"
    )
    im = "\n".join(im_list)
    return im
