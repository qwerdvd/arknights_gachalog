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
from .calculate_character_talent_buff import calculate_talent_buff
from .cal_buff_list import get_buff_list
from .cal_damage import calculate_physical_character_damage, calculate_magical_character_damage
from ..utils.alias.chName_to_CharacterId_list import chName_to_CharacterId

dmg_cal = on_command('伤害计算', priority=priority, block=True)


# 伤害计算
# "伤害计算 能天使 三技能 一模"
# 默认满技能满潜模组满级
@dmg_cal.handle()
async def send_dmg_cal_msg(
        event: MessageEvent, matcher: Matcher, args: Message = CommandArg()
):
    logger.info('开始执行[干员伤害计算]')
    mes = args.extract_plain_text().split()
    is_uniequip = False
    if len(mes) == 2:
        character = mes[0]
        skill_id = mes[1]
        uniequip_id = None
    elif len(mes) == 3:
        character = mes[0]
        skill_id = mes[1]
        uniequip_id = mes[2]
        is_uniequip = True

    # 处理技能id
    if skill_id == '一技能':
        skill_id = '1'
    elif skill_id == '二技能':
        skill_id = '2'
    elif skill_id == '三技能':
        skill_id = '3'

    characterId = await chName_to_CharacterId(character)
    print(characterId)
    with open(f'src/plugins/ark/tool/data/basic_character_info/{characterId}.json', encoding='UTF-8') as f:
        basic_character_info = json.load(f)
    profession = basic_character_info['profession']
    if profession in ['VANGUARD', 'SNIPER', 'DEFENDER', 'CASTER', 'GUARD']:
        damage_type = 'physical'
        print(damage_type)
        character_info = await calculate_fully_trained_character_data(characterId, is_uniequip, uniequip_id)
        talent_buff = await calculate_talent_buff(characterId, is_uniequip, uniequip_id)
        buff_list = await get_buff_list(characterId, is_uniequip, uniequip_id, skill_id)
        damage = await calculate_physical_character_damage(character_info)
    elif profession in ['SUPPORTER', 'MEDIC', 'SPECIALIST']:
        damage_type = 'magical'
        print(damage_type)
        character_info = await calculate_fully_trained_character_data(characterId, is_equip, uniequip_id)
        damage = await calculate_magical_character_damage(character_info)
