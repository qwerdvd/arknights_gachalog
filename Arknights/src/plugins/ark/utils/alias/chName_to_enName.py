import json
from pathlib import Path

from ...version import Arknights_version

with open(
    Path(__file__).parents[1] / "map" / f"chName_to_enName_mapping_{Arknights_version}.json",
    "r",
    encoding="utf8",
) as fp:
    chName_to_enName_data = json.load(fp)


async def chName_to_enName(ch_name: str) -> str:
    en_name = chName_to_enName_data[ch_name]
    return en_name
