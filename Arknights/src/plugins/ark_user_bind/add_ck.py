from pathlib import Path
from http.cookies import SimpleCookie

from ..utils.db_operation.db_cache_and_check import refresh_ck
from ..utils.db_operation.db_operation import select_db, token_db, cookies_db


async def _deal_ck(mes, qid) -> str:
    simp_dict = SimpleCookie(mes)
    uid = await select_db(qid, 'uid')
    if isinstance(uid, str):
        pass
    else:
        return '该用户没有绑定过UID噢~'
    im_list = []
    if 'ACCOUNT' in simp_dict:
        # 寻找ACCOUNT
        cookie = simp_dict['ACCOUNT'].value
    else:
        return '该CK字段出错, 缺少ACCOUNT字段!'
    await cookies_db(uid, cookie, qid)
    im_list.append(
        f'添加Cookies成功，uid={uid}，ACCOUNT_COOKIE={cookie}'
    )
    im = '\n'.join(im_list)
    return im
