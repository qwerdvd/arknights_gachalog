import json
from datetime import datetime
from typing import Optional
from nonebot.log import logger

from ..utils.ark_api.get_ark_data import get_recharge_record_by_token
from ..utils.download_resource.RESOURCE_PATH import PLAYER_PATH


async def save_recharge_record(uid: str, raw_data: Optional[dict] = None):
    path = PLAYER_PATH / str(uid)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    # 获取当前时间
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")

    # 初始化最后保存的数据
    result = {}

    # 充值记录json路径
    recharge_record_path = path / "recharge_record.json"

    recharge_record_history = None
    old_total_recharge_record = 0
    old_number_of_recharge_records = 0
    if recharge_record_path.exists():
        with open(recharge_record_path, "r", encoding="UTF-8") as f:
            recharge_record_history = json.load(f)
        old_total_recharge_record = recharge_record_history["total_recharge_record"]
        old_number_of_recharge_records = recharge_record_history[
            "number_of_recharge_records"
        ]
        recharge_record_history = recharge_record_history["data"]

    # 获取新抽卡记录
    if raw_data is None:
        raw_data = await get_recharge_record_by_token(uid, recharge_record_history)
        print(raw_data)
    else:
        new_data = []
        if recharge_record_history:
            for item in raw_data:
                if item not in recharge_record_history:
                    new_data.append(item)
            raw_data = new_data

    if raw_data == {}:
        return "你还没有绑定过Cookie噢~"
    if not raw_data:
        return "你还没有绑定过Cookie或者Cookie已失效~"

    result["uid"] = uid
    result["data_time"] = current_time
    result["number_of_recharge_records"] = len(raw_data)
    total_recharge_record = 0
    # 抽卡记录中的 star 为实际 star - 1
    print(raw_data)
    for i in range(len(raw_data)):
        total_recharge_record += raw_data[i]["amount"]
    result["total_recharge_record"] = total_recharge_record
    if len(raw_data[0]) > 1:
        raw_data.sort(key=lambda x: (-int(x["orderId"])))
    result["data"] = raw_data

    # 计算数据
    all_add = result["number_of_recharge_records"] - old_number_of_recharge_records
    total_recharge_record_add = (
        result["total_recharge_record"] - old_total_recharge_record
    )

    # 保存文件
    with open(recharge_record_path, "w", encoding="UTF-8") as file:
        json.dump(result, file, ensure_ascii=False)

    # 回复文字
    if all_add == 0:
        im = f"UID{uid}没有新增充值数据!"
        print(im)
    else:
        im = (
            f"UID{uid}数据更新成功！"
            f"本次更新{all_add}个充值记录!\n本次更新，你充值了{total_recharge_record_add}\n总额为{total_recharge_record}"
        )
        print(im)
    return im
