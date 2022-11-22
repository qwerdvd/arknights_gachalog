import decimal
import json
import re
from decimal import Decimal

from .time_line import simulation_time_line
from ..utils.alias.characterId_to_uniequipId import characterId_to_uniequipId

from .cal_buff_list import get_character_skill_id

uniequip_buff_id_list = []
talent_buff_id_list = []
sub_profession_trait_buff_id_list = []
skill_buff_id_list = []
direct_addition_buff_list = ["attack_speed", "base_attack_time"]
direct_multiplication_buff_list = ["atk", "max_hp"]


async def clear_buff_list():
    uniequip_buff_id_list.clear()
    talent_buff_id_list.clear()
    sub_profession_trait_buff_id_list.clear()
    skill_buff_id_list.clear()


class CharacterBasicInfo:
    """
    CharacterBasicInfo: 角色基础信息
    max_hp: 最大生命值
    atk: 攻击力
    defense: 防御力
    magic_resistance: 魔抗
    cost: 花费
    respawn_time: 复活时间
    attack_speed: 攻击速度
    attack_time: 攻击间隔
    """

    def __init__(self, character_info):
        self.max_hp = character_info["base_hp"]
        self.atk = character_info["base_atk"]
        self.base_atk = character_info["base_atk"]
        self.defense = character_info["base_def"]
        self.magic_resistance = character_info["base_magic_resistance"]
        self.cost = character_info["base_cost"]
        self.respawn_time = character_info["base_respawn_time"]
        self.attack_speed = character_info["base_attack_speed"]
        self.attack_time = character_info["base_attack_time"]
        self.base_atk_scale = 1
        self.skill_atk_scale = 1

    def update_basic_attribute_by_direct_addition(self, key, value):
        add_atk = 0
        if key in direct_addition_buff_list:
            if key == "def":
                key = "defense"
            if key == "base_attack_time":
                key = "attack_time"
            if key == "atk":
                add_atk += self.__dict__[key] + value
            setattr(self, key, self.__dict__[key] + value)
        return add_atk

    def update_attribute_by_direct_multiplication(self, key, value):
        add_atk = 0
        if key in direct_multiplication_buff_list:
            if key == "atk":
                add_atk += self.__dict__[key] * value
            setattr(self, key, self.__dict__[key] * (1 + value))
        return add_atk

    def update_basic_attribute_with_skill_by_direct_addition(self, key, value, skill_id):
        if key in direct_addition_buff_list:
            if key == "def":
                key = "defense"
            if key == "base_attack_time":
                key = "attack_time"
                if skill_id == "skchr_angel_3":
                    value = value * 2
            setattr(self, key, self.__dict__[key] + value)

    def update_attribute_with_skill_by_direct_multiplication(self, key, value):
        skill_add_atk = 0
        if key in direct_multiplication_buff_list:
            if key == "atk":
                skill_add_atk += self.base_atk * value
            setattr(self, key, self.__dict__[key] * (1 + value))
        return skill_add_atk

    def update_attack_scale(self, value):
        self.base_atk_scale *= value


class CharacterSkillInfo:
    """
    skillType: 技能类型
    durationType: 持续时间类型
    duration: 持续时间
    spType: SP类型
    levelUpCost: 升级消耗
    maxChargeTime: 最大充能次数
    spCost: SP消耗
    initSp: 初始SP
    increment: SP增长
    blackboard: 技能效果
    """

    def __init__(self, skill_basic_info, skill_id):
        self.skillType = skill_basic_info[skill_id]["skillType"]
        self.durationType = skill_basic_info[skill_id]["durationType"]
        self.duration = skill_basic_info[skill_id]["duration"]
        self.spType = skill_basic_info[skill_id]["spData"]["spType"]
        self.levelUpCost = skill_basic_info[skill_id]["spData"]["levelUpCost"]
        self.maxChargeTime = skill_basic_info[skill_id]["spData"]["maxChargeTime"]
        self.spCost = skill_basic_info[skill_id]["spData"]["spCost"]
        self.initSp = skill_basic_info[skill_id]["spData"]["initSp"]
        self.increment = skill_basic_info[skill_id]["spData"]["increment"]
        self.blackboard = skill_basic_info[skill_id]["blackboard"]


