import json

from .cal_full_trained_character_info import get_uniequip_talent_adjustment


async def calculate_talent_buff(characterId: str, is_uniequip: bool, uniequip_id: str):
    with open(
        f"src/plugins/ark/tool/data/character_talent_info/{characterId}.json",
        encoding="UTF-8",
    ) as f:
        character_talent_info = json.load(f)
    if is_uniequip:
        if uniequip_id == "一模":
            uniequip_id = 1
        elif uniequip_id == "二模":
            uniequip_id = 2
    # 先默认取最高天赋加成
    for i in range(len(character_talent_info)):
        talent = character_talent_info[f"{i + 1}"]["candidates"][-1]
        # 假如有模组，需要覆写天赋加成
        target = "TALENT"
        if is_uniequip:
            override_talent_data = await get_uniequip_talent_adjustment(characterId, uniequip_id, target)
            print(f"override_talent_data {override_talent_data}")
            if override_talent_data:
                override_talent_index = override_talent_data["talent_index"]  # 覆写的天赋索引
                override_talent = override_talent_data["blackboard"]  # 覆写的天赋加成

                # 计算潜能对天赋加成的影响
                raw_talent_without_potential = character_talent_info[f"{override_talent_index + 1}"]["candidates"][0]
                raw_talent_with_potential = character_talent_info[f"{override_talent_index + 1}"]["candidates"][1]
                without_potential = raw_talent_without_potential["blackboard"]
                with_potential = raw_talent_with_potential["blackboard"]
                potential_add = []
                for item in with_potential:
                    key = item["key"]
                    for item2 in without_potential:
                        if key == item2["key"]:
                            raw_potential_add = item["value"] - item2["value"]
                            potential_add.append({"key": item["key"], "value": raw_potential_add})

                # 进行天赋的覆写加成
                if i == override_talent_index:
                    talent["blackboard"] = override_talent

        character_talent_info[f"{i + 1}"]["candidates"][-1] = talent
    # print(f"c_t_i: {character_talent_info}")

    return character_talent_info
