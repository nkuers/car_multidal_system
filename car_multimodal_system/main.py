import threading
from voice_control import recognize_voice
from fusion_logic import fuse
from combined_interaction import CombinedInteraction  # 使用整合后的交互模块

voice_result = ""
interaction_result = ""

def run_voice():
    global voice_result
    print("[语音] 正在聆听...")
    voice_result = recognize_voice()

def run_interaction():
    global interaction_result
    print("[交互] 开始检测头部和手势")
    interaction_module = CombinedInteraction()
    interaction_result = interaction_module.run()

if __name__ == "__main__":
    print("🚗 启动车载多模态交互系统")

    # ✅ 并行启动语音和整合交互模块
    threads = [
        threading.Thread(target=run_voice),
        threading.Thread(target=run_interaction),
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # ✅ 模态融合并输出结果
    result = fuse(voice_result, interaction_result, interaction_result)  # 交互结果包含手势和视觉
    print(f"\n🧠 系统响应：{result}")