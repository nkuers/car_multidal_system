def fuse(voice_result, gesture_result, vision_result):
    print("\n[融合模块] 开始判断：")
    print(f"语音：{voice_result}, 手势：{gesture_result}, 视觉：{vision_result}")
    if vision_result == "点头" or gesture_result == "大拇指":
        return "确认操作"
    if gesture_result == "摇手" or vision_result == "摇头":
        return "取消操作"
    if voice_result:
        return f"语音指令：“{voice_result}”"
    return "无操作"