def save_buff_key(key, buff_id):
    if buff_id == 1:
        if key not in uniequip_buff_id_list:
            uniequip_buff_id_list.append(key)
    elif buff_id == 2:
        if key not in talent_buff_id_list:
            talent_buff_id_list.append(key)
    elif buff_id == 3:
        if key not in sub_profession_trait_buff_id_list:
            sub_profession_trait_buff_id_list.append(key)
    elif buff_id == 4:
        if key not in skill_buff_id_list:
            skill_buff_id_list.append(key)


class UniequipBuff:
    def __init__(self, characterId, uniequip_buff_list):
        self.characterId = characterId
        for uniequip_buff in uniequip_buff_list:
            setattr(self, uniequip_buff["key"], uniequip_buff["value"])
            save_buff_key(uniequip_buff["key"], buff_id=1)


class TalentBuff:
    def __init__(self, characterId, talent_buff_list):
        self.characterId = characterId
        for talent_buff in talent_buff_list:
            for buff in talent_buff:
                setattr(self, buff["key"], buff["value"])
                save_buff_key(buff["key"], buff_id=2)


class SubProfessionTraitBuff:
    def __init__(self, characterId, sub_profession_trait_buff_list):
        self.characterId = characterId
        for sub_profession_trait_buff in sub_profession_trait_buff_list:
            setattr(self, sub_profession_trait_buff["key"], sub_profession_trait_buff["value"])
            save_buff_key(sub_profession_trait_buff["key"], buff_id=3)


class SkillBuff:
    def __init__(self, characterId, skill_buff_list):
        self.characterId = characterId
        for skill_buff in skill_buff_list:
            setattr(self, skill_buff["key"], skill_buff["value"])
            save_buff_key(skill_buff["key"], buff_id=4)


