from pathlib import Path
from http.cookies import SimpleCookie

from ..utils.db_operation.db_cache_and_check import refresh_ck
from ..utils.db_operation.db_operation import select_db, stoken_db, cookies_db

pic_path = Path(__file__).parent / 'pic'


async def deal_ck(mes, qid, mode: str = 'PIC'):
    im = await _deal_ck(mes, qid)
    if mode == 'PIC':
        im = await _deal_ck_to_pic(im)
    return im


async def _deal_ck_to_pic(im) -> bytes:
    ok_num = im.count('成功')
    if ok_num < 1:
        status_pic = pic_path / 'ck_no.png'
    elif ok_num < 2:
        status_pic = pic_path / 'ck_ok.png'
    else:
        status_pic = pic_path / 'all_ok.png'
    with open(status_pic, 'rb') as f:
        im = f.read()
    return im


async def _deal_ck(mes, qid) -> str:
    simp_dict = SimpleCookie(mes)
    uid = await select_db(qid, 'uid')
    if isinstance(uid, str):
        pass
    else:
        return '该用户没有绑定过UID噢~'
    im_list = []
    if 'ACCOUNT' in simp_dict:
        # 寻找stoken
        cookie = simp_dict['ACCOUNT'].value
    else:
        return '该CK字段出错, 缺少ACCOUNT字段!'
    await cookies_db(uid, cookie, qid)
    im_list.append(
        f'添加Cookies成功，uid={uid}，ACCOUNT_COOKIE={cookie}'
    )
    im = '\n'.join(im_list)
    return im
