import threading
from voice_control import recognize_voice
from fusion_logic import fuse
from combined_interaction import CombinedInteraction
from config_manager import load_config
from log_manager import save_interaction_log, clean_logs  # 导入日志管理模块
from transformers import pipeline

voice_result = None
interaction_result = None

def run_voice():
    global voice_result
    print("[语音] 正在聆听...")
    voice_result = recognize_voice()
    print(f"[语音] 识别结果：{voice_result}")

def run_interaction():
    global interaction_result
    print("[交互] 开始检测头部和手势")
    interaction_module = CombinedInteraction()
    interaction_result = interaction_module.run()

if __name__ == "__main__":
    # 在程序启动时清理日志文件
    clean_logs()


    config = load_config()
    print(f"加载用户配置：{config}")

    user_role = "driver"  # 示例：可以通过传感器或登录系统动态获取

    threads = [
        threading.Thread(target=run_voice),
        threading.Thread(target=run_interaction),
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    gesture_result, vision_result = interaction_result
    result = fuse(voice_result, gesture_result, vision_result,user_role)
    print(f"\n🧠 系统响应：{result}")

    # 保存交互记录到日志
    save_interaction_log(voice_result, gesture_result, vision_result, result)
    # 初始化大模型推理引擎
    # qa_pipeline = pipeline("text2text-generation", model="google/flan-t5-base")

    # prompt = "用户说：播放音乐，视觉检测为点头。请判断他的意图是什么？"
    # response = qa_pipeline(prompt, max_length=100, num_return_sequences=1)[0]["generated_text"]
    # print(f"[调试] 大模型推理结果：{response}")

    # from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

    # try:
    #     tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
    #     model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base")
    #     print("[测试] 模型和分词器加载成功")
    # except Exception as e:
    #     print(f"[错误] 模型加载失败：{e}")

