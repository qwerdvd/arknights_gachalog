from pathlib import Path

GAMEDATA_PATH = Path() / 'data/gamedata'  # 主目录
EXCEL_PATH = GAMEDATA_PATH / 'excel'  # 资源目录
CHARACTER_TABLE_PATH = EXCEL_PATH / 'character_table.json'  # 干员数据
DATA_VERSION_PATH = EXCEL_PATH / 'data_version.txt'  # 数据版本
