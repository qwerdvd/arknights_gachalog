import json
from pathlib import Path

from ...version import Arknights_version

mata_path = f'C:\\Users\\qwerdvd\\PycharmProjects\\pythonProject\\Arknights\\src\\plugins\\ark\\tool\\data\\map' \
            f'\\characterId_to_uniequipId_mapping_{Arknights_version}.json '

with open(mata_path, encoding='utf8') as fp:
    characterId_to_uniequipId_data = json.load(fp)


async def characterId_to_uniequipId(characterId: str, uniequip_id: int) -> str:
    """
    :说明:
      接受角色 ID 转换为角色对应模组名称
    :参数:
      * avatar_id (str): 角色ID。
    :返回:
      * name (str): 角色对应模组名称。
    """
    raw_uniequipId = characterId_to_uniequipId_data[characterId]
    uniequip_id = raw_uniequipId[uniequip_id]
    return uniequip_id
