import threading
import cv2
import mediapipe as mp
import numpy as np
from collections import deque
from PIL import ImageFont, ImageDraw, Image

def put_chinese_text(img, text, pos, font_path="simsun.ttc", font_size=24, color=(0, 255, 0)):
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    font = ImageFont.truetype(font_path, font_size, encoding="utf-8")
    color_rgb = (color[2], color[1], color[0])
    draw.text(pos, text, font=font, fill=color_rgb)
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

class VisualInteraction(threading.Thread):
    def __init__(self):
        super().__init__()
        self.mp = mp.solutions  # 显式初始化 mediapipe.solutions
        self.face_mesh = self.mp.face_mesh.FaceMesh(static_image_mode=False,
                                                         max_num_faces=1,
                                                         refine_landmarks=True,
                                                         min_detection_confidence=0.5,
                                                         min_tracking_confidence=0.5)
        self.mp_draw = mp.solutions.drawing_utils
        self.prev_nose_y = deque(maxlen=10)
        self.prev_nose_x = deque(maxlen=10)
        self.nod_threshold = 10
        self.shake_threshold = 10

        self.nod_count = 0
        self.shake_count = 0
        self.no_gesture_count = 0
        self.confirm_threshold = 3

        self.recent_gestures = deque(maxlen=20)

        self.current_gesture = "无动作"  # 共享给外部调用的当前动作
        self.lock = threading.Lock()

        self.running = True

    def run(self):
        cap = cv2.VideoCapture(0)
        print("[视觉交互] 实时检测启动，按 ESC 或点击 × 退出窗口")

        while self.running:
            ret, frame = cap.read()
            if not ret:
                break

            h, w = frame.shape[:2]
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb)

            detected_gesture = "无动作"
            gaze_direction = "未知"

            if results.multi_face_landmarks:
                face_landmarks = results.multi_face_landmarks[0]
                nose = face_landmarks.landmark[1]
                nose_x, nose_y = int(nose.x * w), int(nose.y * h)
                self.prev_nose_y.append(nose_y)
                self.prev_nose_x.append(nose_x)

                nod_detected = False
                if len(self.prev_nose_y) == 10:
                    dy = max(self.prev_nose_y) - min(self.prev_nose_y)
                    if dy > self.nod_threshold:
                        nod_detected = True

                shake_detected = False
                if len(self.prev_nose_x) == 10:
                    dx = max(self.prev_nose_x) - min(self.prev_nose_x)
                    if dx > self.shake_threshold:
                        shake_detected = True

                if nod_detected:
                    self.nod_count += 1
                else:
                    self.nod_count = 0

                if shake_detected:
                    self.shake_count += 1
                else:
                    self.shake_count = 0

                if not nod_detected and not shake_detected:
                    self.no_gesture_count += 1
                else:
                    self.no_gesture_count = 0

                if self.nod_count >= self.confirm_threshold:
                    detected_gesture = "点头 (确认)"
                    self.shake_count = 0
                    self.no_gesture_count = 0
                elif self.shake_count >= self.confirm_threshold:
                    detected_gesture = "摇头 (拒绝)"
                    self.nod_count = 0
                    self.no_gesture_count = 0
                elif self.no_gesture_count >= self.confirm_threshold:
                    found_recent = False
                    for past_gesture in reversed(self.recent_gestures):
                        if past_gesture != "无动作":
                            detected_gesture = past_gesture + " (最近有效)"
                            found_recent = True
                            break
                    if not found_recent:
                        detected_gesture = "无动作"
                    self.nod_count = 0
                    self.shake_count = 0

                left_eye = face_landmarks.landmark[33]
                right_eye = face_landmarks.landmark[263]
                eye_center_x = int((left_eye.x + right_eye.x) / 2 * w)
                if eye_center_x < w * 0.4:
                    gaze_direction = "注视左侧"
                elif eye_center_x > w * 0.6:
                    gaze_direction = "注视右侧"
                else:
                    gaze_direction = "注视中央"

                self.mp_draw.draw_landmarks(frame, face_landmarks, mp.solutions.face_mesh.FACEMESH_CONTOURS)
            else:
                self.nod_count = 0
                self.shake_count = 0
                self.no_gesture_count += 1
                if self.no_gesture_count >= self.confirm_threshold:
                    found_recent = False
                    for past_gesture in reversed(self.recent_gestures):
                        if past_gesture != "无动作":
                            detected_gesture = past_gesture + " (最近有效)"
                            found_recent = True
                            break
                    if not found_recent:
                        detected_gesture = "无动作"

            simple_gesture = "无动作"
            if "点头" in detected_gesture:
                simple_gesture = "点头(确认)"
            elif "摇头" in detected_gesture:
                simple_gesture = "摇头（拒绝）"
            self.recent_gestures.append(simple_gesture)

            # 更新共享变量
            with self.lock:
                self.current_gesture = detected_gesture

            # 显示窗口（可选，main.py里可去掉）
            frame = put_chinese_text(frame, f"头部动作: {detected_gesture}", (10, 30), font_size=30, color=(0, 255, 0))
            frame = put_chinese_text(frame, f"目光方向: {gaze_direction}", (10, 70), font_size=30, color=(0, 128, 255))
            cv2.imshow("视觉交互演示", frame)

            key = cv2.waitKey(1)
            if key == 27 or cv2.getWindowProperty("视觉交互演示", cv2.WND_PROP_VISIBLE) < 1:
                break

        cap.release()
        cv2.destroyAllWindows()
        return simple_gesture


    def get_current_gesture(self):
        with self.lock:
            return self.current_gesture

    def stop(self):
        self.running = False