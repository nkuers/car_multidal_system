import cv2
import mediapipe as mp
import math
from collections import deque
import threading
from PIL import Image, ImageDraw, ImageFont
import numpy as np

class GestureController:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=1,
                                         min_detection_confidence=0.85,
                                         min_tracking_confidence=0.85)
        self.mp_draw = mp.solutions.drawing_utils
        self.running = True

        self.hand_x_history = deque(maxlen=10)
        self.recent_gestures = deque(maxlen=5)

    def put_chinese_text(self, img, text, pos, font_path="simsun.ttc", font_size=30, color=(0, 255, 0)):
        img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil)
        font = ImageFont.truetype(font_path, font_size, encoding="utf-8")
        draw.text(pos, text, font=font, fill=color[::-1])
        img = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
        return img

    def detect_gesture(self, handLms, img_shape):
        h, w, _ = img_shape
        landmarks = [(int(lm.x * w), int(lm.y * h)) for lm in handLms.landmark]

        palm_x = landmarks[0][0]
        self.hand_x_history.append(palm_x)

        fingers = []
        fingers.append(int(landmarks[4][0] > landmarks[3][0]))
        tips = [8, 12, 16, 20]
        joints = [6, 10, 14, 18]
        for tip, joint in zip(tips, joints):
            fingers.append(int(landmarks[tip][1] < landmarks[joint][1]))

        if sum(fingers) == 0:
            return "握拳 (暂停音乐)"
        if fingers[0] == 1 and sum(fingers[1:]) == 0:
            return "竖起大拇指 (确认)"
        if self.is_shaking():
            return "摇手 (拒绝)"
        return "未知手势"

    def is_shaking(self):
        if len(self.hand_x_history) < 10:
            return False
        x_vals = list(self.hand_x_history)
        return max(x_vals) - min(x_vals) > 40

    def run(self):
        cap = cv2.VideoCapture(0)
        print("[手势] 开始检测，输入 'q' 或按 ESC 或点击窗口 × 退出")

        def input_listener():
            while True:
                user_input = input()
                if user_input.strip().lower() == 'q':
                    self.running = False
                    break

        threading.Thread(target=input_listener, daemon=True).start()

        gesture = "无手势"
        window_name = "手势检测"
        cv2.namedWindow(window_name)

        while self.running:
            success, img = cap.read()
            if not success:
                print("[手势] 无法读取摄像头")
                break

            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = self.hands.process(img_rgb)

            if results.multi_hand_landmarks:
                handLms = results.multi_hand_landmarks[0]
                self.mp_draw.draw_landmarks(img, handLms, self.mp_hands.HAND_CONNECTIONS)
                gesture_now = self.detect_gesture(handLms, img.shape)
                self.recent_gestures.append(gesture_now)
                gesture = max(set(self.recent_gestures), key=self.recent_gestures.count)

            img = self.put_chinese_text(img, f"手势: {gesture}", (10, 30), font_size=30, color=(0, 255, 0))
            cv2.imshow(window_name, img)

            key = cv2.waitKey(30) & 0xFF
            if key == 27:
                self.running = False
                break

            try:
                if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                    print("[手势] 窗口关闭检测到")
                    self.running = False
                    break
            except cv2.error:
                print("[手势] 窗口被销毁")
                self.running = False
                break

        cap.release()
        cv2.destroyAllWindows()
        return gesture


if __name__ == "__main__":
    gesture_module = GestureController()
    gesture_module.run()