async def calculate_character_damage(
    characterId: str,
    character_info: dict,
    buff_list: dict,
    skill_id: int,
    profession: str,
    is_uniequip: bool,
    uniequip_id: str,
):
    im = []
    print(character_info)
    print(buff_list)
    skill_id = await get_character_skill_id(characterId, skill_id)
    print(f"skill_id {skill_id}")
    print(f"profession {profession}")
    if is_uniequip:
        if uniequip_id == "一模":
            uniequip_id = 1
        elif uniequip_id == "二模":
            uniequip_id = 2
        uniequip_id = await characterId_to_uniequipId(characterId, uniequip_id)
    else:
        uniequip_id = None

    im.append(f"计算{characterId}的{skill_id}技能带{uniequip_id}模组的伤害\n")
    character = CharacterBasicInfo(character_info)

    with open(
        f"src/plugins/ark/tool/data/character_skill_info/{characterId}.json",
        encoding="utf-8",
    ) as f:
        skill_basic_info = json.load(f)
    skill = CharacterSkillInfo(skill_basic_info, skill_id)
    print(skill.__dict__)

    atk_scale = 1
    sub_profession_talent_atk_scale = 1
    uniequip_atk_scale = 1
    talent_atk_scale = 1
    damage_scale = 1

    total_duration_frame = 0

    base_atk = character.base_atk
    add_atk = 0
    combo_attack_times = 0
    total_attack_times = 1

    off_string_damage = 0
    damage = 0

    print(buff_list["uniequip_buff_list"])
    uniequip_test, talent_test, sub_profession_trait_test, skill_test = await update_character_arb_info(
        characterId, buff_list
    )
    skill_buff_list = buff_list["skill_buff_list"]

    print(character.__dict__)
    # 基础属性的计算
    # 并记录原始攻击力与增加的攻击力
    base_atk_teat, add_atk_test, skill_add_atk = await update_character_attribute_info(
        character, uniequip_test, talent_test, sub_profession_trait_test, skill_test, skill_id
    )
    print(f"base_atk_teat: {base_atk_teat} add_atk: {add_atk_test} skill_add_atk: {skill_add_atk}")

    await update_character_atk_scale(
        character,
        uniequip_test,
        talent_test,
        sub_profession_trait_test,
        skill_test,
    )

    frame_rate = 30
    for buff in talent_test.__dict__:
        buff_split = re.split("[\[\]\.]", buff)
        print(buff_split)
        if len(buff_split) == 2:
            buff_type = buff_split[0]
            buff_id = buff_split[1]
        if len(buff_split) > 2:
            buff_type = buff_split[1]
            buff_id = buff_split[3]
            print(buff_type, buff_id)
            if buff_type == "withdraw":
                if buff_id == "interval":
                    blood_lock_time = talent_test.__dict__[buff] * frame_rate
    for buff in skill_test.__dict__:
        buff_split_1 = re.split("@", buff)
        buff_split_2 = re.split("[\[\]\.]", buff)
        if len(buff_split_1) > 1:
            buff_type = buff_split_1[0]
            buff_id = buff_split_1[1]
            print(buff_type, buff_id)
            if buff_type == "attack":  # attack@ 类型的buff
                if buff_id == "max_target":  # attack@max_target
                    im.append(f"最大攻击目标数: {skill_test.__dict__[buff]}\n")
                elif buff_id == "times":  # attack@times
                    combo_attack_times = skill_test.__dict__[buff]
                    im.append(f"攻击次数: {combo_attack_times}\n")
                elif buff_id == "atk_scale":  # attack@atk_scale
                    character.skill_atk_scale = character.skill_atk_scale * skill_test.__dict__[buff]
                    im.append(f"攻击力提升至: {character.skill_atk_scale * 100}%\n")
                elif buff_id == "trigger_time":  # attack@trigger_time
                    attack_trigger_time = skill_test.__dict__[buff]
                elif buff_id == "move_speed":  # attack@move_speed
                    pass
                elif buff_id == "def":  # attack@def
                    pass
                elif buff_id == "projectile_life_time":  # attack@projectile_life_time
                    pass
        if len(buff_split_2) > 1:
            buff_type = buff_split_2[1]
            buff_id = buff_split_2[3]
            print(buff_type, buff_id)
            if buff_type == "atk_up":
                if buff_id == "atk_scale":
                    character.skill_atk_scale = skill_test.__dict__[buff]
                    im.append(f"攻击力提升: {skill_test.__dict__[buff]}\n")

    basic_attack_damage = (
        character.atk
        * atk_scale
        * talent_atk_scale
        * uniequip_atk_scale
        * damage_scale
        * sub_profession_talent_atk_scale
    )

    print(character.base_atk_scale, character.skill_atk_scale)
    print(character.__dict__)
    character.atk = base_atk + add_atk_test + skill_add_atk
    final_atk_scale = character.base_atk_scale * character.skill_atk_scale
    final_atk = character.atk * final_atk_scale

    if skill_id == "skchr_amgoat_2":
        # 技能实际效果为先削减主攻击目标的法术抗性，再对爆炸范围内所有敌人造成½倍率的伤害(包括主攻击目标)
        # 最后对主攻击目标额外造成一次½倍率的伤害
        final_atk = final_atk * 2
        im.append(f"艾雅法拉二技能实际效果为先削减主攻击目标的法术抗性,再对爆炸范围内所有敌人造成½倍率的伤害(包括主攻击目标),最后对主攻击目标额外造成一次½倍率的伤害\n")
        im.append(
            f"最终攻击力 (攻击力 * 倍率) 为 ({base_atk} + {add_atk_test} + {skill_add_atk}) * {final_atk_scale * 2} = {final_atk}\n"
        )
        print(
            f"最终攻击力 (攻击力 * 倍率) 为 ({base_atk} + {add_atk_test} + {skill_add_atk}) * {final_atk_scale * 2} = {final_atk}"
        )
    else:
        im.append(
            f"最终攻击力 (攻击力 * 倍率) 为 ({base_atk} + {add_atk_test} + {skill_add_atk}) * {final_atk_scale} = {final_atk}\n"
        )
        print(f"最终攻击力 (攻击力 * 倍率) 为 ({base_atk} + {add_atk_test} + {skill_add_atk}) * {final_atk_scale} = {final_atk}")
    raw_attack_time = character.attack_time
    print(f"攻击间隔为 {raw_attack_time}")
    final_attack_speed = character.attack_speed
    print(f"最终攻击速度为 {final_attack_speed}%")

    # 最终攻击间隔
    final_attack_time = raw_attack_time / (final_attack_speed / 100)
    final_attack_time_in_frame = final_attack_time * frame_rate
    im.append(f"最终攻击间隔: {final_attack_time_in_frame} 帧, {final_attack_time} 秒\n")
    print(f"最终攻击间隔: {final_attack_time_in_frame} 帧, {final_attack_time} 秒")

    # 对攻击间隔进行帧对齐 (对齐到 1 帧)
    frame_alignment_attack_interval = Decimal(final_attack_time_in_frame).quantize(
        Decimal("0"), rounding=decimal.ROUND_HALF_UP
    )
    if skill_id in ["skchr_amgoat_3", "skchr_amgoat_2"]:
        frame_alignment_attack_interval += 1
        frame_alignment_attack_time = frame_alignment_attack_interval / frame_rate
        print(f"技能 {skill_id} 由于需要补帧, 所以补正后的攻击间隔为 {frame_alignment_attack_interval}")
        im.append(
            f"技能 {skill_id} 由于需要补帧, 所以补正后的攻击间隔为 {frame_alignment_attack_interval} 帧, {frame_alignment_attack_time} 秒\n"
        )
    else:
        frame_alignment_attack_time = frame_alignment_attack_interval / frame_rate
        im.append(f"帧对齐后的攻击间隔: {frame_alignment_attack_interval} 帧, {frame_alignment_attack_time} 秒\n")

    default_skill_forward = 12  # 默认前摇为 12 帧

    print(f"技能持续时间为 {skill.duration} 秒")

    if combo_attack_times == 0:
        combo_attack_times = 1

    is_special_treatment = False

    # 特殊处理弹药类技能
    if characterId in ["char_1013_chen2", "char_4039_horn"]:
        im.append("弹药类技能特殊处理\n")
        is_special_treatment = True
        str_time_line = ""
        skill_buff_list = buff_list["skill_buff_list"]
        hand_up_time = 12  # 抬手 12 帧
        prob_add_attack_trigger_time = 0
        if skill.duration > 0:
            if characterId == "char_4039_horn":  # 号角触发血战
                (
                    first_stage_duration,
                    first_stage_atk_times,
                    first_stage_damage,
                    overload_add_atk,
                    second_stage_atk,
                    second_stage_duration,
                    second_stage_atk_times,
                    second_stage_damage,
                ) = await deal_with_horn_skill_damage(
                    skill_buff_list,
                    base_atk,
                    final_atk,
                    skill.duration,
                    frame_rate,
                    frame_alignment_attack_interval,
                    final_atk_scale,
                )
                im.append("号角默认触发血战,过载伤害分两段计算\n")
                im.append(f"不触发过载时攻击力(攻击力 * 倍率)为 ({base_atk} + {add_atk_test}) * {final_atk_scale} = {final_atk}\n")
                im.append(f"不触发过载时持续时间为 {first_stage_duration}\n")
                im.append(f"不触发过载时攻击次数为 {first_stage_atk_times}\n")
                im.append(f"不触发过载时伤害为 {first_stage_damage}\n")
                im.append(
                    f"触发过载时攻击力(攻击力 * 倍率)为 ({base_atk} + {overload_add_atk}) * {final_atk_scale} = {second_stage_atk}\n"
                )
                im.append(f"触发过载时持续时间为 {second_stage_duration}\n")
                im.append(f"触发过载时攻击次数为 {second_stage_atk_times}\n")
                im.append(f"触发过载时伤害为 {second_stage_damage}\n")
                # 总伤害
                damage = first_stage_damage + second_stage_damage
            else:
                total_skill_duration = skill.duration
                attack_trigger_time = skill.duration * frame_rate / float(frame_alignment_attack_interval)
                attack_time = Decimal(attack_trigger_time / 2).quantize(Decimal("0"), rounding=decimal.ROUND_CEILING)
                im.append(f"攻击次数为 {attack_time} 次\n")
                im.append(f"技能持续时间为 {total_skill_duration} 秒\n")
                damage = final_atk * int(attack_time) * damage_scale
        else:
            if characterId == "char_1013_chen2":  # 天赋多计入 4 发弹药
                prob_add_attack_trigger_time = 4
                im.append("水陈天赋多计入 4 发弹药\n")
            attack_time = (attack_trigger_time / 2 + prob_add_attack_trigger_time) * 2  # 一次消耗 2 发弹药
            attack_interval = int(frame_alignment_attack_interval)  # 帧对齐后的攻击间隔(帧)
            total_skill_duration = (attack_time * attack_interval + hand_up_time) / frame_rate  # 技能持续时间(秒)
            im.append(f"攻击次数为 {attack_time} 次\n")
            im.append(f"技能持续时间为 {total_skill_duration} 秒\n")
            damage = final_atk * int(attack_time) * damage_scale
    elif skill.duration > 0 and not is_special_treatment:
        total_duration_frame = skill.duration * frame_rate
        attack_times = (total_duration_frame - default_skill_forward) / int(frame_alignment_attack_interval)
        total_attack_times = (
            int(Decimal(attack_times).quantize(Decimal("0"), rounding=decimal.ROUND_CEILING)) * combo_attack_times
        )
        print(f"攻击次数为 {total_attack_times} 次")
        damage = final_atk * total_attack_times * damage_scale + off_string_damage
    elif skill.duration == -1 and not is_special_treatment:  # -1 表示为永续技能或者是次数技能
        default_simulation_time = 120
        default_spine_duration_frame = 48  # 默认动画持续时间(帧)
        if skill_id == "skchr_amgoat_2":
            default_spine_duration_frame = 36
        im.append(f"技能持续时间为永久, 模拟时间为 {default_simulation_time} 秒\n")
        total_duration_frame = default_simulation_time * frame_rate
        im.append(f"在模拟的情况下技能总持续帧数为 {total_duration_frame} 帧\n")
        str_time_line = ""
        str_time_line = await simulation_time_line(
            character,
            skill,
            frame_alignment_attack_time,
            default_spine_duration_frame,
        )
        # 特殊处理史尔特尔的技能
        if characterId == "char_350_surtr" and skill_id == "skchr_surtr_3":
            max_hp = character.max_hp
            loss_time, attack_interval = await deal_with_surtr_third_skill(
                max_hp,
                frame_rate,
                frame_alignment_attack_interval,
                skill_buff_list,
            )
            im.append(f"损失100%血量共耗时 {loss_time} 帧 {loss_time / frame_rate} 秒\n")
            # 计算总共输出时间
            total_output_time = loss_time + blood_lock_time
            im.append(f"总输出时间为 {total_output_time} 帧\n")
            # 计算总共输出次数
            total_output_times = int(
                Decimal(total_output_time / float(attack_interval)).quantize(
                    Decimal("0"), rounding=decimal.ROUND_CEILING
                )
            )
            im.append(f"总输出次数为 {total_output_times} 次\n")
            str_time_line = ""
            damage = final_atk * total_output_times * damage_scale

        if str_time_line != "":
            print(str_time_line)
            im.append(f"时间轴为 {str_time_line}\n")
            basic_attack_number = str_time_line.count("-")
            skill_attack_number = str_time_line.count("+")
            if basic_attack_number != 0:
                im.append(f"普攻次数为 {basic_attack_number} 次\n")
            if skill_attack_number != 0:
                im.append(
                    f"技能次数为 {combo_attack_times}连击 * {skill_attack_number} = {skill_attack_number * combo_attack_times} 次\n"
                )
            basic_attack_number = basic_attack_damage * basic_attack_number
            skill_attack_number = final_atk * total_attack_times * skill_attack_number * combo_attack_times
            damage = basic_attack_number + skill_attack_number
            im.append(f"普攻伤害为 {basic_attack_number}\n")
            im.append(f"技能伤害为 {skill_attack_number}\n")
    elif skill.duration == 0:  # 表示瞬发技能
        damage = final_atk

    if damage_scale != 1:
        im.append(f"damage_scale为 {damage_scale}\n")
    im.append(f"总伤害为 {damage}")
    print(f"总伤害为 {damage}")

    # 特殊处理黑键伤害计算
    if characterId == "char_4046_ebnhlz":
        single_attack_damage, mata_full_damage = await deal_with_ebnhlz_skill_damage(
            character,
            add_atk_test,
            base_atk,
            uniequip_id,
            buff_list,
            total_attack_times,
            skill_id,
        )

        default_simulation_time = total_duration_frame

        str_time_line = await get_ebnhlz_third_skill_time_line(
            default_simulation_time, frame_alignment_attack_interval, uniequip_id
        )

        _attack_time = str.count(str_time_line, "+-")

        damage = single_attack_damage * _attack_time

        im = (
            f"计算{characterId}的{skill_id}技能带{uniequip_id}模组的伤害\n"
            f"最终攻击力 (攻击力 * 倍率) 为 ({base_atk} + {add_atk_test}) * 1 = {final_atk}\n"
            f"最终攻击间隔: {final_attack_time_in_frame} 帧, {final_attack_time} 秒"
            f"帧对齐后的攻击间隔: {frame_alignment_attack_interval} 帧, {frame_alignment_attack_time} 秒\n"
            f"攻击模式为攒满球再加一次普攻\n"
            f"攒满球的伤害为: {mata_full_damage}\n"
            f"时间轴为 {str_time_line}\n"
            f"满蓄力+普攻伤害 {single_attack_damage}\n"
            f"攻击次数为 {_attack_time} 次\n"
            f"总伤害为 {damage}"
        )

    await clear_buff_list()

    return im


