from decimal import Decimal


async def simulation_time_line(
    character,
    skill,
    frame_alignment_attack_time: Decimal,
    default_spine_duration_frame: int,
) -> str:
    time_line = []
    default_simulation_time = 120  # 默认模拟时间
    frame_rate = 30  # 帧率

    # 总帧数
    total_duration_frame = default_simulation_time * frame_rate
    # 攻击间隔 (帧)
    attack_interval = frame_alignment_attack_time
    # 达到技能所需技力的帧数
    reach_sp_frame = skill.spCost / skill.increment * frame_rate

    # 初始化总计时器
    total_timer = 1
    # 默认第一帧开技能,所以要先加上技能动画帧数
    total_timer += default_spine_duration_frame
    while total_timer < total_duration_frame:
        # 初始化技能间隔计时器
        skill_interval_timer = 0
        # 初始化普攻计数器
        normal_attack_count = 0

        # 进行一次普攻
        total_timer += attack_interval  # 总计时器加上普攻间隔
        skill_interval_timer += attack_interval  # 技能间隔计时器加上普攻间隔
        time_line.append("A")  # 记录普攻
        normal_attack_count += 1  # 普攻计数器加一

        # 对 spType 进行判断
        if skill.spType == 1:  # 1 表示为自动回复技能
            # 判断是否达到技能所需 sp , 达到就进行一次技能释放
            if skill_interval_timer > reach_sp_frame:
                total_timer += default_spine_duration_frame  # 总计时器加上技能动画帧数
                skill_interval_timer = 0  # 技能间隔计时器清零
                time_line.append("S")  # 记录技能释放
        elif skill.spType == 2:  # 2 表示为攻击回复技能
            if normal_attack_count < skill.spCost - skill.initSp:  # 判断是否达到攻击次数
                if skill.duration == -1:  # 判断是否为永续技能
                    total_timer += default_spine_duration_frame  # 总计时器加上技能动画帧数
                    skill_interval_timer = skill.spCost  # 此时可认为一直是满技力
                    time_line.append("S")  # 记录技能释放
                else:
                    # 如果满足条件,则进行一次技能释放
                    total_timer += default_spine_duration_frame  # 总计时器加上技能动画帧数
                    skill_interval_timer = 0  # 技能间隔计时器清零
                    time_line.append("S")  # 记录技能释放
            else:
                # 如果不满足条件,则进行一次普攻
                total_timer += attack_interval
                skill_interval_timer += attack_interval
                time_line.append("A")
                normal_attack_count += 1

    str_time_line = "".join(time_line)
    im = str_time_line

    return im
