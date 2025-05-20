import json
from datetime import datetime
import os

LOG_FILE = "interaction_log.json"
MAX_LOG_SIZE = 1024 * 1024  # 最大日志文件大小（1MB）
MAX_LOG_ENTRIES = 100  # 最大日志条目数量

def save_interaction_log(voice_result, gesture_result, vision_result, response):
    if not response or response.strip() == "":
        response = "无效操作"

    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "voice_result": voice_result,
        "gesture_result": gesture_result,
        "vision_result": vision_result,
        "response": response
    }

    # 读取现有日志
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
    except FileNotFoundError:
        logs = []

    # 添加新日志条目
    logs.append(log_entry)

    # 保存日志
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=4)

    print(f"[日志] 已保存交互记录：{log_entry}")

def clean_logs():
    """清理日志文件（按大小限制）"""
    if not os.path.exists(LOG_FILE):
        print("[日志清理] 日志文件不存在，无需清理")
        return

    # 检查文件大小
    file_size = os.path.getsize(LOG_FILE)
    if file_size > MAX_LOG_SIZE:
        print(f"[日志清理] 日志文件大小超过限制（{file_size} 字节），开始清理")
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []

        # 保留最近的 MAX_LOG_ENTRIES 条记录
        logs = logs[-MAX_LOG_ENTRIES:]
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=4)

        print(f"[日志清理] 日志已清理，保留最近 {len(logs)} 条记录")