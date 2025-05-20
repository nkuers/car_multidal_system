import json

KNOWLEDGE_BASE_FILE = "knowledge_base.json"

def retrieve_knowledge(voice_result, gesture_result, vision_result):
    """从知识库中检索相关信息"""
    try:
        with open(KNOWLEDGE_BASE_FILE, "r", encoding="utf-8") as f:
            knowledge_base = json.load(f)
    except FileNotFoundError:
        print("[知识库] 知识库文件不存在")
        return None

    # 简单匹配逻辑
    for entry in knowledge_base:
        if voice_result in entry["keywords"] or gesture_result in entry["keywords"] or vision_result in entry["keywords"]:
            print(f"[知识库] 匹配到相关知识：{entry['response']}")
            return entry["response"]

    print("[知识库] 未匹配到相关知识")
    return None