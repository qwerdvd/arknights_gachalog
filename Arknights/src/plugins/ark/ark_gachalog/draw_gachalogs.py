import json
import asyncio
import time
from io import BytesIO
from pathlib import Path
from typing import Tuple, Union

import matplotlib
from nonebot.log import logger
from PIL import Image, ImageDraw
import numpy
from matplotlib import pyplot as plt, font_manager, cm

from ..utils.draw_image_tools.send_image_tool import convert_img
from ..utils.draw_image_tools.draw_image_tool import get_simple_bg
from ..utils.fonts.fonts import font_origin, ys_font_origin
from ..utils.alias.avatarId_and_name_covert import name_to_avatar_id
from ..utils.alias.chName_to_enName import chName_to_enName

# from ..utils.download_resource.RESOURCE_PATH import (
#     CHAR_STAND_PATH as STAND_PATH,
# )
from ..utils.download_resource.RESOURCE_PATH import (
    AVATAR_PATH,
    PLAYER_PATH,
    #     WEAPON_PATH,
)

TEXT_PATH = Path(__file__).parent / "texture2d"

title_mask = Image.open(TEXT_PATH / "title_mask.png")
up_tag = Image.open(TEXT_PATH / "up.png")

gs_font_110 = ys_font_origin(110)
gs_font_45 = ys_font_origin(45)
gs_font_23 = font_origin(23)
gs_font_26 = font_origin(26)
gs_font_28 = font_origin(28)
gs_font_40 = font_origin(40)

first_color = (29, 29, 29)
brown_color = (41, 25, 0)
red_color = (255, 66, 66)
green_color = (74, 189, 119)

NOT_USED_POOL_MAP = {"常驻标准寻访"}


# async def _get_tag(level: int) -> Image.Image:
#     """
#     :获取标签
#     tag 1: 非酋
#     tag 2: 小非
#     tag 3: 稳定
#     tag 4: 小欧
#     tag 5: 欧皇
#     """
#     return Image.open(TEXT_PATH / f'tag_{level}.png')


async def _draw_card(
    img: Image.Image,
    xy_point: Tuple[int, int],
    # type: str,
    name: str,
    gacha_num: int,
):
    card_img = Image.open(TEXT_PATH / "item_bg.png")
    card_img_draw = ImageDraw.Draw(card_img)
    point = (0, 1)
    text_point = (150, 370)
    # is_up = False
    # if type == '角色':
    #     if name not in ['莫娜', '迪卢克', '七七', '刻晴', '琴']:
    #         is_up = True
    #     # _id = await name_to_avatar_id(name)
    #     _id = 1
    #     item_pic = (
    #         Image.open(AVATAR_PATH / f'{_id}.png')
    #         .convert('RGBA')
    #         .resize((108, 108))
    #     )
    # else:
    #     id = 1
    # item_pic = (
    #     Image.open(WEAPON_PATH / f'{name}.png')
    #     .convert('RGBA')
    #     .resize((108, 108))
    # )
    _id = await name_to_avatar_id(name)
    _name = await chName_to_enName(name)
    item_pic = (
        Image.open(AVATAR_PATH / f"char_{_id}_{_name}.png")
        .convert("RGBA")
        .resize((300, 312))
    )
    card_img.paste(item_pic, point, item_pic)
    # card_img.paste(item_pic, point, item_pic)
    if gacha_num >= 55:
        text_color = red_color
    elif gacha_num <= 30:
        text_color = green_color
    else:
        text_color = brown_color
    card_img_draw.text(
        text_point,
        f"{name}\n{gacha_num}抽",
        text_color,
        gs_font_45,
        "mm",
        align="center",
    )
    # if is_up:
    #     card_img.paste(up_tag, (47, -2), up_tag)
    img.paste(card_img, xy_point, card_img)


