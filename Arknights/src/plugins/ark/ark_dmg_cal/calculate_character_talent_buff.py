import json
from .cal_full_trained_character_info import get_equip_talent_adjustment


async def calculate_talent_buff(characterId: str, is_equip: bool, uniequip_id: str):
    with open(f'src/plugins/ark/tool/data/character_talent_info/{characterId}.json', encoding='UTF-8') as f:
        character_talent_info = json.load(f)
    # 先默认取最高天赋加成
    for i in range(len(character_talent_info)):
        talent = character_talent_info[f"{i + 1}"]["candidates"][-1]
        # 假如有模组，需要覆写天赋加成
        target = "TALENT"
        if is_equip:
            if uniequip_id == '一模':
                uniequip_id = 1
            elif uniequip_id == '二模':
                uniequip_id = 2
            override_talent_data = await get_equip_talent_adjustment(characterId, uniequip_id, target)
            override_talent_index = override_talent_data["talent_index"]  # 覆写的天赋索引
            print(override_talent_index)
            override_talent = override_talent_data["blackboard"]  # 覆写的天赋加成
            print(override_talent)

            # 计算模组覆写后的天赋加成
            if i == override_talent_index:
                talent["blackboard"] = override_talent
        print(talent)

    return 0