async def deal_with_surtr_third_skill(
    max_hp: int,
    frame_rate: int,
    frame_alignment_attack_interval: Decimal,
    skill_buff_list: list,
):
    hp_ratio = 0
    duration = 0
    interval = 0

    attack_interval = frame_alignment_attack_interval

    for buff in skill_buff_list:
        if buff["key"] == "interval":  # 生命流失结算间隔
            interval = buff["value"] * frame_rate
        elif buff["key"] == "hp_ratio":  # 生命流失最大比例
            hp_ratio = buff["value"]
        elif buff["key"] == "duration":  # 生命流失达到最大比例时间
            duration = buff["value"] * frame_rate

    # 计算生命流失过程
    current_hp = max_hp
    loss_time = 0
    init_loss_hp = 0
    timer = 0

    while current_hp > 0:
        timer += 1
        # 计算每 0.2 * 30 = 6 帧的生命流失
        hp_loss = (
            (max_hp * hp_ratio) / (duration * frame_rate)
        ) * interval * timer * interval * timer / 2 - init_loss_hp
        # 计算剩余血量
        current_hp = current_hp - hp_loss
        init_loss_hp = init_loss_hp + hp_loss
        # 计算生命值 > 0 的情况下的时间
        loss_time = loss_time + interval

    return loss_time, attack_interval


