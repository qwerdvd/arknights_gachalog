import json

from ..cal_buff_list import get_character_skill_id
from ..character_class import Char, clear_buff_list


async def calculate_angel_damage(
    character_id: str,
    character_info: dict,
    buff_list: dict,
    skill_id: str,
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

    angel_uniequip_test = angel_buff.UniequipBuff(buff_list)
    angel_talent_test = angel_buff.TalentBuff(buff_list)
    angel_sub_profession_test = angel_buff.SubProfessionTraitBuff(buff_list)
    angel_skill_test = angel_buff.SkillBuff(buff_list)

    print(f"angel_uniequip_test is {angel_uniequip_test.__dict__}")
    print(f"angel_talent_test is {angel_talent_test.__dict__}")
    print(f"angel_sub_profession_test is {angel_sub_profession_test.__dict__}")
    print(f"angel_skill_test is {angel_skill_test.__dict__}")

    # 根据模组信息更新角色信息

    clear_buff_list()

    return im
