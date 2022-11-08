import json

from .cal_full_trained_character_info import calculate_fully_trained_character_data


async def calculate_physical_character_damage(characterId: str):
    character_info = await calculate_fully_trained_character_data(characterId)
    print(character_info)

    return 0


async def calculate_magical_character_damage(characterId: str):
    character_info = await calculate_fully_trained_character_data(characterId)
    print(character_info)

    return 0