async def get_ebnhlz_third_skill_time_line(
    default_simulation_time: int,
    frame_alignment_attack_interval: Decimal,
    uniequip_id: str,
) -> str:
    time_line = []

    # 总帧数
    total_duration_frame = default_simulation_time
    # 攻击间隔 (帧)
    attack_interval = frame_alignment_attack_interval
    print("attack_interval", attack_interval)
    # 技能前摇
    skill_forward_frame = 10
    frame = 1
    timer = 0  # 初始化计时器
    # 攒球计数器
    ball_save_number = 0
    if uniequip_id == "uniequip_002_ebnhlz":
        max_ball_save_number = 4
    else:
        max_ball_save_number = 3
    while frame <= total_duration_frame:
        # 默认第一帧开技能
        is_first_skill_spine = True if frame == 1 else False
        if is_first_skill_spine:
            frame = frame + skill_forward_frame
            time_line.append("+")  # "+"表示技能
            frame = frame + attack_interval
            time_line.append("-")  # "-"表示普攻
        while 1:
            if frame <= total_duration_frame:
                basic_attack_number = 1  # 初始化普攻计数器
                skill_attack_number = 1  # 初始化技能计数器
                # 进行一次攒球
                timer += attack_interval
                frame += attack_interval
                # 攒球计数器 +1
                ball_save_number += 1
                time_line.append("0")  # "0"表示攒球
                # 判断是否达到技能所需 sp
                if ball_save_number >= max_ball_save_number:
                    # 进行一次技能攻击
                    frame += attack_interval
                    # 技能计数器 +1
                    skill_attack_number += 1
                    time_line.append("+")  # "+"表示技能
                    # 进行一次普攻
                    frame += attack_interval
                    # 普攻计数器 +1
                    basic_attack_number += 1
                    time_line.append("-")  # "-"表示普攻
                    # 计时器清零
                    ball_save_number = 0
            else:
                break

    str_time_line = "".join(time_line)
    im = str_time_line

    return im


