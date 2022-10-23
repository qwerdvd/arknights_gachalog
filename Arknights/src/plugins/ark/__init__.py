from nonebot.log import logger
from nonebot import load_all_plugins, get_plugin_by_module_name

if get_plugin_by_module_name("ark"):
    logger.info("推荐直接加载 ark 仓库文件夹")
    load_all_plugins(
        [
            'ark.ark_gachalog',
            'ark.ark_user_bind',
        ],
        [],
    )