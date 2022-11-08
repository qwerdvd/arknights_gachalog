import json
from pathlib import Path

from ...version import Arknights_version

with open(
    Path(__file__).parents[1]
    / 'map'
    / f'CharacterId_to_chName_mapping_{Arknights_version}.json',
    'r',
    encoding='utf8',
) as fp:
    CharacterId_and_chName_data = json.load(fp)

async def chName_to_CharacterId(name: str) -> str:
    """
    :说明:
      接受角色名称转换为角色ID
    :参数:
      * name (str): 角色名称。
    :返回:
        * avatar_id (str): 角色ID。
        """
    CharacterId = ''
    for i in CharacterId_and_chName_data:
        if CharacterId_and_chName_data[i] == name:
            CharacterId = i
            break
    return CharacterId
