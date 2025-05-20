import json
import os

CONFIG_FILE = "user_config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        # 默认配置
        return {
            "preferred_commands": {
                "确认": ["点头", "竖起大拇指"],
                "取消": ["摇头", "摇手"],
                "暂停音乐": ["握拳"]
            },
            "voice_aliases": {
                "播放音乐": ["播放", "开始音乐"],
                "导航": ["导航到", "去往"]
            }
        }

def save_config(config):
    # 去重处理
    for key in ["preferred_commands", "voice_aliases"]:
        for action, triggers in config[key].items():
            config[key][action] = list(set(triggers))  # 去重
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)
    print("[配置管理] 用户配置已保存")