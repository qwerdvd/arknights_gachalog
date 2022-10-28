import copy
import json
import asyncio
from typing import Any, Dict, Literal, Optional

from nonebot.log import logger
import aiohttp
from aiohttp import ClientSession

from ..db_operation.db_operation import get_token, select_db, get_channelMasterId
from .arknights_api import (
    GET_GACHA_LOG_URL,
    GET_AUTHKEY_URL,
    GET_AUTHKEY_URL_Bilibili,
    GET_UID_URL,
)

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

gacha_type_meta_data = {'单up池': [], '专属推荐干员寻访': [], '联合寻访': [], '常驻标准寻访': []}


async def usr_ark_basic_info(token: str) -> dict:
    """
    :说明:
      获取用户游戏基本信息，包含uid,channelMasterId和nickName。
    :参数:
      * token (str): 用户token。
    :返回:
      * result (dict): 用户基本信息。
      {'status': 0, 'msg': 'OK', 'data': {'uid': '', 'guest': 0, 'channelMasterId': 1, 'nickName': ''}}
    """
    HEADER = copy.deepcopy(_HEADER)
    payload = {
        "appId": 1,
        "channelMasterId": 1,
        "channelToken": {
            "token": f"{token}"
        }
    }
    HEADER['Referer'] = 'https://ak.hypergryph.com'
    HEADER['Origin'] = 'https://ak.hypergryph.com'
    async with aiohttp.ClientSession() as session:
        async with session.post(GET_UID_URL, headers=HEADER, json=payload) as response:
            usr_basic_info = await response.json()
    return usr_basic_info


async def get_token_by_cookie(COOKIE: str, qid: int) -> dict:
    url = ''
    cookie = COOKIE
    HEADER = copy.deepcopy(_HEADER)
    uid = await select_db(qid)
    channelMasterId = await get_channelMasterId(uid)
    if channelMasterId == 1:
        url = GET_AUTHKEY_URL
        COOKIE = f'ACCOUNT={cookie}'
    elif channelMasterId == 2:
        url = GET_AUTHKEY_URL_Bilibili
        COOKIE = f'ACCOUNT_AK_B={cookie}'
    if cookie == '该用户没有绑定过Cookie噢~' or cookie == '':
        return {}
    HEADER['Cookie'] = COOKIE
    HEADER['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                           'Chrome/106.0.0.0 Safari/537.36 '
    HEADER['sec-fetch-dest'] = 'document'
    HEADER['sec-fetch-mode'] = 'navigate'
    authkey = await _ark_request(
        url=url,
        method='GET',
        header=HEADER,
    )
    logger.info(f'authkey: {authkey}')
    if authkey['msg'] == '登录失效':
        authkey = await _ark_request(
            url=GET_AUTHKEY_URL_Bilibili,
            method='GET',
            header=HEADER,
        )
    token = authkey['data']['content']
    return token


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
        # print(text_data)
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
    token = await get_token(uid)
    HEADER = copy.deepcopy(_HEADER)
    channelMasterId = await get_channelMasterId(uid)
    full_data = old_data or {'单up池': [], '专属推荐干员寻访': [], '联合寻访': [], '常驻标准寻访': []}
    temp = []
    if channelMasterId == 2:
        HEADER['Referer'] = 'https://ak.hypergryph.com/user/bilibili/gacha'
    end_id = 0
    for page in range(1, 999):
        raw_data = await _ark_request(
            url=GET_GACHA_LOG_URL,
            method='GET',
            header=HEADER,
            params={
                'channelId': channelMasterId,
                'token': token,
                'page': page,
                'end_id': end_id,
            },
        )
        await asyncio.sleep(0.9)
        if 'data' in raw_data and 'list' in raw_data['data']:
            data = raw_data['data']['list']
        else:
            return {}
        if not data:
            break
        end_id = data[-1]['ts']
        for i in range(len(data)):
            if data[-i]['pool'] == '专属推荐干员寻访':
                gacha_type = '专属推荐干员寻访'
                if data[-i] not in full_data[gacha_type]:
                    temp.append(data[-i])
                full_data[gacha_type][0:0] = temp
                temp = []
            elif data[-i]['pool'] == '联合寻访':
                gacha_type = '联合寻访'
                if data[-i] not in full_data[gacha_type]:
                    temp.append(data[-i])
                full_data[gacha_type][0:0] = temp
                temp = []
            elif data[-i]['pool'] == '常驻标准寻访':
                gacha_type = '常驻标准寻访'
                if data[-i] not in full_data[gacha_type]:
                    temp.append(data[-i])
                full_data[gacha_type][0:0] = temp
                temp = []
            else:
                gacha_type = '单up池'
                if data[-i] not in full_data[gacha_type]:
                    temp.append(data[-i])
                full_data[gacha_type][0:0] = temp
                temp = []
        temp = []
        await asyncio.sleep(0.5)
    return full_data
