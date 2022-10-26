import json
from datetime import datetime
from typing import Optional

from ..utils.ark_api.get_ark_data import get_gacha_log_by_token
from ..utils.download_resource.RESOURCE_PATH import PLAYER_PATH


async def calculate_gacha_num(star, gacha_data: Optional[dict] = None) -> int:
    gacha_num = 0
    for i in range(len(gacha_data['List'])):
        for j in range(len(gacha_data['List'][i]['chars'])):
            if gacha_data['List'][i]['chars'][j]['rarity'] == star:
                gacha_num += 1
                j += 1
        i += 1
    return gacha_num


async def save_gachalogs(uid: str, raw_data: Optional[dict] = None):
    path = PLAYER_PATH / str(uid)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    # 获取当前时间
    now = datetime.now()
    current_time = now.strftime('%Y-%m-%d %H-%M-%S')

    # 初始化最后保存的数据
    result = {}

    # 抽卡记录json路径
    gachalogs_path = path / 'gacha_logs.json'

    gachalogs_history = None
    old_six_star_gacha_num = 0
    old_five_star_gacha_num = 0
    old_four_star_gacha_num = 0
    old_three_star_gacha_num = 0
    old_all_gacha_num = 0
    if gachalogs_path.exists():
        with open(gachalogs_path, "r", encoding='UTF-8') as f:
            gachalogs_history = json.load(f)
        gachalogs_history = gachalogs_history['data']
        old_six_star_gacha_num = gachalogs_history['six_star_gacha_num']
        old_five_star_gacha_num = gachalogs_history['five_star_gacha_num']
        old_four_star_gacha_num = gachalogs_history['four_star_gacha_num']
        old_three_star_gacha_num = gachalogs_history['three_star_gacha_num']
        old_all_gacha_num = gachalogs_history['all_gacha_num']

    # 获取新抽卡记录
    if raw_data is None:
        raw_data = await get_gacha_log_by_token(uid, gachalogs_history)
    else:
        new_data = {}
        if gachalogs_history:
            for i in ['List']:
                for item in raw_data[i]:
                    if item not in gachalogs_history[i]:
                        new_data[i].append(item)
            raw_data = new_data
            for i in ['List']:
                raw_data[i].extend(gachalogs_history[i])

    if raw_data == {}:
        return '你还没有绑定过Cookie噢~'
    if not raw_data:
        return '你还没有绑定过Cookie或者Cookie已失效~'

    # 校验值
    temp_data = {'List': []}
    for i in ['List']:
        for item in raw_data[i]:
            if 'ts' in item:
                temp_data[i].append(item)
    raw_data = temp_data

    result['uid'] = uid
    result['data_time'] = current_time
    star = 6
    six_star_gacha_num = await calculate_gacha_num(star, raw_data)
    result['six_star_gacha_num'] = six_star_gacha_num
    star = 5
    five_star_gacha_num = await calculate_gacha_num(star, raw_data)
    result['five_star_gacha_num'] = five_star_gacha_num
    star = 4
    four_star_gacha_num = await calculate_gacha_num(star, raw_data)
    result['four_star_gacha_num'] = four_star_gacha_num
    star = 3
    three_star_gacha_num = await calculate_gacha_num(star, raw_data)
    result['three_star_gacha_num'] = three_star_gacha_num
    result['all_gacha_num'] = six_star_gacha_num + five_star_gacha_num + four_star_gacha_num + three_star_gacha_num
    for i in ['List']:
        if len(raw_data[i]) > 1:
            raw_data[i].sort(key=lambda x: (-int(x['ts'])))
    result['data'] = raw_data

    # 计算数据
    six_star_add = result['six_star_gacha_num'] - old_six_star_gacha_num
    five_star_add = result['five_star_gacha_num'] - old_five_star_gacha_num
    four_star_add = result['four_star_gacha_num'] - old_four_star_gacha_num
    three_star_add = result['three_star_gacha_num'] - old_three_star_gacha_num
    all_add = result['all_gacha_num'] - old_all_gacha_num

    # 保存文件
    with open(gachalogs_path, 'w', encoding='UTF-8') as file:
        json.dump(result, file, ensure_ascii=False)

    # 回复文字
    if all_add == 0:
        im = f'UID{uid}没有新增抽卡数据!'
        print(im)
    else:
        im = (
            f'UID{uid}数据更新成功！'
            f'本次更新{all_add}个数据!\n{six_star_add}个6星，{five_star_add}个5星\n{four_star_add}个4星，{three_star_add}个3星'
        )
        print(im)
    return im