async def deal_with_ebnhlz_skill_damage(
    character: CharacterBasicInfo,
    add_atk_test: int,
    base_atk: int,
    uniequip_id: str,
    buff_list: dict,
    total_attack_times: int,
    skill_id: str,
):
    character.atk = add_atk_test + base_atk
    final_atk = character.atk * 1  # 黑键攻击力倍率为 1
    if uniequip_id == "uniequip_002_ebnhlz":
        default_combo_attack_times = 5  # 一模黑键连击次数为 4 + 1
    else:
        default_combo_attack_times = 4

    # 获取黑键 1 天赋伤害倍率
    talent_1_buff_list = buff_list["talent_buff_list"][0]
    talent_1_atk_scale = 1
    for buff in talent_1_buff_list:
        if buff["key"] == "atk_scale":
            talent_1_atk_scale = buff["value"]

    # 获取黑键 2 天赋伤害倍率
    talent_2_buff_list = buff_list["talent_buff_list"][1]
    talent_2_atk_scale = 1
    for buff in talent_2_buff_list:
        if buff["key"] == "atk_scale":
            talent_2_atk_scale = buff["value"]

    talent_2_append_damage = final_atk * talent_2_atk_scale * total_attack_times

    talent_scale_multiplier = 1
    if skill_id == "skchr_ebnhlz_3":  # 黑键 3 技能对天赋 1 的攻击力倍率影响为 直接乘算
        skill_buff_list = buff_list["skill_buff_list"]
        for buff in skill_buff_list:
            if buff["key"] == "talent_scale_multiplier":
                talent_scale_multiplier = buff["value"]
    talent_1_scale_multiplied = talent_1_atk_scale * talent_scale_multiplier

    # 假如攒满 3 个球再攻击
    # 则此次伤害为 3 个球的伤害加上刚转好的 1 个球的伤害
    # 再加上天赋 2 的伤害
    mata_full_damage = final_atk * talent_1_scale_multiplied * default_combo_attack_times + talent_2_append_damage

    # 假设攻击模式为 攒满球 + 1 次普攻 循环
    single_attack_damage = mata_full_damage + final_atk * talent_2_atk_scale * 1

    return single_attack_damage, mata_full_damage


