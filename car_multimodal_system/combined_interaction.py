import cv2
from gesture_controller import GestureController
from vision_control import VisualInteraction
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import time

def put_chinese_text(img, text, pos, font_path="simsun.ttc", font_size=24, color=(0, 255, 0)):
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    try:
        font = ImageFont.truetype(font_path, font_size, encoding="utf-8")
    except:
        font = ImageFont.load_default()
    color_rgb = (color[2], color[1], color[0])
    draw.text(pos, text, font=font, fill=color_rgb)
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

class CombinedInteraction:
    def __init__(self):
        self.gesture_controller = GestureController()
        self.visual_interaction = VisualInteraction()
        self.running = True
        self.last_vision_result_time = 0
        self.vision_result_cooldown = 1.5  # 秒

    def run(self):
        cap = cv2.VideoCapture(0)
        print("[交互] 开始检测头部和手势，按 ESC 或点击窗口 × 退出")

        gesture_result = "无手势"
        vision_result = "无动作"
        gaze_direction = "未知"

        while self.running:
            ret, frame = cap.read()
            if not ret:
                print("[交互] 无法读取摄像头")
                break

            h, w = frame.shape[:2]
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # 手势检测
            hand_results = self.gesture_controller.hands.process(rgb_frame)
            if hand_results.multi_hand_landmarks:
                handLms = hand_results.multi_hand_landmarks[0]
                self.gesture_controller.mp_draw.draw_landmarks(frame, handLms, self.gesture_controller.mp_hands.HAND_CONNECTIONS)
                gesture_result = self.gesture_controller.detect_gesture(handLms, frame.shape)

            # 面部检测
            face_results = self.visual_interaction.face_mesh.process(rgb_frame)
            if face_results.multi_face_landmarks:
                face_landmarks = face_results.multi_face_landmarks[0]
                self.visual_interaction.mp_draw.draw_landmarks(
                    frame,
                    face_landmarks,
                    self.visual_interaction.mp.face_mesh.FACEMESH_CONTOURS
                )

                # 节流逻辑，避免频繁更新
                now = time.time()
                if now - self.last_vision_result_time > self.vision_result_cooldown:
                    vision_result = self.visual_interaction.get_current_gesture()
                    self.last_vision_result_time = now

                gaze_direction = "注视中央"  # 可根据眼动后期替换为动态方向

            # 在一个窗口显示所有信息
            frame = put_chinese_text(frame, f"头部动作: {vision_result}", (10, 30), font_size=30, color=(0, 255, 0))
            frame = put_chinese_text(frame, f"目光方向: {gaze_direction}", (10, 70), font_size=30, color=(0, 128, 255))
            frame = put_chinese_text(frame, f"手势: {gesture_result}", (10, 110), font_size=30, color=(255, 0, 0))
            cv2.imshow("交互演示", frame)

            # 检测退出条件
            key = cv2.waitKey(1)
            if key == 27 or cv2.getWindowProperty("交互演示", cv2.WND_PROP_VISIBLE) < 1:
                self.running = False
                break

        cap.release()
        cv2.destroyAllWindows()
        return {"gesture": gesture_result, "vision": vision_result}

if __name__ == "__main__":
    interaction = CombinedInteraction()
    interaction.run()
