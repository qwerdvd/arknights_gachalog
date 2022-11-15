import decimal
import json
from decimal import Decimal

from ..utils.alias.characterId_to_uniequipId import characterId_to_uniequipId

# from .cal_full_trained_character_info import calculate_fully_trained_character_data
from .cal_buff_list import get_character_skill_id

uniequip_buff_id_list = []
talent_buff_id_list = []
sub_profession_trait_buff_id_list = []
skill_buff_id_list = []
direct_addition_buff_list = ["attack_speed", "base_attack_time"]
direct_multiplication_buff_list = ["atk", "max_hp"]


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
        self.defense = character_info["base_def"]
        self.magic_resistance = character_info["base_magic_resistance"]
        self.cost = character_info["base_cost"]
        self.respawn_time = character_info["base_respawn_time"]
        self.attack_speed = character_info["base_attack_speed"]
        self.attack_time = character_info["base_attack_time"]
        self.atk_scale = 1

    def update_basic_attribute_by_direct_addition(self, key, value):
        add_atk = 0
        if key in direct_addition_buff_list:
            if key == "def":
                key = "defense"
            if key == "base_attack_time":
                key = "attack_time"
                value = value * 2
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

    def update_basic_attribute_with_skill_by_direct_addition(self, key, value):
        if key in direct_addition_buff_list:
            if key == "def":
                key = "defense"
            if key == "base_attack_time":
                key = "attack_time"
                value = value * 2
            setattr(self, key, self.__dict__[key] + value)

    def update_attribute_with_skill_by_direct_multiplication(self, key, value):
        if key in direct_multiplication_buff_list:
            setattr(self, key, self.__dict__[key] * (1 + value))

    def update_attack_scale(self, value):
        self.atk_scale *= value


