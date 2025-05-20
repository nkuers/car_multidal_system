import pyttsx3

def synthesize_speech(text):
    """将文本转换为语音"""
    engine = pyttsx3.init()
    engine.setProperty("rate", 150)  # 调整语速
    engine.setProperty("volume", 0.9)  # 调整音量
    engine.say(text)
    engine.runAndWait()