async def draw_gachalogs_img(uid: str) -> Union[bytes, str]:
    path = PLAYER_PATH / str(uid) / "gacha_logs.json"
    if not path.exists():
        return "你还没有抽卡数据噢~\n请添加cookie后使用命令`刷新抽卡记录`更新抽卡数据~"
    with open(path, "r", encoding="UTF-8") as f:
        gacha_data = json.load(f)

    # 数据初始化
    total_data = {}
    for i in ["单up池", "专属推荐干员寻访", "联合寻访", "常驻标准寻访"]:
        total_data[i] = {
            "total": 0,
            "avg": 0,
            "remain": 0,
            "item": "",
            "list": [],
        }
        data_list = gacha_data["data"][i]
        # logger.info(data_list)
        is_not_first = False
        num_temp = []
        num = 1
        for data in data_list[::-1]:
            for j in range(len(data["chars"])):
                if data["chars"][j]["rarity"] == 5:
                    data["gacha_num"] = num
                    # logger.info(data['gacha_num'])
                    # 排除第一个
                    if is_not_first:
                        logger.info(num)
                        num_temp.append(num)
                    if not num_temp:
                        is_not_first = True
                    total_data[i]["list"].append(data)
                    num = 1
                    total_data[i]["total"] += 1
                else:
                    num += 1
        # 倒序循环删除十连中不为六星的数据
        for j in range(len(total_data[i]["list"])):
            for k in range(len(total_data[i]["list"][j]["chars"]) - 1, -1, -1):
                if total_data[i]["list"][j]["chars"][k]["rarity"] != 5:
                    total_data[i]["list"][j]["chars"].pop(k)

        total_data[i]["item"] = await name_to_avatar_id(total_data[i]["item"])
        total_data[i]["remain"] = num - 1
        if len(num_temp) == 0:
            total_data[i]["avg"] = 0
        else:
            total_data[i]["avg"] = round(sum(num_temp) / len(num_temp), 2)  # type: ignore
        logger.info(total_data)

    # 常量偏移数据
    single_y = 1000
    main_title_y = 2000
    title_y = 190

    # 计算图片尺寸
    normal_y = (1 + ((total_data["单up池"]["total"] - 1) // 6)) * single_y + main_title_y
    # ['专属推荐干员寻访', '联合寻访', '常驻标准寻访']
    list_1 = ["专属推荐干员寻访", "联合寻访", "常驻标准寻访"]
    changzhu_y = (1 + ((total_data["常驻标准寻访"]["total"] - 1) // 6)) * single_y + title_y
    zhuanshu_y = (1 + ((total_data["专属推荐干员寻访"]["total"] - 1) // 6)) * single_y + title_y
    lianhe_y = (1 + ((total_data["联合寻访"]["total"] - 1) // 6)) * single_y + title_y

    # 获取背景图片各项参数
    based_w = 2300
    # based_h = normal_y + 200
    based_h = normal_y + changzhu_y + zhuanshu_y + lianhe_y + 200
    white_overlay = Image.new("RGBA", (based_w, based_h), (255, 255, 255, 220))
    bg_img = await get_simple_bg(based_w, based_h)
    bg_img.paste(white_overlay, (0, 0), white_overlay)

    # 总标题
    all_title = Image.open(TEXT_PATH / "all_title.png")
    all_title_draw = ImageDraw.Draw(all_title)
    print(all_title_draw)
    # 写UID
    all_title_draw.text((1450, 692), f"{uid}", first_color, gs_font_110, "lm")
    bg_img.paste(all_title, (0, 0), all_title)
    # 画饼图
    Num = gacha_data["all_gacha_num"]
    six_star_num = gacha_data["six_star_gacha_num"]
    five_star_num = gacha_data["five_star_gacha_num"]
    four_star_num = gacha_data["four_star_gacha_num"]
    three_star_num = gacha_data["three_star_gacha_num"]
    data = [six_star_num, five_star_num, four_star_num, three_star_num]
    explode = (0.1, 0.05, 0.025, 0)
    labels = ["six_star", "five_star", "four_star", "three_star"]
    # colors = ['red', 'orange', 'yellow', 'green']
    sizes = [
        data[0] / Num * 100,
        data[1] / Num * 100,
        data[2] / Num * 100,
        data[3] / Num * 100,
    ]
    # ax = plt.subplots(figsize=(4, 4), facecolor='#cc00ff')
    colors = cm.bone(numpy.arange(len(sizes)) / len(sizes))
    plt.pie(
        sizes,
        shadow=False,
        colors=colors,
        explode=explode,
        # labels=labels,
        autopct="%1.1f%%",
        pctdistance=0.8,
        # textprops={'fontsize': 15, 'color': '#8B1A1A'},
    )
    # plt.legend(loc='upper right', fontsize=10, bbox_to_anchor=(1, 1), borderaxespad=0.4)
    plt.axis("square")
    plt.savefig(
        "pie.png",
        format="png",
        bbox_inches="tight",
        transparent=True,
        dpi=600,
        facecolor="none",
    )
    pie = Image.open("./pie.png").resize((850, 850))
    bg_img.paste(pie, (100, 875), pie)

    # 处理title
    # {'total': 0, 'avg': 0, 'remain': 0, 'list': []}
    # 专属寻访先不计算
    type_list = ["单up池", "常驻标准寻访", "联合寻访"]
    y_extend = 0
    for index, i in enumerate(type_list):
        if index != 0:
            title = Image.open(TEXT_PATH / f"pool_title_{index}.png")
        y_extend += (
            (1 + ((total_data[type_list[index - 1]]["total"] - 1) // 6)) * 419
            if index != 0
            else 0
        )
        y_1 = y_extend + 10
        y = index * title_y + y_extend + 2000
        # bg_img.paste(title, (0, y), title)
        if index != 0:
            bg_img.paste(title, (52, y), title)
        tasks = []
        for item_index, item in enumerate(total_data[i]["list"]):
            item_x = (item_index % 6) * 350 + 100
            item_y = (item_index // 6) * 419 + y_1 + main_title_y
            xy_point = (item_x, item_y)
            print(item)
            # if item['name'] == '单up池':
            for j in range(len(item["chars"])):
                tasks.append(
                    _draw_card(
                        bg_img,
                        xy_point,
                        # item['item_type'],
                        item["chars"][j]["name"],
                        item["gacha_num"],
                    )
                )
        await asyncio.gather(*tasks)
        tasks.clear()

    # 发送图片
    res = await convert_img(bg_img)
    logger.info("[查询抽卡]绘图已完成,等待发送!")
    return res
