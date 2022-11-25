async def get_data_version() -> str:
    mata_path = "C:\\Users\\qwerdvd\\PycharmProjects\\pythonProject\\Arknights\\data\\gamedata"
    data_version_path = mata_path + "\\excel\\data_version.txt"
    with open(data_version_path, "r", encoding="utf-8") as f:
        raw_data_version = f.read().splitlines()
    data_version = raw_data_version[2].split(":")[1]
    return data_version
