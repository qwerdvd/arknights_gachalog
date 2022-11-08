import json
from typing import Optional


# Calculate the data of fully trained operators
async def calculate_fully_trained_character_data(characterId: str):
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

    # 获取干员潜能信息数据
    potential_data = await get_potential_data(characterId)

    # 获取干员满信赖加成数据
    favor_data = await get_favor_data(characterId)

    # 计算干员基础数据
    add_hp = potential_data['potential_hp'] + favor_data['favor_hp']
    add_atk = potential_data['potential_atk'] + favor_data['favor_atk']
    add_def = potential_data['potential_def'] + favor_data['favor_def']
    add_magic_resistance = potential_data['potential_magic_resistance']
    add_cost = potential_data['potential_cost']
    add_attack_speed = potential_data['potential_attack_speed']
    add_respawn_time = potential_data['potential_respawn_time']

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