class CharacterSkillInfo:
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

    character_attribute_info = {
        "max_hp": character_info["base_hp"],
        "atk": character_info["base_atk"],
        "def": character_info["base_def"],
        "magic_resistance": character_info["base_magic_resistance"],
        "cost": character_info["base_cost"],
        "respawn_time": character_info["base_respawn_time"],
        "attack_speed": character_info["base_attack_speed"],
        "attack_time": character_info["base_attack_time"],
    }

    atk_scale = 1
    skill_attack_atk_scale = 1
    sub_profession_talent_atk_scale = 1
    uniequip_atk_scale = 1
    talent_atk_scale = 1
    skill_atk_scale = 1
    damage_scale = 1

    total_duration_frame = 0

    base_atk = character_info["base_atk"]
    add_atk = 0
    combo_attack_times = 0
    total_attack_times = 1
    is_crit = False

    off_string_damage = 0
    damage = 0
    surtr_t_2_interval = 0
    # 先计算模组 buff 加成
    uniequip_buff_list = buff_list["uniequip_buff_list"]
    uniequip_test = UniequipBuff(characterId, uniequip_buff_list)
    print(dir(uniequip_test))
    for buff in uniequip_buff_list:
        if buff["key"] == "atk_scale":  # atk_scale 为攻击力倍率
            uniequip_atk_scale = atk_scale * buff["value"]
        elif buff["key"] == "damage_scale":
            damage_scale = damage_scale * (1 + buff["value"])
        elif buff["key"] == "attack_speed":
            character_attribute_info["attack_speed"] = character_attribute_info["attack_speed"] + buff["value"]

    # 再计算天赋 buff 加成
    talent_buff_list = buff_list["talent_buff_list"]
    talent_test = TalentBuff(characterId, talent_buff_list)
    print(dir(talent_test))
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
            elif buff["key"] == "surtr_t_2[withdraw].interval":  # 史尔特尔 2 天赋,锁血
                surtr_t_2_interval = buff["value"]

    # 再计算子职业特性 buff 加成
    sub_profession_trait_buff_list = buff_list["sub_profession_trait_buff_list"]
    sub_profession_trait_test = SubProfessionTraitBuff(characterId, sub_profession_trait_buff_list)
    print(dir(sub_profession_trait_test))
    for buff in sub_profession_trait_buff_list:
        if buff["key"] == "atk_scale":
            sub_profession_talent_atk_scale = atk_scale * buff["value"]

    # 计算普攻伤害
    basic_attack_damage = (
        (character_attribute_info["atk"] + add_atk)
        * atk_scale
        * talent_atk_scale
        * uniequip_atk_scale
        * damage_scale
        * sub_profession_talent_atk_scale
    )

    # 计算离弦伤害
    if characterId == "char_340_shwaz" and skill_id == "skchr_shwaz_3":  # 黑 3 技能离弦 1 枪
        is_off_string = True
        off_string_num = 1
        basic_attack_atk = character_attribute_info["atk"] + add_atk
        basic_attack_atk_scale = uniequip_atk_scale * talent_atk_scale * damage_scale
        off_string_damage = basic_attack_atk * basic_attack_atk_scale * off_string_num
        im.append(f"是否离弦 {is_off_string} \n")
        im.append(f"离弦伤害: {off_string_damage}\n")

    # 再计算技能 buff 加成
    skill_buff_list = buff_list["skill_buff_list"]
    skill_test = SkillBuff(characterId, skill_buff_list)
    print(dir(skill_test))
    for buff in skill_buff_list:
        print(buff)
        if buff["key"] == "attack@atk_scale":
            skill_attack_atk_scale = buff["value"]
        elif buff["key"] == "attack@times":  # attack@times 为攻击次数(连击)
            combo_attack_times += buff["value"]
        elif buff["key"] == "base_attack_time":  # base_attack_time 为攻击间隔
            if characterId == "char_103_angel" and skill_id == "skchr_angel_3":  # 能天使 3 技能攻击间隔双倍减少
                character_attribute_info["attack_time"] = character_attribute_info["attack_time"] + buff["value"] * 2
            else:
                character_attribute_info["attack_time"] = character_attribute_info["attack_time"] + buff["value"]
        elif buff["key"] == "atk":
            add_atk += base_atk * buff["value"]
        elif buff["key"] == "atk_scale":
            skill_atk_scale = atk_scale * buff["value"]
        elif buff["key"] == "damage_scale":
            damage_scale = damage_scale * buff["value"]
        elif buff["key"] == "max_hp":
            character_attribute_info["max_hp"] = character_attribute_info["max_hp"] + buff["value"]
        elif buff["key"] == "attack@surtr_s_2[critical].atk_scale":
            atk_scale = atk_scale * buff["value"]
        elif buff["key"] == "attack_speed":
            character_attribute_info["attack_speed"] = character_attribute_info["attack_speed"] + buff["value"]

    # 剔除暴击 buff 下的伤害倍率加成
    for buff in skill_buff_list:
        if buff["key"] == "prob" and buff["atk_scale"] in skill_buff_list:
            skill_atk_scale = skill_atk_scale / buff["atk_scale"].value

    # 计算技能概率暴击 buff
    skill_crit_buff_list = buff_list["skill_buff_list"]
    for buff in skill_crit_buff_list:
        if buff["key"] == "prob":
            prob = buff["value"]
            is_crit = True
        elif buff["key"] == "atk_scale":
            atk_scale = buff["value"]

    # 计算覆写的天赋
    for buff in skill_buff_list:
        if buff["key"] == "bgsnow_s_3[atk_up].atk_scale":
            skill_atk_scale = atk_scale * buff["value"]
        elif buff["key"] == "hit_interval":
            character_attribute_info["attack_time"] = buff["value"]

    # 特殊处理弹药技能
    if characterId in ["char_1013_chen2"]:
        talent_buff_list = buff_list["talent_buff_list"]
        for talent in talent_buff_list:
            for buff in talent:
                if buff["key"] == "spareshot_chen.prob":
                    spareshot_chen_prob = buff["value"]
                elif buff["key"] == "chen2_t_2[common].attack_speed":
                    character_attribute_info["attack_speed"] = character_attribute_info["attack_speed"] + buff["value"]

    # 特殊处理
    if characterId == "char_4055_bgsnow" and skill_id == "skchr_bgsnow_2":  # 鸿雪 2 技能造成 3 连击
        combo_attack_times += 3

    print(uniequip_buff_id_list)
    print(character.__dict__)
    # 基础属性的计算
    # 并记录原始攻击力与增加的攻击力
    base_atk_teat, add_atk_test = await update_character_attribute_info(
        character,
        uniequip_test,
        talent_test,
        sub_profession_trait_test,
        skill_test,
    )
    print(f"base_atk_teat: {base_atk_teat} add_atk: {add_atk_test}")

    print(uniequip_test.__dict__)
    print(talent_test.__dict__)
    print(sub_profession_trait_test.__dict__)
    print(skill_test.__dict__)
    print(character.__dict__)

    await update_character_atk_scale(
        character,
        uniequip_test,
        talent_test,
        sub_profession_trait_test,
        skill_test,
    )
    print(character.atk_scale)
    character_attribute_info["atk"] = add_atk + base_atk
    print(character_attribute_info)
    final_atk_scale_without_crit = (
        uniequip_atk_scale
        * talent_atk_scale
        * skill_atk_scale
        * skill_attack_atk_scale
        * sub_profession_talent_atk_scale
    )
    if is_crit:
        final_atk_scale_with_crit = final_atk_scale_without_crit * atk_scale
    else:
        final_atk_scale_with_crit = final_atk_scale_without_crit
    final_atk = character_attribute_info["atk"] * final_atk_scale_with_crit
    if skill_id == "skchr_amgoat_2":
        # 技能实际效果为先削减主攻击目标的法术抗性，再对爆炸范围内所有敌人造成½倍率的伤害(包括主攻击目标)
        # 最后对主攻击目标额外造成一次½倍率的伤害
        final_atk = final_atk * 2
        im.append(f"艾雅法拉二技能实际效果为先削减主攻击目标的法术抗性,再对爆炸范围内所有敌人造成½倍率的伤害(包括主攻击目标),最后对主攻击目标额外造成一次½倍率的伤害\n")
        im.append(f"最终攻击力 (攻击力 * 倍率) 为 ({base_atk} + {add_atk}) * {final_atk_scale_with_crit * 2} = {final_atk}\n")
        print(f"最终攻击力 (攻击力 * 倍率) 为 ({base_atk} + {add_atk}) * {final_atk_scale_with_crit * 2} = {final_atk}")
    else:
        im.append(f"最终攻击力 (攻击力 * 倍率) 为 ({base_atk} + {add_atk}) * {final_atk_scale_with_crit} = {final_atk}\n")
        print(f"最终攻击力 (攻击力 * 倍率) 为 ({base_atk} + {add_atk}) * {final_atk_scale_with_crit} = {final_atk}")
    raw_attack_time = character_attribute_info["attack_time"]
    print(f"攻击间隔为 {raw_attack_time}")
    final_attack_speed = character_attribute_info["attack_speed"]
    print(f"最终攻击速度为 {final_attack_speed}%")

    frame_rate = 30
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

    # 获取技能数据
    skill_type = await get_skill_basic_info(characterId, skill_id, "skillType")  # 技能类型
    skill_duration_type = await get_skill_basic_info(characterId, skill_id, "durationType")  # 持续类型
    sp_type = await get_skill_basic_info(characterId, skill_id, "spType")  # sp 类型
    sp_cost = await get_skill_basic_info(characterId, skill_id, "spCost")  # sp 消耗
    init_sp = await get_skill_basic_info(characterId, skill_id, "initSp")  # 初始 sp
    sp_increment = await get_skill_basic_info(characterId, skill_id, "increment")  # sp 增长
    skill_duration = await get_skill_basic_info(characterId, skill_id, "duration")  # 技能持续时间
    max_charge_time = await get_skill_basic_info(characterId, skill_id, "maxChargeTime")  # 最大蓄力次数
    print(f"技能持续时间为 {skill_duration} 秒")

    time_line = []
    if combo_attack_times == 0:
        combo_attack_times = 1

    is_special_treatment = False

    # 特殊处理弹药类技能
    if characterId in ["char_1013_chen2", "char_4039_horn"]:
        im.append("弹药类技能特殊处理\n")
        is_special_treatment = True
        str_time_line = ""
        skill_buff_list = buff_list["skill_buff_list"]
        attack_trigger_time = 0
        hand_up_time = 12  # 抬手 12 帧
        prob_add_attack_trigger_time = 0
        if skill_duration > 0:
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
                    skill_duration,
                    frame_rate,
                    frame_alignment_attack_interval,
                    final_atk_scale_with_crit,
                )
                im.append("号角默认触发血战,过载伤害分两段计算\n")
                im.append(
                    f"不触发过载时攻击力(攻击力 * 倍率)为 ({base_atk} + {add_atk}) * {final_atk_scale_with_crit} = {final_atk}\n"
                )
                im.append(f"不触发过载时持续时间为 {first_stage_duration}\n")
                im.append(f"不触发过载时攻击次数为 {first_stage_atk_times}\n")
                im.append(f"不触发过载时伤害为 {first_stage_damage}\n")
                im.append(
                    f"触发过载时攻击力(攻击力 * 倍率)为 ({base_atk} + {overload_add_atk}) * {final_atk_scale_with_crit} = {second_stage_atk}\n"
                )
                im.append(f"触发过载时持续时间为 {second_stage_duration}\n")
                im.append(f"触发过载时攻击次数为 {second_stage_atk_times}\n")
                im.append(f"触发过载时伤害为 {second_stage_damage}\n")
                # 总伤害
                damage = first_stage_damage + second_stage_damage
            else:
                total_skill_duration = skill_duration
                attack_trigger_time = skill_duration * frame_rate / float(frame_alignment_attack_interval)
                attack_time = Decimal(attack_trigger_time / 2).quantize(Decimal("0"), rounding=decimal.ROUND_CEILING)
                im.append(f"攻击次数为 {attack_time} 次\n")
                im.append(f"技能持续时间为 {total_skill_duration} 秒\n")
                damage = final_atk * int(attack_time) * damage_scale

        else:
            for buff in skill_buff_list:
                if buff["key"] == "attack@trigger_time":  # 弹药总量
                    attack_trigger_time = buff["value"]
            if characterId == "char_1013_chen2":  # 天赋多计入 4 发弹药
                prob_add_attack_trigger_time = 4
                im.append("水陈天赋多计入 4 发弹药\n")
            attack_time = (attack_trigger_time / 2 + prob_add_attack_trigger_time) * 2  # 一次消耗 2 发弹药
            attack_interval = int(frame_alignment_attack_interval)  # 帧对齐后的攻击间隔(帧)
            total_skill_duration = (attack_time * attack_interval + hand_up_time) / frame_rate  # 技能持续时间(秒)
            im.append(f"攻击次数为 {attack_time} 次\n")
            im.append(f"技能持续时间为 {total_skill_duration} 秒\n")
            damage = final_atk * int(attack_time) * damage_scale
    elif skill_duration > 0 and not is_special_treatment:
        total_duration_frame = skill_duration * frame_rate
        attack_times = (total_duration_frame - default_skill_forward) / int(frame_alignment_attack_interval)
        total_attack_times = (
            int(Decimal(attack_times).quantize(Decimal("0"), rounding=decimal.ROUND_CEILING)) * combo_attack_times
        )
        damage = final_atk * total_attack_times * damage_scale + off_string_damage
    elif skill_duration == -1 and not is_special_treatment:  # -1 表示为永续技能或者是次数技能
        default_simulation_time = 120
        default_spine_duration_frame = 48  # 默认动画持续时间(帧)
        if skill_id == "skchr_amgoat_2":
            default_spine_duration_frame = 36
        im.append(f"技能持续时间为永久, 模拟时间为 {default_simulation_time} 秒\n")
        total_duration_frame = default_simulation_time * frame_rate
        im.append(f"在模拟的情况下技能总持续帧数为 {total_duration_frame} 帧\n")
        str_time_line = ""
        str_time_line = await get_time_line(
            default_simulation_time,
            frame_alignment_attack_interval,
            sp_cost,
            sp_increment,
            sp_type,
            frame_rate,
            default_spine_duration_frame,
            max_charge_time,
        )

        # 特殊处理史尔特尔的技能
        if characterId == "char_350_surtr" and skill_id == "skchr_surtr_3":
            max_hp = character_attribute_info["max_hp"]
            (loss_time, blood_lock_time, attack_interval,) = await deal_with_surtr_third_skill(
                max_hp,
                surtr_t_2_interval,
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
    elif skill_duration == 0:  # 表示瞬发技能
        damage = final_atk

    if damage_scale != 1:
        im.append(f"damage_scale为 {damage_scale}\n")
    im.append(f"总伤害为 {damage}")
    print(f"总伤害为 {damage}")

    # 特殊处理黑键伤害计算
    if characterId == "char_4046_ebnhlz":
        single_attack_damage, mata_full_damage = await deal_with_ebnhlz_skill_damage(
            character_attribute_info,
            add_atk,
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
            f"最终攻击力 (攻击力 * 倍率) 为 ({base_atk} + {add_atk}) * 1 = {final_atk}\n"
            f"最终攻击间隔: {final_attack_time_in_frame} 帧, {final_attack_time} 秒"
            f"帧对齐后的攻击间隔: {frame_alignment_attack_interval} 帧, {frame_alignment_attack_time} 秒\n"
            f"攻击模式为攒满球再加一次普攻\n"
            f"攒满球的伤害为: {mata_full_damage}\n"
            f"时间轴为 {str_time_line}\n"
            f"满蓄力+普攻伤害 {single_attack_damage}\n"
            f"攻击次数为 {_attack_time} 次\n"
            f"总伤害为 {damage}"
        )

    return im


async def get_skill_basic_info(characterId: str, skill_id: int, params: str) -> int:
    with open(
        f"src/plugins/ark/tool/data/character_skill_info/{characterId}.json",
        encoding="utf-8",
    ) as f:
        skill_basic_info = json.load(f)
    if params == "duration":
        info = skill_basic_info[skill_id][params]
    elif params == "spType":
        info = skill_basic_info[skill_id]["spData"][params]
    elif params == "initSp":
        info = skill_basic_info[skill_id]["spData"][params]
    elif params == "spCost":
        info = skill_basic_info[skill_id]["spData"][params]
    elif params == "increment":
        info = skill_basic_info[skill_id]["spData"][params]
    elif params == "skillType":
        info = skill_basic_info[skill_id][params]
    elif params == "durationType":
        info = skill_basic_info[skill_id][params]
    elif params == "maxChargeTime":
        info = skill_basic_info[skill_id]["spData"][params]
    else:
        info = 0
    return info


async def get_time_line(
    default_simulation_time: int,
    frame_alignment_attack_interval: Decimal,
    sp_cost: int,
    sp_increment: int,
    sp_type: int,
    frame_rate: int,
    default_spine_duration_frame: int,
    max_charge_time: int,
) -> str:
    time_line = []

    # 总帧数
    total_duration_frame = default_simulation_time * frame_rate
    # 默认取攻击动画为 4 帧
    default_attack_frame = 4
    # 攻击间隔 (帧)
    attack_interval = frame_alignment_attack_interval
    # 达到技能所需 sp 的帧数
    reach_sp_frame = sp_cost / sp_increment * frame_rate
    print(f"达到技能所需 sp 的帧数为 {reach_sp_frame}")
    frame = 1
    timer = 0  # 初始化计时器
    i = 0
    while frame <= total_duration_frame:
        # 默认第一帧开技能, 放完所有蓄力的次数
        is_first_skill_spine = True if frame == 1 else False
        if is_first_skill_spine:
            frame = frame + default_spine_duration_frame
            time_line.append("+")  # "+"表示技能
        while i < max_charge_time - 1:
            frame = frame + default_spine_duration_frame
            time_line.append("+")  # "+"表示技能
            i = i + 1
            timer = 0
            print(123)
        print(frame)
        while 1:
            if frame <= total_duration_frame:
                basic_attack_number = 0  # 初始化普攻计数器
                skill_attack_number = 1  # 初始化技能计数器
                # 进行一次普攻
                # timer += attack_interval + default_attack_frame
                # frame += attack_interval + default_attack_frame
                timer += attack_interval
                frame += attack_interval
                # 普攻计数器 +1
                basic_attack_number += 1
                time_line.append("-")  # "-"表示普攻
                # 对 spType 进行判断
                if sp_type == 1:  # 1 表示为自动回复技能
                    # 判断是否达到技能所需 sp
                    if timer >= reach_sp_frame:
                        # 进行一次技能攻击
                        frame += attack_interval
                        # 技能计数器 +1
                        skill_attack_number += 1
                        time_line.append("+")  # "+"表示技能
                        # 计时器清零
                        timer = 0
                elif sp_type == 2:  # 2 表示为攻击回复技能
                    # 如果普攻计数器达到 3 次
                    if basic_attack_number == 3:
                        # 进行一次技能攻击
                        timer += attack_interval
                        # 技能计数器 +1
                        skill_attack_number += 1
                        time_line.append("+")  # "+"表示技能
                        # 普攻计数器清零
                        basic_attack_number = 0
            else:
                break
    str_time_line = "".join(time_line)
    im = str_time_line

    return im


async def deal_with_surtr_third_skill(
    max_hp: int,
    surtr_t_2_interval: int,
    frame_rate: int,
    frame_alignment_attack_interval: Decimal,
    skill_buff_list: list,
):
    hp_ratio = 0
    duration = 0
    interval = 0

    blood_lock_time = surtr_t_2_interval * frame_rate
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

    return loss_time, blood_lock_time, attack_interval


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
    character_attribute_info: dict,
    add_atk: int,
    base_atk: int,
    uniequip_id: str,
    buff_list: dict,
    total_attack_times: int,
    skill_id: str,
):
    character_attribute_info["atk"] = add_atk + base_atk
    final_atk = character_attribute_info["atk"] * 1  # 黑键攻击力倍率为 1
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
    skill_duration: int,
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
    first_stage_duration = skill_duration - horn_s_3_overload_start_damage_duration  # 第一段持续时间
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
):
    atk = character.atk
    add_atk = 0
    # 属性中的直接加算部分
    for buff_key in uniequip_buff_id_list:
        add_atk += character.update_basic_attribute_by_direct_addition(buff_key, uniequip_test.__dict__[buff_key])
    for buff_key in talent_buff_id_list:
        add_atk += character.update_basic_attribute_by_direct_addition(buff_key, talent_test.__dict__[buff_key])
    for buff_key in sub_profession_trait_buff_id_list:
        add_atk += character.update_basic_attribute_by_direct_addition(
            buff_key, sub_profession_trait_test.__dict__[buff_key]
        )
    for buff_key in skill_buff_id_list:
        character.update_basic_attribute_with_skill_by_direct_addition(buff_key, skill_test.__dict__[buff_key])

    # 属性中的直接乘算部分
    for buff_key in uniequip_buff_id_list:
        add_atk += character.update_attribute_by_direct_multiplication(buff_key, uniequip_test.__dict__[buff_key])
    for buff_key in talent_buff_id_list:
        add_atk += character.update_attribute_by_direct_multiplication(buff_key, talent_test.__dict__[buff_key])
    for buff_key in sub_profession_trait_buff_id_list:
        add_atk += character.update_attribute_by_direct_multiplication(
            buff_key, sub_profession_trait_test.__dict__[buff_key]
        )
    for buff_key in skill_buff_id_list:
        character.update_basic_attribute_with_skill_by_direct_addition(buff_key, skill_test.__dict__[buff_key])

    return atk, add_atk


async def update_character_atk_scale(
    character: CharacterBasicInfo,
    uniequip_test: UniequipBuff,
    talent_test: TalentBuff,
    sub_profession_trait_test: SubProfessionTraitBuff,
    skill_test: SkillBuff,
):
    for buff_key in uniequip_buff_id_list:
        if buff_key == "atk_scale":
            character.atk_scale = character.atk_scale * uniequip_test.__dict__[buff_key]
    for buff_key in talent_buff_id_list:
        if buff_key == "atk_scale":
            character.atk_scale = character.atk_scale * talent_test.__dict__[buff_key]
    for buff_key in sub_profession_trait_buff_id_list:
        if buff_key == "atk_scale":
            character.atk_scale = character.atk_scale * sub_profession_trait_test.__dict__[buff_key]
    for buff_key in skill_buff_id_list:
        if buff_key == "atk_scale":
            character.atk_scale = character.atk_scale * skill_test.__dict__[buff_key]
        elif buff_key == "attack@atk_scale":
            character.atk_scale = character.atk_scale * skill_test.__dict__[buff_key]
