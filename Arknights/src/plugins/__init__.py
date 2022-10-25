from nonebot import load_plugins
from pathlib import Path

dir_ = Path(__file__).parent
load_plugins(str(dir_ / "ark"))