async def deal_with_horn_skill_damage(
    skill_buff_list: dict,
    base_atk: int,
    final_atk: int,
    skill: CharacterSkillInfo,
    frame_rate: int,
    frame_alignment_attack_interval: Decimal,
    final_atk_scale_with_crit: int,
):
    talent_1_buff_atk = 0.23
    talent_2_buff_attack_speed = 21
    for buff in skill_buff_list:
        if buff["key"] == "horn_s_3[overload_start].atk":
            horn_s_3_overload_start_atk = buff["value"]
            overload_add_atk = base_atk * horn_s_3_overload_start_atk * (1 + talent_1_buff_atk)
        elif buff["key"] == "horn_s_3[overload_start].interval":
            horn_s_3_overload_start_interval = buff["value"]
        elif buff["key"] == "horn_s_3[overload_start].hp_ratio":
            horn_s_3_overload_start_hp_ratio = buff["value"]
        elif buff["key"] == "horn_s_3[overload_start].damage_duration":
            horn_s_3_overload_start_damage_duration = buff["value"]
    # 号角伤害分为两段, 第一段不触发过载, 第二段触发过载
    # 第一段伤害
    first_stage_atk = final_atk  # 第一段伤害的攻击力
    first_stage_duration = skill.duration - horn_s_3_overload_start_damage_duration  # 第一段持续时间
    first_stage_atk_times = Decimal(
        first_stage_duration * frame_rate / float(frame_alignment_attack_interval)
    ).quantize(
        Decimal("0"), rounding=decimal.ROUND_CEILING
    )  # 第一段攻击次数
    first_stage_damage = first_stage_atk * int(first_stage_atk_times)  # 第一段伤害
    # 第二段伤害
    second_stage_atk = (base_atk + overload_add_atk) * final_atk_scale_with_crit  # 第二段伤害的攻击力
    second_stage_duration = horn_s_3_overload_start_damage_duration  # 第二段持续时间
    second_stage_atk_times = Decimal(
        second_stage_duration * frame_rate / float(frame_alignment_attack_interval)
    ).quantize(
        Decimal("0"), rounding=decimal.ROUND_CEILING
    )  # 第二段攻击次数
    second_stage_damage = second_stage_atk * int(second_stage_atk_times)  # 第二段伤害

    return (
        first_stage_duration,
        first_stage_atk_times,
        first_stage_damage,
        overload_add_atk,
        second_stage_atk,
        second_stage_duration,
        second_stage_atk_times,
        second_stage_damage,
    )


