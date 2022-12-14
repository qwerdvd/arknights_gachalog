import json
from typing import Optional

from .cal_character_info import get_uniequip_adjustment
from .calculate_character_talent_buff import calculate_talent_buff


async def get_buff_list(characterId: str, is_uniequip: bool, uniequip_id: str, skill_id: str) -> Optional[dict]:
    buff_list = {}

    # 模组 buff
    # 暂时为特性追加部分
    uniequip_buff_list = []
    if is_uniequip:
        if uniequip_id == "一模":
            uniequip_id = 1
        elif uniequip_id == "二模":
            uniequip_id = 2
        raw_uniequip_trait_data = await get_uniequip_adjustment(characterId, uniequip_id, "TRAIT")
        raw_uniequip_display_data = await get_uniequip_adjustment(characterId, uniequip_id, "DISPLAY")
        for trait in raw_uniequip_trait_data:
            uniequip_buff_list.append(trait)
        for display in raw_uniequip_display_data:
            uniequip_buff_list.append(display)
    buff_list["uniequip_buff_list"] = uniequip_buff_list

    # 天赋 buff
    talent_buff_list = []
    if is_uniequip:
        if uniequip_id == "一模":
            uniequip_id = 1
        elif uniequip_id == "二模":
            uniequip_id = 2
    else:
        uniequip_id = None
    raw_talent_buff = await calculate_talent_buff(characterId, is_uniequip, uniequip_id)
    for i in range(len(raw_talent_buff)):
        talent = raw_talent_buff[f"{i + 1}"]["candidates"][-1]
        single_talent_buff = talent["blackboard"]
        talent_buff_list.append(single_talent_buff)
    print(talent_buff_list)
    buff_list["talent_buff_list"] = talent_buff_list

    # 技能 buff
    skill_buff_list = []
    with open(
        f"src/plugins/ark/tool/data/character_skill_info/{characterId}.json",
        encoding="UTF-8",
    ) as f:
        character_skill_info = json.load(f)
    character_skill_id = await get_character_skill_id(characterId, skill_id)
    character_skill = character_skill_info[character_skill_id]
    for buff in character_skill["blackboard"]:
        skill_buff_list.append(buff)
    buff_list["skill_buff_list"] = skill_buff_list

    # 子职业特性 buff
    sub_profession_trait_buff_list = []
    with open(
        f"src/plugins/ark/tool/data/basic_character_info/{characterId}.json",
        encoding="UTF-8",
    ) as f:
        character_info = json.load(f)
    sub_profession_id = character_info["subProfessionId"]
    if character_info["trait"] is not None:
        for i in range(len(character_info["trait"]["candidates"][0]["blackboard"])):
            sub_profession_trait = character_info["trait"]["candidates"][0]["blackboard"][i]
            sub_profession_trait_buff_list.append(sub_profession_trait)
    buff_list["sub_profession_trait_buff_list"] = sub_profession_trait_buff_list

    return buff_list


async def get_character_skill_id(characterId: str, skill_id: str):
    with open(
        f"src/plugins/ark/tool/data/skill_number_to_skill_id/{characterId}.json",
        encoding="UTF-8",
    ) as f:
        character_skill_info = json.load(f)
    character_skill_id = character_skill_info[skill_id]
    return character_skill_id
