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
# from ..utils.download_resource.RESOURCE_PATH import (
#     CHAR_STAND_PATH as STAND_PATH,
# )
from ..utils.download_resource.RESOURCE_PATH import (
    AVATAR_PATH,
    PLAYER_PATH,
    #     WEAPON_PATH,
)

TEXT_PATH = Path(__file__).parent / 'texture2d'

title_mask = Image.open(TEXT_PATH / 'title_mask.png')
up_tag = Image.open(TEXT_PATH / 'up.png')

gs_font_110 = ys_font_origin(110)
gs_font_23 = font_origin(23)
gs_font_26 = font_origin(26)
gs_font_28 = font_origin(28)
gs_font_40 = font_origin(40)

first_color = (29, 29, 29)
brown_color = (41, 25, 0)
red_color = (255, 66, 66)
green_color = (74, 189, 119)

NOT_USED_POOL_MAP = {'常驻标准寻访'}


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
    card_img = Image.open(TEXT_PATH / 'item_bg.png')
    card_img_draw = ImageDraw.Draw(card_img)
    point = (1, 0)
    text_point = (55, 124)
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
    item_pic = (
        Image.open(AVATAR_PATH / f'char_{_id}_{name}.jpg')
        .convert('RGBA')
        .resize((300, 312))
    )
    card_img.paste(item_pic, point)
    # card_img.paste(item_pic, point, item_pic)
    if gacha_num >= 81:
        text_color = red_color
    elif gacha_num <= 55:
        text_color = green_color
    else:
        text_color = brown_color
    card_img_draw.text(
        text_point, f'{gacha_num}抽', text_color, gs_font_23, 'mm'
    )
    # if is_up:
    #     card_img.paste(up_tag, (47, -2), up_tag)
    img.paste(card_img, xy_point, card_img)


