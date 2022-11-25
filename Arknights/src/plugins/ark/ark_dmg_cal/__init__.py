import json

from nonebot import on_command, on_regex
from nonebot.adapters.onebot.v11 import (
    GroupMessageEvent,
    Message,
    MessageEvent,
    MessageSegment,
    NoticeEvent,
)
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

from .cal_single_damage.char_103_angel import calculate_angel_damage
from ..config import priority
from ..utils.alias.chName_to_CharacterId_list import chName_to_CharacterId
from .cal_buff_list import get_buff_list, get_character_skill_id
from .cal_character_info import calculate_fully_trained_character_data
from .calculate_character_talent_buff import calculate_talent_buff
from ..utils.alias.characterId_to_uniequipId import characterId_to_uniequipId

dmg_cal = on_command("伤害计算", priority=priority, block=True)


# 伤害计算
# "伤害计算 能天使 三技能 一模"
# 默认满技能满潜模组满级
@dmg_cal.handle()
async def send_dmg_cal_msg(event: MessageEvent, matcher: Matcher, args: Message = CommandArg()):
    logger.info("开始执行[干员伤害计算]")
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
    if skill_id == "一技能":
        skill_id = "1"
    elif skill_id == "二技能":
        skill_id = "2"
    elif skill_id == "三技能":
        skill_id = "3"

    char_id = await chName_to_CharacterId(character)
    print(char_id)
    with open(
        f"src/plugins/ark/tool/data/basic_character_info/{char_id}.json",
        encoding="UTF-8",
    ) as f:
        basic_character_info = json.load(f)
    profession = basic_character_info["profession"]
    character_info = await calculate_fully_trained_character_data(char_id, is_uniequip, uniequip_id)
    talent_buff = await calculate_talent_buff(char_id, is_uniequip, uniequip_id)
    buff_list = await get_buff_list(char_id, is_uniequip, uniequip_id, skill_id)
    im = await calculate_angel_damage(char_id, character_info, buff_list, skill_id, uniequip_id)
    im.append("finish")
    await matcher.finish(im)
