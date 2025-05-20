import json
from collections import Counter
from config_manager import load_config, save_config

LOG_FILE = "interaction_log.json"

def load_logs():
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("[日志分析] 日志文件不存在")
        return []

def analyze_logs():
    logs = load_logs()
    if not logs:
        print("[日志分析] 无日志记录可供分析")
        return

    # 统计语音、手势和视觉结果的频率
    voice_counter = Counter(log["voice_result"] for log in logs if log["voice_result"])
    gesture_counter = Counter(log["gesture_result"] for log in logs if log["gesture_result"])
    vision_counter = Counter(log["vision_result"] for log in logs if log["vision_result"])

    print("\n[日志分析] 用户交互统计：")
    print(f"最常用语音指令：{voice_counter.most_common(3)}")
    print(f"最常用手势：{gesture_counter.most_common(3)}")
    print(f"最常用视觉动作：{vision_counter.most_common(3)}")

    # 更新用户配置
    update_user_config(gesture_counter, vision_counter)

def update_user_config(gesture_counter, vision_counter):
    config = load_config()

    # 更新 preferred_commands
    for action, triggers in config["preferred_commands"].items():
        for trigger in triggers:
            if trigger in gesture_counter or trigger in vision_counter:
                print(f"[日志分析] 优化指令：{action} -> {trigger}")

    # 保存更新后的配置
    save_config(config)
    print("[日志分析] 用户配置已更新")

if __name__ == "__main__":
    analyze_logs()