async def draw_gachalogs_img(uid: str) -> Union[bytes, str]:
    path = PLAYER_PATH / str(uid) / 'gacha_logs.json'
    if not path.exists():
        return '你还没有抽卡数据噢~\n请添加cookie后使用命令`刷新抽卡记录`更新抽卡数据~'
    with open(path, 'r', encoding='UTF-8') as f:
        gacha_data = json.load(f)

    # 数据初始化
    total_data = {}
    for i in ['单up池', '专属推荐干员寻访', '联合寻访', '常驻标准寻访']:
        total_data[i] = {
            'total': 0,
            'avg': 0,
            'remain': 0,
            'item': '',
            'list': [],
        }
        data_list = gacha_data['data'][i]
        # logger.info(data_list)
        is_not_first = False
        num_temp = []
        num = 1
        for data in data_list[::-1]:
            for j in range(len(data['chars'])):
                if data['chars'][j]['rarity'] == 5:
                    data['gacha_num'] = num
                    # logger.info(data['gacha_num'])
                    # 排除第一个
                    if is_not_first:
                        logger.info(num)
                        num_temp.append(num)
                    if not num_temp:
                        is_not_first = True
                    total_data[i]['list'].append(data)
                    num = 1
                    total_data[i]['total'] += 1
                else:
                    num += 1
        # total_data['List']['item'] = await name_to_avatar_id(total_data['List']['item'])
        total_data[i]['remain'] = num - 1
        if len(num_temp) == 0:
            total_data[i]['avg'] = 0
        else:
            total_data[i]['avg'] = round(sum(num_temp) / len(num_temp), 2)  # type: ignore
        logger.info(total_data)

    # 常量偏移数据
    single_y = 1000
    title_y = 2000

    # 计算图片尺寸
    normal_y = (
                       1 + ((total_data['单up池']['total'] - 1) // 6)
               ) * single_y + title_y
    # char_y = (
    #     1 + ((total_data['角色祈愿']['total'] - 1) // 6)
    # ) * single_y + title_y
    # weapon_y = (
    #     1 + ((total_data['武器祈愿']['total'] - 1) // 6)
    # ) * single_y + title_y

    # 获取背景图片各项参数
    based_w = 2300
    based_h = normal_y + 200
    # based_h = normal_y + char_y + weapon_y + 200
    white_overlay = Image.new('RGBA', (based_w, based_h), (255, 255, 255, 220))
    bg_img = await get_simple_bg(based_w, based_h)
    bg_img.paste(white_overlay, (0, 0), white_overlay)

    # 总标题
    all_title = Image.open(TEXT_PATH / 'all_title.png')
    all_title_draw = ImageDraw.Draw(all_title)
    print(all_title_draw)
    # 写UID
    all_title_draw.text((1450, 692), f'{uid}', first_color, gs_font_110, 'lm')
    bg_img.paste(all_title, (0, 0), all_title)
    # 画饼图
    Num = gacha_data['all_gacha_num']
    six_star_num = gacha_data['six_star_gacha_num']
    five_star_num = gacha_data['five_star_gacha_num']
    four_star_num = gacha_data['four_star_gacha_num']
    three_star_num = gacha_data['three_star_gacha_num']
    data = [six_star_num, five_star_num, four_star_num, three_star_num]
    explode = (0.1, 0.05, 0.025, 0)
    labels = ['six_star', 'five_star', 'four_star', 'three_star']
    # colors = ['red', 'orange', 'yellow', 'green']
    sizes = [data[0] / Num * 100, data[1] / Num * 100, data[2] / Num * 100, data[3] / Num * 100]
    # ax = plt.subplots(figsize=(4, 4), facecolor='#cc00ff')
    colors = cm.bone(numpy.arange(len(sizes)) / len(sizes))
    plt.pie(sizes,
            shadow=False,
            colors=colors,
            explode=explode,
            # labels=labels,
            autopct='%1.1f%%',
            pctdistance=0.8,
            # textprops={'fontsize': 15, 'color': '#8B1A1A'},
            )
    # plt.legend(loc='upper right', fontsize=10, bbox_to_anchor=(1, 1), borderaxespad=0.4)
    plt.axis('square')
    plt.savefig('pie.png',
                format='png',
                bbox_inches='tight',
                transparent=True,
                dpi=600,
                facecolor='none'
                )
    pie = Image.open('./pie.png').resize((850, 850))
    bg_img.paste(pie, (100, 875), pie)

    # 处理title
    # {'total': 0, 'avg': 0, 'remain': 0, 'list': []}
    type_list = ['单up池', '专属推荐干员寻访', '联合寻访', '常驻标准寻访']
    y_extend = 0
    for index, i in enumerate(type_list):
        # if total_data[i]['avg'] == 0:
        #     level = 3
        # else:
        #     # 非酋 <= 90
        #     # 小非 <= 80
        #     # 稳定 <= 72
        #     # 小欧 <= 60
        #     # 欧皇 <= 43
        #     # 武器统一减10
        #     for num_index, num in enumerate([42, 58, 68, 75, 90]):
        #         if i == '武器祈愿':
        #             num -= 10
        #         if total_data[i]['avg'] <= num:
        #             level = 5 - num_index
        #             break
        #     else:
        #         level = 3

        # tag_pic = await _get_tag(level)
        # tag_pic = tag_pic.resize((208, 88))
        # # title.paste(tag_pic, (35, 54), tag_pic)
        # title_draw = ImageDraw.Draw(title)
        # # 卡池
        # title_draw.text((245, 86), i, first_color, gs_font_40, 'lm')
        # 抽卡时间
        # if gacha_data['data'][i]:
        #     ts = gacha_data['data'][i][0]['ts']
        #     # first_time = datetime.datetime.strptime(first_timestamp, '%Y-%m-%d')
        #     local_gacha_time = time.localtime(ts)
        #     first_time = time.strftime('%Y-%m-%d %H:%M:%S', local_gacha_time)
        # else:
        #     first_time = '暂未抽过卡!'
        # title_draw.text((245, 123), first_time, first_color, gs_font_28, 'lm')
        # 平均抽卡数量
        # title_draw.text(
        #     (108, 209),
        #     str(total_data[i]['avg']),
        #     first_color,
        #     gs_font_40,
        #     'mm',
        # )
        # title_draw.text(
        #     (261, 209),
        #     str(gacha_data[f'{CHANGE_MAP[i]}_gacha_num']),
        #     first_color,
        #     gs_font_40,
        #     'mm',
        # )
        # title_draw.text(
        #     (104, 160),
        #     str(total_data[i]['remain']),
        #     red_color,
        #     gs_font_28,
        #     'mm',
        # )
        y_extend += (
            (1 + ((total_data[type_list[index - 1]]['total'] - 1) // 6)) * 50
            if index != 0
            else 0
        )
        y = y_extend + 10
        # y = index * title_y + y_extend + 500
        # bg_img.paste(title, (0, y), title)
        # bg_img.paste(title, (0, y), title)
        tasks = []
        for item_index, item in enumerate(total_data[i]['list']):
            item_x = (item_index % 6) * 350 + 100
            item_y = (item_index // 6) * 419 + y + title_y
            xy_point = (item_x, item_y)
            tasks.append(
                _draw_card(
                    bg_img,
                    xy_point,
                    # item['item_type'],
                    # item['name'],
                    item['gacha_num'],
                )
            )
        await asyncio.gather(*tasks)
        tasks.clear()

    # 发送图片
    res = await convert_img(bg_img)
    logger.info('[查询抽卡]绘图已完成,等待发送!')
    return res
