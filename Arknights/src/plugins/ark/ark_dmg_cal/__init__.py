import json

from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot import on_regex, on_command
from nonebot.adapters.onebot.v11 import (
    NoticeEvent,
    MessageSegment,
    GroupMessageEvent,
    Message,
    MessageEvent,
)
from nonebot.params import CommandArg

from ..config import priority
from .cal_full_trained_character_info import calculate_fully_trained_character_data
from .cal_damage import calculate_physical_character_damage, calculate_magical_character_damage
from ..utils.alias.chName_to_CharacterId_list import chName_to_CharacterId

dmg_cal = on_command('伤害计算', priority=priority, block=True)


@dmg_cal.handle()
async def send_dmg_cal_msg(
        event: MessageEvent, matcher: Matcher, args: Message = CommandArg()
):
    logger.info('开始执行[干员伤害计算]')
    mes = args.extract_plain_text().strip().replace(' ', '')
    character = mes.split(' ')[0]
    characterId = await chName_to_CharacterId(character)
    print(characterId)
    with open(f'src/plugins/ark/tool/data/basic_character_info/{characterId}.json', encoding='UTF-8') as f:
        basic_character_info = json.load(f)
    profession = basic_character_info['profession']
    if profession in ['VANGUARD', 'SNIPER', 'DEFENDER', 'CASTER', 'GUARD']:
        damage_type = 'physical'
        print(damage_type)
        damage = await calculate_physical_character_damage(characterId)
    elif profession in ['SUPPORTER', 'MEDIC', 'SPECIALIST']:
        damage_type = 'magical'
        print(damage_type)
        damage = await calculate_magical_character_damage(characterId)
