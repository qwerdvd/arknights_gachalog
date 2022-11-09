import json
from typing import Optional
from ..utils.alias.characterId_to_uniequipId import characterId_to_uniequipId


async def get_data_version() -> str:
    mata_path = 'C:\\Users\\qwerdvd\\PycharmProjects\\pythonProject\\Arknights\\data\\gamedata'
    data_version_path = mata_path + '\\excel\\data_version.txt'
    with open(data_version_path, 'r', encoding='utf-8') as f:
        raw_data_version = f.read().splitlines()
    data_version = raw_data_version[2].split(':')[1]
    return data_version


# Calculate the data of fully trained operators
async def calculate_fully_trained_character_data(characterId: str, is_equip: bool, uniequip_id: str):
    with open(f'src/plugins/ark/tool/data/basic_character_info/{characterId}.json', encoding='UTF-8') as f:
        basic_character_info = json.load(f)

    character_info = {
        'basic_hp': basic_character_info['data']['maxHp'],
        'basic_atk': basic_character_info['data']['atk'],
        'basic_def': basic_character_info['data']['def'],
        'basic_magic_resistance': basic_character_info['data']['magicResistance'],
        'basic_cost': basic_character_info['data']['cost'],
        'basic_respawn_time': basic_character_info['data']['respawnTime'],
        'basic_attack_speed': basic_character_info['data']['attackSpeed'],
        'basic_attack_time': basic_character_info['data']['baseAttackTime']
    }

    # 获取干员模组加成数据
    if is_equip:
        if uniequip_id == '一模':
            uniequip_id = 1
        elif uniequip_id == '二模':
            uniequip_id = 2
        # 模组属性加成数据
        uniequip_attribute_data = await get_equip_attribute_data(characterId, uniequip_id)
        # 天赋覆写数据
        uniequip_talent_override = await get_equip_talent_adjustment(characterId, uniequip_id, target="TALENT")
        # 特性覆写数据
        uniequip_trait_override = await get_equip_trait_adjustment(characterId, uniequip_id, target="TRAIT")

    # TODO: 模组加成优先于潜能加成
    # 获取干员潜能信息数据
    potential_data = await get_potential_data(characterId)

    # 获取干员满信赖加成数据
    favor_data = await get_favor_data(characterId)

    # 计算干员基础数据
    add_hp = potential_data['potential_hp'] + favor_data['favor_hp'] + uniequip_attribute_data['uniequip_hp']
    add_atk = potential_data['potential_atk'] + favor_data['favor_atk'] + uniequip_attribute_data['uniequip_atk']
    add_def = potential_data['potential_def'] + favor_data['favor_def'] + uniequip_attribute_data['uniequip_def']
    add_magic_resistance = potential_data['potential_magic_resistance'] + uniequip_attribute_data[
        'uniequip_magic_resistance']
    add_cost = potential_data['potential_cost'] + uniequip_attribute_data['uniequip_cost']
    add_attack_speed = potential_data['potential_attack_speed'] + uniequip_attribute_data['uniequip_attack_speed']
    add_respawn_time = potential_data['potential_respawn_time'] + uniequip_attribute_data['uniequip_respawn_time']

    # 计算干员满练数据
    character_info['basic_hp'] = character_info['basic_hp'] + add_hp
    character_info['basic_atk'] = character_info['basic_atk'] + add_atk
    character_info['basic_def'] = character_info['basic_def'] + add_def
    character_info['basic_magic_resistance'] = character_info['basic_magic_resistance'] + add_magic_resistance
    character_info['basic_cost'] = character_info['basic_cost'] + add_cost
    character_info['basic_attack_speed'] = character_info['basic_attack_speed'] + add_attack_speed
    character_info['basic_respawn_time'] = character_info['basic_respawn_time'] + add_respawn_time

    return character_info


async def get_potential_data(characterId: str) -> Optional[dict]:
    with open(f'src/plugins/ark/tool/data/character_potential_info/{characterId}.json', encoding='UTF-8') as f:
        character_potential_info = json.load(f)
    potential_data = {}
    potential_hp, potential_atk, potential_def, potential_magic_resistance, potential_cost = 0, 0, 0, 0, 0
    potential_cost, potential_attack_speed, potential_respawn_time = 0, 0, 0
    for potential in character_potential_info.items():
        if potential[1]['type'] == 0:
            attributeModifiers = potential[1]['buff']['attributes']['attributeModifiers']
            for attributeModifier in attributeModifiers:
                if attributeModifier['attributeType'] == 0:
                    potential_hp += attributeModifier['value']
                elif attributeModifier['attributeType'] == 1:
                    potential_atk += attributeModifier['value']
                elif attributeModifier['attributeType'] == 2:
                    potential_def += attributeModifier['value']
                elif attributeModifier['attributeType'] == 3:
                    potential_magic_resistance += attributeModifier['value']
                elif attributeModifier['attributeType'] == 4:
                    potential_cost += attributeModifier['value']
                elif attributeModifier['attributeType'] == 7:
                    potential_attack_speed += attributeModifier['value']
                elif attributeModifier['attributeType'] == 21:
                    potential_respawn_time += attributeModifier['value']
    potential_data['potential_hp'] = potential_hp
    potential_data['potential_atk'] = potential_atk
    potential_data['potential_def'] = potential_def
    potential_data['potential_magic_resistance'] = potential_magic_resistance
    potential_data['potential_cost'] = potential_cost
    potential_data['potential_attack_speed'] = potential_attack_speed
    potential_data['potential_respawn_time'] = potential_respawn_time
    return potential_data


