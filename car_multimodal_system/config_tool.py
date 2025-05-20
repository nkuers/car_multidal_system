from config_manager import load_config, save_config

def add_preferred_command(action, trigger):
    config = load_config()
    if action not in config["preferred_commands"]:
        config["preferred_commands"][action] = []
    config["preferred_commands"][action].append(trigger)
    save_config(config)
    print(f"已添加偏好指令：{action} -> {trigger}")

def add_voice_alias(action, alias):
    config = load_config()
    if action not in config["voice_aliases"]:
        config["voice_aliases"][action] = []
    config["voice_aliases"][action].append(alias)
    save_config(config)
    print(f"已添加语音别名：{action} -> {alias}")

if __name__ == "__main__":
    print("用户配置工具")
    print("1. 添加偏好指令")
    print("2. 添加语音别名")
    choice = input("请选择操作：")
    if choice == "1":
        action = input("请输入操作名称（如 确认）：")
        trigger = input("请输入触发条件（如 点头）：")
        add_preferred_command(action, trigger)
    elif choice == "2":
        action = input("请输入操作名称（如 播放音乐）：")
        alias = input("请输入语音别名（如 开始音乐）：")
        add_voice_alias(action, alias)
    else:
        print("无效选择")