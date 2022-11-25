import json

from ..cal_buff_list import get_character_skill_id
from ..character_class import Char, clear_buff_list
from nonebot import logger


async def calculate_angel_damage(
    character_id: str,
    character_info: dict,
    buff_list: dict,
    skill_id: str,
    uniequip_id: str = None,
) -> list:
    im = []
    skill_id = await get_character_skill_id(character_id, skill_id)

    with open(
        f"src/plugins/ark/tool/data/character_skill_info/{character_id}.json",
        encoding="utf-8",
    ) as f:
        skill_basic_info = json.load(f)
    angel = Char(character_info)
    angel_skill = angel.SkillInfo(skill_basic_info, skill_id)
    angel_buff = angel.Buff()

    angel_uniequip_buff = angel_buff.UniequipBuff(buff_list)
    angel_talent_buff = angel_buff.TalentBuff(buff_list)
    angel_sub_profession_buff = angel_buff.SubProfessionTraitBuff(buff_list)
    angel_skill_buff = angel_buff.SkillBuff(buff_list)

    logger.info(f"angel_arb_info: {angel.__dict__}")
    logger.info(f"angel_uniequip_buff is {angel_uniequip_buff.__dict__}")
    logger.info(f"angel_talent_buff is {angel_talent_buff.__dict__}")
    logger.info(f"angel_sub_profession_buff is {angel_sub_profession_buff.__dict__}")
    logger.info(f"angel_skill_buff is {angel_skill_buff.__dict__}")

    atk_scale = 1

    # 先计算模组加成
    for buff in angel_uniequip_buff.__dict__:
        log = "[模组] "
        if angel_uniequip_buff.__dict__ != {}:
            if buff == "atk_scale":
                angel.base_atk_scale = angel.base_atk_scale * angel_uniequip_buff.__dict__["atk_scale"]
                log = log + f"{uniequip_id}: atk_scale: {angel.base_atk_scale}x"
                logger.info(log)

    # 计算天赋加成
    for buff in angel_talent_buff.__dict__:
        log = "[天赋] "
        if angel_talent_buff.__dict__ != {}:
            if buff == "attack_speed":
                add_attack_speed = angel_talent_buff.__dict__["attack_speed"]
                angel.attack_speed = angel.attack_speed + add_attack_speed
                log = log + f"快速弹匣: attack_speed: +{add_attack_speed}"
                logger.info(log)
                log = "[天赋] "
            if buff == "atk":
                add_atk = angel_talent_buff.__dict__["atk"] * angel.base_atk
                angel.atk = angel.atk + add_atk
                log = log + f"天使的祝福: atk: +{add_atk} (+{add_atk})"
                logger.info(log)
                log = "[天赋] "
            if buff == "max_hp":
                add_max_hp = angel_talent_buff.__dict__["max_hp"] * angel.max_hp
                angel.max_hp = angel.max_hp + add_max_hp
                log = log + f"天使的祝福: max_hp: +{add_max_hp} (+{add_max_hp})"
                logger.info(log)
                log = "[天赋] "

    # 计算副职业加成
    for buff in angel_sub_profession_buff.__dict__:
        if angel_sub_profession_buff.__dict__ != {}:
            pass

    # 计算技能加成
    for buff in angel_skill_buff.__dict__:
        log = "[技能] "
        if angel_skill_buff.__dict__ != {}:
            if buff == "attack@atk_scale":
                skill_atk_scale = angel.skill_atk_scale * angel_skill_buff.__dict__["attack@atk_scale"]
                log = log + f"过载模式: atk_scale: {skill_atk_scale}x"
                logger.info(log)
                log = "[技能] "
            if buff == "attack@times":
                attack_times = angel_skill_buff.__dict__["attack@times"]
                log = log + f"过载模式: attack_times: {attack_times}"
                logger.info(log)
                log = "[技能] "
            if buff == "base_attack_time":
                angel.attack_time += angel_skill_buff.__dict__["base_attack_time"] * 2
                log = log + f"过载模式: 攻击间隔双倍减算"
                logger.info(log)
                log = "[技能] "

    logger.info(f"[面板 ] {angel.__dict__}")

    clear_buff_list()

    return im
