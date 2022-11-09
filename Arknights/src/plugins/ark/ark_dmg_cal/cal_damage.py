import json
import decimal

from decimal import Decimal
from .cal_full_trained_character_info import calculate_fully_trained_character_data
from .cal_buff_list import get_character_skill_id
from ..utils.alias.characterId_to_uniequipId import characterId_to_uniequipId


# TODO: 干员离弦伤害 (黑)

async def calculate_character_damage(
        characterId: str, character_info: dict, buff_list: dict, skill_id: int, profession: str, is_uniequip: bool,
        uniequip_id: str,
):
    print(character_info)
    print(buff_list)
    skill_id = await get_character_skill_id(characterId, skill_id)
    print(f"skill_id {skill_id}")
    print(f"profession {profession}")
    if is_uniequip:
        if uniequip_id == '一模':
            uniequip_id = 1
        elif uniequip_id == '二模':
            uniequip_id = 2
    equip_id = await characterId_to_uniequipId(characterId, uniequip_id)

    character_attribute_info = {
        'max_hp': character_info['base_hp'],
        'atk': character_info['base_atk'],
        'def': character_info['base_def'],
        'magic_resistance': character_info['base_magic_resistance'],
        'cost': character_info['base_cost'],
        'respawn_time': character_info['base_respawn_time'],
        'attack_speed': character_info['base_attack_speed'],
        'attack_time': character_info['base_attack_time'],
    }

    atk_scale = 1
    skill_attack_atk_scale = 1
    uniequip_atk_scale = 1
    talent_atk_scale = 1
    skill_atk_scale = 1
    damage_scale = 1

    base_atk = character_attribute_info['atk']
    add_atk = 0
    combo_attack_times = 1
    # 先计算模组 buff 加成
    uniequip_buff_list = buff_list["uniequip_buff_list"]
    for buff in uniequip_buff_list:
        if buff["key"] == "atk_scale":  # atk_scale 为攻击力倍率
            uniequip_atk_scale = atk_scale * buff["value"]
        elif buff["key"] == "damage_scale":
            damage_scale = damage_scale * (1 + buff["value"])

    # 再计算天赋 buff 加成
    talent_buff_list = buff_list["talent_buff_list"]
    for talent in talent_buff_list:
        for buff in talent:
            if buff["key"] == "atk":
                add_atk += base_atk * buff["value"]
            elif buff["key"] == "max_hp":
                character_attribute_info["max_hp"] = character_attribute_info["max_hp"] * (1 + buff["value"])
            elif buff["key"] == "attack_speed":
                character_attribute_info["attack_speed"] = character_attribute_info["attack_speed"] + buff["value"]
            elif buff["key"] == "atk_scale":
                talent_atk_scale = atk_scale * buff["value"]

    # 再计算技能 buff 加成
    skill_buff_list = buff_list["skill_buff_list"]
    for buff in skill_buff_list:
        print(buff)
        if buff["key"] == "attack@atk_scale":
            skill_attack_atk_scale = buff["value"]
        elif buff["key"] == "attack@times":  # attack@times 为攻击次数(连击)
            combo_attack_times = buff["value"]
        elif buff["key"] == "base_attack_time":  # base_attack_time 为攻击间隔
            if characterId == "char_103_angel" and skill_id == "skchr_angel_3":  # 能天使 3 技能攻击间隔双倍减少
                character_attribute_info["attack_time"] = character_attribute_info["attack_time"] + buff["value"] * 2
            else:
                character_attribute_info["attack_time"] = character_attribute_info["attack_time"] + buff["value"]
        elif buff["key"] == "atk":
            add_atk += base_atk * buff["value"]
        elif buff["key"] == "atk_scale":
            skill_atk_scale = atk_scale * buff["value"]
        elif buff["key"] == "bgsnow_s_3[atk_up].atk_scale":
            skill_atk_scale = atk_scale * buff["value"]
        elif buff["key"] == "damage_scale":
            damage_scale = damage_scale * buff["value"]

    print(atk_scale)
    character_attribute_info["atk"] = add_atk + base_atk
    print(character_attribute_info)
    final_atk_scale = uniequip_atk_scale * talent_atk_scale * skill_atk_scale * skill_attack_atk_scale
    final_atk = character_attribute_info["atk"] * final_atk_scale
    print(f"最终攻击力 (攻击力 * 倍率) 为 ({base_atk} + {add_atk}) * {final_atk_scale} = {final_atk}")
    raw_attack_time = character_attribute_info["attack_time"]
    print(f"攻击间隔为 {raw_attack_time}")
    final_attack_speed = character_attribute_info["attack_speed"]
    print(f"最终攻击速度为 {final_attack_speed}%")

    frame_rate = 30
    # 最终攻击间隔
    final_attack_time = raw_attack_time / (final_attack_speed / 100)
    final_attack_time_in_frame = final_attack_time * frame_rate
    print(f"最终攻击间隔: {final_attack_time_in_frame} 帧, {final_attack_time} 秒")

    # 对攻击间隔进行帧对齐 (对齐到 1 帧)
    frame_alignment_attack_interval = Decimal(final_attack_time_in_frame).quantize(
        Decimal("0"), rounding=decimal.ROUND_HALF_UP
    )
    frame_alignment_attack_time = frame_alignment_attack_interval / frame_rate
    print(f"帧对齐攻击间隔: {frame_alignment_attack_interval} 帧, {frame_alignment_attack_time} 秒")

    default_skill_forward = 12  # 默认前摇为 12 帧
    skill_duration = await get_skill_basic_info(characterId, skill_id, "duration")
    print(f"技能持续时间为 {skill_duration} 秒")
    total_duration_frame = skill_duration * frame_rate
    print(f"技能总持续帧数为 {total_duration_frame} 帧")
    attack_times = (total_duration_frame - default_skill_forward) / int(frame_alignment_attack_interval)
    print(f"攻击次数为 {attack_times} 次")
    total_attack_times = int(
        Decimal(attack_times).quantize(Decimal("0"), rounding=decimal.ROUND_CEILING)) * combo_attack_times
    print(f"总攻击次数为 {total_attack_times} 次")

    damage = final_atk * total_attack_times * damage_scale
    print(f"总伤害为 {damage}")

    im = f"{characterId}的{skill_id}技能带{equip_id}模组的总伤害为{damage}\n" \
         f"数据为:\n" \
         f"最终攻击力 (攻击力 * 倍率) 为 ({base_atk} + {add_atk}) * {final_atk_scale} = {final_atk}\n" \
         f"最终攻击间隔: {final_attack_time_in_frame} 帧, {final_attack_time} 秒\n" \
         f"帧对齐攻击间隔: {frame_alignment_attack_interval} 帧, {frame_alignment_attack_time} 秒\n" \
         f"技能持续时间为 {skill_duration} 秒\n" \
         f"总持续帧数为 {total_duration_frame} 帧\n" \
         f"攻击次数为 {attack_times} 次\n" \
         f"总攻击次数为 {total_attack_times} 次\n" \
         f"damage_scale为 {damage_scale}\n" \
         f"总伤害为 {damage}"

    return im


async def get_skill_basic_info(
        characterId: str, skill_id: int, params: str
) -> int:
    with open(f'src/plugins/ark/tool/data/character_skill_info/{characterId}.json', encoding='utf-8') as f:
        skill_basic_info = json.load(f)
    info = skill_basic_info[skill_id][params]
    return info