async def get_favor_data(characterId: str) -> Optional[dict]:
    with open(f'src/plugins/ark/tool/data/character_favor_info/{characterId}.json', encoding='UTF-8') as f:
        character_favor_info = json.load(f)
    favor_data = {}
    favor_hp, favor_atk, favor_def = 0, 0, 0
    for favor in character_favor_info['data'].items():
        if favor[0] == 'atk':
            favor_atk += favor[1]
        elif favor[0] == 'def':
            favor_def += favor[1]
        elif favor[0] == 'hp':
            favor_hp += favor[1]
    favor_data['favor_hp'] = favor_hp
    favor_data['favor_atk'] = favor_atk
    favor_data['favor_def'] = favor_def
    return favor_data


# 获取干员模组基础属性数据
async def get_equip_attribute_data(characterId: str, uniequip_id: int) -> Optional[dict]:
    equip_id = await characterId_to_uniequipId(characterId, uniequip_id)
    with open(f'src/plugins/ark/tool/data/uniequip_info/{equip_id}.json', encoding='UTF-8') as f:
        character_uniequip_info = json.load(f)
    uniequip_attribute_data = {}
    uniequip_base_attribute = character_uniequip_info['attributeBlackboard']
    uniequip_hp, uniequip_atk, uniequip_def, uniequip_magic_resistance = 0, 0, 0, 0
    uniequip_cost, uniequip_attack_speed, uniequip_respawn_time = 0, 0, 0
    for i in range(len(uniequip_base_attribute)):
        if uniequip_base_attribute[i]['key'] == 'atk':
            uniequip_atk = uniequip_base_attribute[i]['value']
        elif uniequip_base_attribute[i]['key'] == 'def':
            uniequip_def = uniequip_base_attribute[i]['value']
        elif uniequip_base_attribute[i]['key'] == 'magicResistance':
            uniequip_magic_resistance = uniequip_base_attribute[i]['value']
        elif uniequip_base_attribute[i]['key'] == 'max_hp':
            uniequip_hp = uniequip_base_attribute[i]['value']
        elif uniequip_base_attribute[i]['key'] == 'cost':
            uniequip_cost = uniequip_base_attribute[i]['value']
        elif uniequip_base_attribute[i]['key'] == 'attack_speed':
            uniequip_attack_speed = uniequip_base_attribute[i]['value']
        elif uniequip_base_attribute[i]['key'] == 'respawn_time':
            uniequip_respawn_time = uniequip_base_attribute[i]['value']
    uniequip_attribute_data['uniequip_hp'] = uniequip_hp
    uniequip_attribute_data['uniequip_atk'] = uniequip_atk
    uniequip_attribute_data['uniequip_def'] = uniequip_def
    uniequip_attribute_data['uniequip_magic_resistance'] = uniequip_magic_resistance
    uniequip_attribute_data['uniequip_cost'] = uniequip_cost
    uniequip_attribute_data['uniequip_attack_speed'] = uniequip_attack_speed
    uniequip_attribute_data['uniequip_respawn_time'] = uniequip_respawn_time

    return uniequip_attribute_data


# 获取干员模组特性调整数据
async def get_equip_trait_adjustment(characterId: str, uniequip_id: int, target: str) -> Optional[dict]:
    equip_id = await characterId_to_uniequipId(characterId, uniequip_id)
    override_trait_data = {}
    with open(f'src/plugins/ark/tool/data/uniequip_info/{equip_id}.json', encoding='UTF-8') as f:
        character_uniequip_info = json.load(f)
    uniequip_parts_info = character_uniequip_info['parts']
    for i in range(len(uniequip_parts_info)):
        if uniequip_parts_info[i]["target"] == target:
            raw_override_trait_data = uniequip_parts_info[i]['overrideTraitDataBundle']['candidates'][-1]
            override_trait_data = raw_override_trait_data['blackboard']

    return override_trait_data


# 获取干员模组天赋调整数据
async def get_equip_talent_adjustment(characterId: str, uniequip_id: int, target: str) -> Optional[dict]:
    equip_id = await characterId_to_uniequipId(characterId, uniequip_id)
    override_talent_data = {}
    with open(f'src/plugins/ark/tool/data/uniequip_info/{equip_id}.json', encoding='UTF-8') as f:
        character_uniequip_info = json.load(f)
    uniequip_parts_info = character_uniequip_info['parts']
    for i in range(len(uniequip_parts_info)):
        print(uniequip_parts_info[i])
        if uniequip_parts_info[i]["target"] == target:
            raw_override_talent_data = uniequip_parts_info[i]['addOrOverrideTalentDataBundle']['candidates'][-1]
            override_talent_data['talent_index'] = raw_override_talent_data['talentIndex']
            override_talent_data['blackboard'] = raw_override_talent_data['blackboard']

    return override_talent_data
