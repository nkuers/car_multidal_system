import speech_recognition as sr

def recognize_voice():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("[语音] 正在聆听...")
        audio = r.listen(source, timeout=10, phrase_time_limit=10)
    try:
        command = r.recognize_google(audio, language="zh-CN")
        print(f"[语音] 识别结果：{command}")
        return command
    except:
        print("[语音] 识别失败")
        return ""
