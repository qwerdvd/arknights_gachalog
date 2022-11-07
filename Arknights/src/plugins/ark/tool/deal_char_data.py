import json
import asyncio
from pathlib import Path

print(Path.cwd())

# 角色信息文件地址
mata_path = 'C:\\Users\\qwerdvd\\PycharmProjects\\pythonProject\\Arknights\\data\\gamedata'
char_path = mata_path + '\\excel\\character_table.json'
data_version_path = mata_path + '\\excel\\data_version.txt'
skill_path = mata_path + '\\excel\\skill_table.json'

# 读取角色信息文件
with open(char_path, 'r', encoding='utf-8') as f:
    char_path = json.load(f)

# 读取数据版本文件
with open(data_version_path, 'r', encoding='utf-8') as f:
    raw_data_version = f.read().splitlines()

# 读取技能信息文件
with open(skill_path, 'r', encoding='utf-8') as f:
    raw_skill_data = json.load(f)


# 从数据版本文件中提取版本号
data_version = raw_data_version[2].split(':')[1]

CharacterId_to_chName_mapping = {}
chName_to_enName_mapping = {}


# 角色 id 英文名到中文名的映射
# "char_002_amiya": "阿米娅"
async def get_CharacterId_to_chName_mapping():
    for char in char_path.items():
        CharacterId_to_chName_mapping[char[0]] = char[1]['name']
    # 保存角色 id 英文名到中文名的映射
    with open(f'C:\\Users\\qwerdvd\\PycharmProjects\\pythonProject\\Arknights\\src\\plugins\\ark\\tool\\data\\map'
              f'\\CharacterId_to_chName_mapping_{data_version}.json', 'w', encoding='utf8') as f2:
        json.dump(CharacterId_to_chName_mapping, f2, ensure_ascii=False, indent=2)


# 角色 id 中文名到英文名的映射
# "阿米娅": "amiya"
async def get_chName_to_enName_mapping():
    for char in char_path.items():
        chName_to_enName_mapping[char[1]['name']] = char[0].split('_')[2]
    # 保存角色 id 中文名到英文名的映射
    with open(f'C:\\Users\\qwerdvd\\PycharmProjects\\pythonProject\\Arknights\\src\\plugins\\ark\\tool\\data\\map'
              f'\\chName_to_enName_mapping_{data_version}.json', 'w', encoding='utf8') as f2:
        json.dump(chName_to_enName_mapping, f2, ensure_ascii=False, indent=2)


# 储存满级干员数据
# 潜能数据另外列表储存
async def get_char_data():
    for char in char_path.items():
        max_level_character_info = {}
        character_name = char[0]
        name = char[1]['name']  # 角色名
        profession = char[1]['profession']  # 干员职业
        subProfessionId = char[1]['subProfessionId']  # 干员子职业
        star = char[1]['rarity'] + 1  # 星级
        raw_skills = char[1]['skills']  # 技能
        skills = []
        for skill in raw_skills:
            mata_skill = {'overridePrefabKey': skill['overridePrefabKey'],
                          'overrideTokenKey': skill['overrideTokenKey'], 'skillId': skill['skillId']}
            skills.append(mata_skill)
        raw_phases = char[1]['phases'][-1]['attributesKeyFrames'][-1]
        elite = len(char[1]['phases']) - 1  # 精英化等级
        max_level = raw_phases['level']  # 最大等级
        phases = raw_phases['data']  # 满级干员数据
        teamId = char[1]['teamId']  # 干员所属阵营
        tokenKey = char[1]['tokenKey']  # 召唤物id
        trait = char[1]['trait']  # 干员特性
        max_level_character_info['name'] = name
        max_level_character_info['profession'] = profession
        max_level_character_info['subProfessionId'] = subProfessionId
        max_level_character_info['star'] = star
        max_level_character_info['skills'] = skills
        max_level_character_info['elite'] = elite
        max_level_character_info['max_level'] = max_level
        max_level_character_info['data'] = phases
        max_level_character_info['teamId'] = teamId
        max_level_character_info['tokenKey'] = tokenKey
        max_level_character_info['trait'] = trait
        with open(f'C:\\Users\\qwerdvd\\PycharmProjects\\pythonProject\\Arknights\\src\\plugins\\ark\\tool\\data'
                  f'\\basic_character_info\\{character_name}.json', 'w', encoding='utf8') as f2:
            json.dump(max_level_character_info, f2, ensure_ascii=False, indent=2)


# 储存干员潜能数据
async def get_char_potential_data():
    for char in char_path.items():
        character_name = char[0]
        raw_potential = char[1]['potentialRanks']
        potential = {}
        for i in range(len(raw_potential)):
            potential[i + 2] = raw_potential[i]  # 从 2 潜开始
        with open(f'C:\\Users\\qwerdvd\\PycharmProjects\\pythonProject\\Arknights\\src\\plugins\\ark\\tool\\data'
                  f'\\character_potential_info\\{character_name}.json', 'w', encoding='utf8') as f2:
            json.dump(potential, f2, ensure_ascii=False, indent=2)


# 储存干员天赋数据
async def get_char_talents_data():
    for char in char_path.items():
        character_name = char[0]
        raw_talents = char[1]['talents']
        talents = {}
        if raw_talents is not None:
            for i in range(len(raw_talents)):
                talents[i + 1] = raw_talents[i]  # 从 1 天赋开始
            with open(f'C:\\Users\\qwerdvd\\PycharmProjects\\pythonProject\\Arknights\\src\\plugins\\ark\\tool\\data'
                      f'\\character_talent_info\\{character_name}.json', 'w', encoding='utf8') as f2:
                json.dump(talents, f2, ensure_ascii=False, indent=2)


async def ger_char_skill_data():
    for char in char_path.items():
        skill_info = {}
        character_name = char[0]
        for i in range(len(char[1]['skills'])):
            skill_id = char[1]['skills'][i]['skillId']
            for skill in raw_skill_data.items():
                if skill[0] == skill_id:
                    mata_skill_data = skill[1]['levels'][-1]
                    skill_info[skill_id] = mata_skill_data
        with open(f'C:\\Users\\qwerdvd\\PycharmProjects\\pythonProject\\Arknights\\src\\plugins\\ark'
                  f'\\tool\\data'
                  f'\\character_skill_info\\{character_name}.json', 'w', encoding='utf8') as f2:
            json.dump(skill_info, f2, ensure_ascii=False, indent=2)


async def main():
    # await get_CharacterId_to_chName_mapping()  # 角色 id 英文名到中文名的映射
    # await get_chName_to_enName_mapping()  # 角色 id 中文名到英文名的映射
    # await get_char_data()  # 满级干员基础数据
    # await get_char_potential_data()  # 干员潜能数据
    # await get_char_talents_data()  # 干员天赋数据
    await ger_char_skill_data()  # 干员技能数据


if __name__ == "__main__":
    asyncio.run(main())
