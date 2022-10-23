from pathlib import Path

MAIN_PATH = Path() / 'data'  # 主目录
RESOURCE_PATH = MAIN_PATH / 'resource'  # 资源目录
AVATAR_PATH = RESOURCE_PATH / 'avatar'  # 干员头像
BUILDING_SKILL_PATH = RESOURCE_PATH / 'building_skill'  # 基建技能图标
ENEMY_PATH = RESOURCE_PATH / 'enemy'  # 敌人图标
ITEM_PATH = RESOURCE_PATH / 'item'  # 游戏物品图标
ITEM_RARITY_IMG_PATH = RESOURCE_PATH / 'item_rarity_img'  # 物品稀有度图标
PORTRAIT_PATH = RESOURCE_PATH / 'portrait'  # 干员半身像
PROFESSION_PATH = RESOURCE_PATH / 'profession'  # 干员职业图标
# MAP_PATH = RESOURCE_PATH / 'map'
SKIN_PATH = RESOURCE_PATH / 'skin'  # 干员皮肤
TEMP_PATH = RESOURCE_PATH / 'temp'

PLAYER_PATH = MAIN_PATH / 'players'


def init_dir():
    for i in [
        MAIN_PATH,
        RESOURCE_PATH,
        AVATAR_PATH,
        ITEM_PATH,
        PORTRAIT_PATH,
        PROFESSION_PATH,
        BUILDING_SKILL_PATH,
        ENEMY_PATH,
        ITEM_RARITY_IMG_PATH,
        # MAP_PATH,
        SKIN_PATH,
        TEMP_PATH,
        PLAYER_PATH,
    ]:
        i.mkdir(parents=True, exist_ok=True)


init_dir()
