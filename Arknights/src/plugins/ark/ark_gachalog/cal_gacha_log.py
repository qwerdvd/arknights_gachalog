import time
from typing import Optional
from nonebot.log import logger


async def calculate_average_star_probability(star: int, gacha_logs: Optional[dict] = None) -> int:
    """
    计算某星级出货概率
    :param star: 星级。
    :param gacha_logs: 抽卡记录。
    :return: probability: 该星级的出货概率。
    """
    star_gacha_num = gacha_logs[f'{star}_star_gacha_num']
    all_gacha_num = gacha_logs['all_gacha_num']
    probability = star_gacha_num / all_gacha_num
    return probability


async def get_gacha_time(ts: int) -> str:
    """
    获取抽卡时间
    :param ts: 时间戳。
    :return: gacha_time: 抽卡时间。
    """
    local_gacha_time = time.localtime(ts)
    gacha_time = time.strftime('%Y-%m-%d %H:%M:%S', local_gacha_time)
    return gacha_time

