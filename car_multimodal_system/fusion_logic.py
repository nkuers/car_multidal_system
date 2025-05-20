from config_manager import load_config
from transformers import AutoTokenizer, AutoModelForCausalLM
from knowledge_base import retrieve_knowledge  # 检索增强模块
from tts_engine import synthesize_speech  # 语音合成模块

# 初始化支持中文的小型模型 Qwen/Qwen-1.8B
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen1.5-1.8B-Chat", trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen1.5-1.8B-Chat", trust_remote_code=True)

def fuse(voice_result, gesture_result, vision_result, user_role="passenger"):
    config = load_config()
    permissions = config["permissions"]

    print("\n[融合模块] 开始判断：")
    print(f"语音：{voice_result}, 手势：{gesture_result}, 视觉：{vision_result}, 用户角色：{user_role}")

    # 构建多模态输入
    multimodal_input = (
        f"语音输入: {voice_result if voice_result else '无'}\n"
        f"手势输入: {gesture_result if gesture_result else '无'}\n"
        f"视觉输入: {vision_result if vision_result else '无'}\n"
        f"用户角色: {user_role if user_role else '未知'}\n"
    )
    # 检索增强：从知识库中获取相关信息
    knowledge = retrieve_knowledge(voice_result, gesture_result, vision_result)
    if knowledge:
        multimodal_input += f"相关知识: {knowledge}\n"
    multimodal_input += "请用一句话描述用户当前最可能的意图："

    print(f"[调试] 最终多模态输入：\n{multimodal_input}")

    # 使用大模型推理用户意图
    try:
        inputs = tokenizer(
            multimodal_input,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512  # 设置最大长度为 512
        )
        outputs = model.generate(**inputs, max_length=100, num_return_sequences=1)
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"[调试] 大模型推理结果：{response}")
    except Exception as e:
        print(f"[错误] 大模型推理失败：{e}")
        response = "推理失败"

    # 验证推理结果
    if not response or response.strip() == "":
        response = "无效操作"
        print("[调试] 推理结果为空，返回默认值：无效操作")
    
     # 提取核心内容（只保留意图描述部分）
    if "请用一句话描述用户当前最可能的意图：" in response:
        core_response = response.split("请用一句话描述用户当前最可能的意图：")[-1].strip()
    else:
        core_response = response  # 如果格式不匹配，保留原始响应

    # 检查权限
    action = check_permission(core_response, user_role, permissions)

    # 语音合成反馈
    synthesize_speech(core_response)

    return action

def check_permission(action, user_role, permissions):
    """检查操作权限"""
    if not action or action.strip() == "":
        print(f"[权限管理] 无效的操作：{action}")
        return "无效操作"

    if action in permissions["driver_only"] and user_role != "driver":
        print(f"[权限管理] 操作被拒绝：{action} 仅限驾驶员执行")
        return "操作被拒绝"

    print(f"[权限管理] 操作允许：{action}")
    return action