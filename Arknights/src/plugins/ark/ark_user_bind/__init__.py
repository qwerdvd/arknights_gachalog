from typing import Any, List, Tuple

from nonebot import on_command, on_regex
from nonebot.adapters.onebot.v11 import (
    PRIVATE_FRIEND,
    Message,
    MessageEvent,
    MessageSegment,
)
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, RegexGroup

# from .draw_user_card import get_user_card
from ..config import priority
from ..utils.db_operation.db_operation import (
    bind_db,
    delete_db,
    get_user_bind_data,
    select_db,
)
from ..utils.exception.handle_exception import handle_exception

# from .draw_user_card import get_user_card
from ..utils.nonebot2.rule import FullCommand
from .add_ck import deal_ck

add_cookie = on_command("添加", permission=PRIVATE_FRIEND)
# bind_info = on_command(
#     '绑定信息', priority=priority, block=True, rule=FullCommand()
# )
bind = on_regex(r"^(绑定|切换|解绑|删除)(uid|UID)([0-9]+)?$", priority=priority)


# @bind_info.handle()
# async def send_bind_card(
#         event: MessageEvent,
#         matcher: Matcher,
# ):
#     logger.info('开始执行[查询用户绑定状态]')
#     qid = event.user_id
#     # im = await get_user_card(qid)
#     uid = await select_db(qid, 'uid')
#     im = f'QID为{QID},UID为{UID}'
#     logger.info('[查询用户绑定状态]完成!等待图片发送中...')
#     # await matcher.finish(MessageSegment.image(im))
#     await matcher.finish(im)


@add_cookie.handle()
@handle_exception("Cookie", "校验失败！请输入正确的Cookies！")
async def send_add_ck_msg(event: MessageEvent, matcher: Matcher, args: Message = CommandArg()):
    logger.info("开始执行[添加Cookie]")
    mes = args.extract_plain_text().strip().replace(" ", "")
    qid = event.user_id
    im = await deal_ck(mes, qid)
    if isinstance(im, str):
        await matcher.finish(im)
    await matcher.finish(MessageSegment.image(im))


# 群聊内 绑定uid的命令，会绑定至当前qq号上
@bind.handle()
@handle_exception("绑定ID", "绑定ID异常")
async def send_link_uid_msg(event: MessageEvent, matcher: Matcher, args: Tuple[Any, ...] = RegexGroup()):
    im = []
    logger.info("开始执行[绑定/解绑用户信息]")
    logger.info("[绑定/解绑]参数: {}".format(args))
    qid = event.user_id
    logger.info("[绑定/解绑]UserID: {}".format(qid))

    if args[0] in ("绑定"):
        logger.info("[绑定]开始执行")
        if args[2] is None:
            await matcher.finish("请输入正确的uid！")
        if args[1] in ("uid", "UID"):
            logger.info("[绑定]开始执行[绑定uid]")
            im = await bind_db(qid, args[2])
        else:
            im = await bind_db(qid, None, args[2])
    else:
        if args[1] in ("uid", "UID"):
            im = await delete_db(qid, {"UID": args[2]})
    await matcher.finish(im, at_sender=True)
