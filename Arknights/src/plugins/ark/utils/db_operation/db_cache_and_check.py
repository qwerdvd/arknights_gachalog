import os
import re
import random
import string
import datetime
from shutil import copyfile

from httpx import AsyncClient
from nonebot.log import logger

from Arknights.src.plugins.ark.utils.ark_api.arknights_api import GET_AUTHKEY_URL
from ark_db_pool import ark_pool
from Arknights.src.plugins.ark.utils.ark_api.get_ark_data import get_token_by_cookie


async def check_db():
    return_str = str()
    normal_num = 0
    invalid_str = ''
    invalid_list = []
    conn = ark_pool.connect()
    c = conn.cursor()
    cursor = c.execute('SELECT UID,Cookies,QID from NewCookiesTable')
    c_data = cursor.fetchall()
    for row in c_data:
        try:
            aid = re.search(r'account_id=(\d*)', row[1])
            ark_id_data = aid.group(0).split('=')  # type: ignore
            ark_id = ark_id_data[1]
            mys_data = await get_token_by_cookie(ark_id)
            for i in mys_data['data']['list']:
                if i['game_id'] != 2:
                    mys_data['data']['list'].remove(i)
            return_str = (
                    return_str + f'uid{row[0]}/{ark_id}的Cookies是正常的！\n'
            )
            normal_num += 1
            logger.info(f'uid{row[0]}/mys{ark_id}的Cookies是正常的！')
        except Exception:
            invalid_str = (
                    invalid_str + f'uid{row[0]}的Cookies是异常的！已删除该条Cookies！\n'
            )
            return_str = (
                    return_str + f'uid{row[0]}的Cookies是异常的！已删除该条Cookies！\n'
            )
            invalid_list.append([row[2], row[0]])
            c.execute('DELETE from NewCookiesTable where UID=?', (row[0],))
            try:
                c.execute(
                    'DELETE from CookiesCache where Cookies=?', (row[1],)
                )
            except Exception:
                pass
            logger.info(f'uid{row[0]}的Cookies是异常的！已删除该条Cookies！')
    if len(c_data) > 9:
        return_str = '正常Cookies数量：{}\n{}'.format(
            str(normal_num),
            '失效cookies:\n' + invalid_str if invalid_str else '无失效Cookies',
        )
    conn.commit()
    conn.close()
    logger.info('已完成Cookies检查！')
    logger.info(f'正常Cookies数量：{str(normal_num)}')
    logger.info('失效cookies:\n' + invalid_str if invalid_str else '无失效Cookies')
    return [return_str, invalid_list]


async def refresh_ck(uid, mysid):
    conn = ark_pool.connect()
    c = conn.cursor()
    try:
        c.execute(
            'DELETE from CookiesCache where uid=?', (uid, mysid)
        )
    except Exception:
        pass


async def check_token_db():
    def random_text(num: int) -> str:
        return ''.join(
            random.sample(string.ascii_lowercase + string.digits, num)
        )

    return_str = str()
    normal_num = 0
    invalid_str = ''
    invalid_list = []
    conn = ark_pool.connect()
    c = conn.cursor()
    cursor = c.execute('SELECT UID,token,QID  from NewCookiesTable')
    c_data = cursor.fetchall()
    for row in c_data:
        if row[1] is None:
            continue
        async with AsyncClient() as client:
            req = await client.get(
                url=GET_AUTHKEY_URL,
                headers={
                    'cookie': row[1],
                    'Referer': 'https://ak.hypergryph.com/user/inquiryGacha',
                    'Origin': 'https://ak.hypergryph.com',
                    'sec-fetch-dest': 'document',
                    'sec-fetch-mode': 'navigate',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ''Chrome/106.0.0.0 Safari/537.36 '
                },
            )
        data = req.json()
        if 'err' in data['message'] or data['statusCode'] == -401:
            invalid_str = (
                    invalid_str + f'uid{row[0]}的token是异常的！已删除该条token！\n'
            )
            return_str = return_str + f'uid{row[0]}的token是异常的！已删除该条token！\n'
            invalid_list.append([row[2], row[0]])
            c.execute(
                'UPDATE NewCookiesTable SET token = ? WHERE UID=?',
                (None, row[0]),
            )
            logger.info(f'uid{row[0]}的token是异常的！已删除该条token！')
        else:
            return_str = return_str + f'uid{row[0]}的token是正常的！\n'
            logger.info(f'uid{row[0]}的token是正常的！')
            normal_num += 1
    if len(c_data) > 9:
        return_str = '正常token数量：{}\n{}'.format(
            str(normal_num),
            '失效token:\n' + invalid_str if invalid_str else '无失效token',
        )
    conn.commit()
    conn.close()
    logger.info('已完成token检查!')
    logger.info(f'正常token数量：{normal_num}')
    logger.info('失效token:\n' + invalid_str if invalid_str else '无失效token')
    return [return_str, invalid_list]


async def delete_cache():
    try:
        today = datetime.date.today()
        endday = today - datetime.timedelta(days=5)
        date_format = today.strftime("%Y_%d_%b")
        endday_format = endday.strftime("%Y_%d_%b")
        copyfile('ID_DATA.db', f'ID_DATA_BAK_{date_format}.db')
        if os.path.exists(f'ID_DATA_BAK_{endday_format}.db'):
            os.remove(f'ID_DATA_BAK_{endday_format}.db')
            logger.info(f'————已删除数据库备份{endday_format}————')
        logger.info('————数据库成功备份————')
    except Exception:
        logger.info('————数据库备份失败————')

    try:
        conn = ark_pool.connect()
        c = conn.cursor()
        c.execute('DROP TABLE CookiesCache')
        c.execute(
            'UPDATE NewCookiesTable SET Extra = ? WHERE Extra=?',
            (None, 'limit30'),
        )
        c.execute(
            """CREATE TABLE IF NOT EXISTS CookiesCache
        (UID TEXT PRIMARY KEY,
        TEXT,          Cookies       
        TEXT);"""
        )
        conn.commit()
        conn.close()
        logger.info('————UID查询缓存已清空————')
    except Exception:
        logger.info('\nerror\n')