async def update_character_attribute_info(
    character: CharacterBasicInfo,
    uniequip_test: UniequipBuff,
    talent_test: TalentBuff,
    sub_profession_trait_test: SubProfessionTraitBuff,
    skill_test: SkillBuff,
    skill_id: str,
):
    atk = character.base_atk
    add_atk = 0
    skill_add_atk = 0
    # 属性中的直接加算部分
    for buff_key in uniequip_buff_id_list:
        if buff_key in uniequip_test.__dict__:
            add_atk += character.update_basic_attribute_by_direct_addition(buff_key, uniequip_test.__dict__[buff_key])
    for buff_key in talent_buff_id_list:
        if buff_key in talent_test.__dict__:
            add_atk += character.update_basic_attribute_by_direct_addition(buff_key, talent_test.__dict__[buff_key])
    for buff_key in sub_profession_trait_buff_id_list:
        if buff_key in sub_profession_trait_test.__dict__:
            add_atk += character.update_basic_attribute_by_direct_addition(
                buff_key, sub_profession_trait_test.__dict__[buff_key]
            )
    for buff_key in skill_buff_id_list:
        if buff_key in skill_test.__dict__:
            character.update_basic_attribute_with_skill_by_direct_addition(
                buff_key, skill_test.__dict__[buff_key], skill_id
            )

    # 属性中的直接乘算部分
    for buff_key in uniequip_buff_id_list:
        if buff_key in uniequip_test.__dict__:
            add_atk += character.update_attribute_by_direct_multiplication(buff_key, uniequip_test.__dict__[buff_key])
    for buff_key in talent_buff_id_list:
        if buff_key in talent_test.__dict__:
            add_atk += character.update_attribute_by_direct_multiplication(buff_key, talent_test.__dict__[buff_key])
    for buff_key in sub_profession_trait_buff_id_list:
        if buff_key in sub_profession_trait_test.__dict__:
            add_atk += character.update_attribute_by_direct_multiplication(
                buff_key, sub_profession_trait_test.__dict__[buff_key]
            )
    for buff_key in skill_buff_id_list:
        if buff_key in skill_test.__dict__:
            skill_add_atk += character.update_attribute_with_skill_by_direct_multiplication(
                buff_key, skill_test.__dict__[buff_key]
            )

    return atk, add_atk, skill_add_atk


async def update_character_atk_scale(
    character: CharacterBasicInfo,
    uniequip_test: UniequipBuff,
    talent_test: TalentBuff,
    sub_profession_trait_test: SubProfessionTraitBuff,
    skill_test: SkillBuff,
):
    for buff_key in uniequip_buff_id_list:
        if buff_key == "atk_scale" and buff_key in uniequip_test.__dict__:
            character.base_atk_scale = character.base_atk_scale * uniequip_test.__dict__[buff_key]
    for buff_key in talent_buff_id_list:
        if buff_key == "atk_scale" and buff_key in talent_test.__dict__:
            character.base_atk_scale = character.base_atk_scale * talent_test.__dict__[buff_key]
    for buff_key in sub_profession_trait_buff_id_list:
        if buff_key == "atk_scale" and buff_key in sub_profession_trait_test.__dict__:
            character.base_atk_scale = character.base_atk_scale * sub_profession_trait_test.__dict__[buff_key]

    for buff_key in skill_buff_id_list:
        if buff_key == "atk_scale" and buff_key in skill_test.__dict__:
            character.skill_atk_scale = character.skill_atk_scale * skill_test.__dict__[buff_key]


async def update_character_arb_info(characterId: str, buff_list: dict):
    # 先计算模组 buff 加成
    uniequip_buff_list = buff_list["uniequip_buff_list"]
    uniequip_test = UniequipBuff(characterId, uniequip_buff_list)
    print(uniequip_test.__dict__)

    # 再计算天赋 buff 加成
    talent_buff_list = buff_list["talent_buff_list"]
    talent_test = TalentBuff(characterId, talent_buff_list)
    print(talent_test.__dict__)

    # 再计算子职业特性 buff 加成
    sub_profession_trait_buff_list = buff_list["sub_profession_trait_buff_list"]
    sub_profession_trait_test = SubProfessionTraitBuff(characterId, sub_profession_trait_buff_list)
    print(sub_profession_trait_test.__dict__)

    # 再计算技能 buff 加成
    skill_buff_list = buff_list["skill_buff_list"]
    skill_test = SkillBuff(characterId, skill_buff_list)
    print(skill_test.__dict__)

    return uniequip_test, talent_test, sub_profession_trait_test, skill_test
