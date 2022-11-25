uniequip_buff_id_list = []
talent_buff_id_list = []
sub_profession_trait_buff_id_list = []
skill_buff_id_list = []
direct_addition_buff_list = ["attack_speed", "base_attack_time"]
direct_multiplication_buff_list = ["atk", "max_hp"]


def clear_buff_list():
    uniequip_buff_id_list.clear()
    talent_buff_id_list.clear()
    sub_profession_trait_buff_id_list.clear()
    skill_buff_id_list.clear()


class Char:
    """
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

    class SkillInfo:
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

    class Buff:
        """
        UniequipBuff: 模组Buff
        TalentBuff: 天赋Buff
        SubProfessionTraitBuff: 子职业特性Buff
        SkillBuff: 技能Buff
        """

        class UniequipBuff:
            def __init__(self, buff_list):
                uniequip_buff_list = buff_list["uniequip_buff_list"]
                for uniequip_buff in uniequip_buff_list:
                    setattr(self, uniequip_buff["key"], uniequip_buff["value"])
                    save_buff_key(uniequip_buff["key"], buff_id=1)

        class TalentBuff:
            def __init__(self, buff_list):
                talent_buff_list = buff_list["talent_buff_list"]
                for talent_buff in talent_buff_list:
                    for buff in talent_buff:
                        setattr(self, buff["key"], buff["value"])
                        save_buff_key(buff["key"], buff_id=2)

        class SubProfessionTraitBuff:
            def __init__(self, buff_list):
                sub_profession_trait_buff_list = buff_list["sub_profession_trait_buff_list"]
                for sub_profession_trait_buff in sub_profession_trait_buff_list:
                    setattr(self, sub_profession_trait_buff["key"], sub_profession_trait_buff["value"])
                    save_buff_key(sub_profession_trait_buff["key"], buff_id=3)

        class SkillBuff:
            def __init__(self, buff_list):
                skill_buff_list = buff_list["skill_buff_list"]
                for skill_buff in skill_buff_list:
                    setattr(self, skill_buff["key"], skill_buff["value"])
                    save_buff_key(skill_buff["key"], buff_id=4)

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
