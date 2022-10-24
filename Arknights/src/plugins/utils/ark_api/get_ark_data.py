import copy
import json
import asyncio
from typing import Any, Dict, Literal, Optional

from nonebot.log import logger
from aiohttp import ClientSession

from ...utils.ark_api.arknights_api import (
    GET_GACHA_LOG_URL,
    GET_AUTHKEY_URL,
)

gacha_type_meta_data = {
    'List': {},
}

_HEADER = {
    'User-Agent': (
        'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) '
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        'AppleWebKit/537.36 (KHTML, like Gecko)'
        'Chrome/106.0.0.0'
        'Safari/537.36'
    ),
    'Referer': 'https://ak.hypergryph.com/user/inquiryGacha',
    'Origin': 'https://ak.hypergryph.com',
}

COOKIE = 'ACCOUNT=s%3AdAlS78TUJAmBb1zSs6sFtCLn.64rk5SwFum2Sz2zCwaXTgVnPKK5jwTywT2e%2FsQKoKz8;'


async def get_token_by_cookie(cookie: str) -> dict:
    HEADER = copy.deepcopy(_HEADER)
    # cookie = await get_stoken(uid)
    cookie = COOKIE
    if cookie == '该用户没有绑定过Cookie噢~' or cookie == '':
        return {}
    HEADER['Cookie'] = cookie
    HEADER['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                           'Chrome/106.0.0.0 Safari/537.36 '
    HEADER['sec-fetch-dest'] = 'document'
    HEADER['sec-fetch-mode'] = 'navigate'
    authkey = await _ark_request(
        url=GET_AUTHKEY_URL,
        method='GET',
        header=HEADER,
    )

    return authkey


async def _ark_request(
        url: str,
        method: Literal['GET', 'POST'] = 'GET',
        header: Dict[str, Any] = _HEADER,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        sess: Optional[ClientSession] = None,
) -> dict:
    """
    :说明:
      访问URL并进行json解析返回。
    :参数:
      * url (str): ArknightsAPI。
      * method (Literal["GET", "POST"]): `POST` or `GET`。
      * header (Dict[str, Any]): 默认为_HEADER。
      * params (Dict[str, Any]): 参数。
      * data (Dict[str, Any]): 参数(`post`方法需要传)。
      * sess (ClientSession): 可选, 指定client。
    :返回:
      * result (dict): json.loads()解析字段。
    """
    is_temp_sess = False
    if sess is None:
        sess = ClientSession()
        is_temp_sess = True
    try:
        req = await sess.request(
            method, url=url, headers=header, params=params
        )
        text_data = await req.text()
        print(text_data)
        if text_data.startswith('('):
            text_data = json.loads(text_data.replace("(", "").replace(")", ""))
            return text_data
        return await req.json()
    except Exception as err:
        print('An exception happened: ' + str(err))
        return {}
    finally:
        if is_temp_sess:
            await sess.close()


async def get_gacha_log_by_token(
        uid: str, old_data: Optional[dict] = None
) -> Optional[dict]:
    token_rawdata = await get_token_by_cookie(uid)
    if token_rawdata == {} or token_rawdata is None:
        return None
    if 'data' in token_rawdata and 'content' in token_rawdata['data']:
        token = token_rawdata['data']['content']
    else:
        return None
    full_data = old_data or {'List': []}
    temp = []
    end_id = 0
    for page in range(1, 999):
        raw_data = await _ark_request(
            url=GET_GACHA_LOG_URL,
            method='GET',
            header=_HEADER,
            params={
                'channelId': '1',
                'token': token,
                'page': page,
                'end_id': end_id,
            },
        )
        await asyncio.sleep(0.9)
        if 'data' in raw_data and 'list' in raw_data['data']:
            data = raw_data['data']['list']
        else:
            logger.warning(raw_data)
            return {}
        if not data:
            break
        end_id = data[-1]['ts']
        if data[-1] in full_data['List']:
            for item in data:
                if item not in full_data['List']:
                    temp.append(item)
            full_data['List'][0:0] = temp
            temp = []
            break
        if len(full_data['List']) >= 1:
            if int(data[-1]['ts']) <= int(
                    full_data['List'][0]['ts']
            ):
                full_data['List'].extend(data)
            else:
                full_data['List'][0:0] = data
        else:
            full_data['List'].extend(data)
        await asyncio.sleep(0.5)
    return full_data
