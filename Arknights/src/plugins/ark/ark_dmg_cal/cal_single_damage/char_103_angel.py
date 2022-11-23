import json

from ..cal_buff_list import get_character_skill_id
from ..cal_damage import (
    UniequipBuff,
    TalentBuff,
    SubProfessionTraitBuff,
    SkillBuff,
    CharacterBasicInfo,
    CharacterSkillInfo,
    clear_buff_list,
)

from ...utils.alias.characterId_to_uniequipId import characterId_to_uniequipId


async def calculate_angel_damage(
    character_id: str,
    character_info: dict,
    buff_list: dict,
    skill_id: str,
    is_uniequip: bool,
    uniequip_id: str,
) -> list:
    im = []
    skill_id = await get_character_skill_id(character_id, skill_id)
    if is_uniequip:
        if uniequip_id == "一模":
            uniequip_id = 1
        elif uniequip_id == "二模":
            uniequip_id = 2
        uniequip_id = await characterId_to_uniequipId(character_id, uniequip_id)
    else:
        uniequip_id = None

    with open(
        f"src/plugins/ark/tool/data/character_skill_info/{character_id}.json",
        encoding="utf-8",
    ) as f:
        skill_basic_info = json.load(f)
    character = CharacterBasicInfo(character_info)
    skill = CharacterSkillInfo(skill_basic_info, skill_id)

    uniequip_test = UniequipBuff(character_id, buff_list)
    talent_test = TalentBuff(character_id, buff_list)
    sub_profession_test = SubProfessionTraitBuff(character_id, buff_list)
    skill_test = SkillBuff(character_id, buff_list)

    print(f"uniequip_test is {uniequip_test.__dict__}")
    print(f"talent_test is {talent_test.__dict__}")
    print(f"sub_profession_test is {sub_profession_test.__dict__}")
    print(f"skill_test is {skill_test.__dict__}")

    # 根据模组信息更新角色信息

    await clear_buff_list()

    return im
