import math

def get_finger_states(landmarks):
    """
    返回5个布尔值表示每个手指是否伸出。
    0: 大拇指, 1-4: 食指-小拇指
    """
    fingers = []
    # 大拇指：横向判断
    fingers.append(landmarks[4].x < landmarks[3].x)

    # 其余手指：纵向判断
    for tip_id in [8, 12, 16, 20]:
        fingers.append(landmarks[tip_id].y < landmarks[tip_id - 2].y)
    return fingers

def detect_hand_gesture(landmarks):
    """
    基于关键点判断是否为：握拳 / 大拇指 / 摇手。
    """
    fingers = get_finger_states(landmarks.landmark)

    # 握拳：所有手指都收起
    if fingers == [False, False, False, False, False]:
        return "暂停音乐（握拳）"

    # 大拇指：只有大拇指伸出
    if fingers == [True, False, False, False, False]:
        return "确认（竖起大拇指）"

    # 摇手检测：只作为演示，暂时用“所有手指伸出”代替
    if fingers == [True, True, True, True, True]:
        return "拒绝（摇手）"

    return None
