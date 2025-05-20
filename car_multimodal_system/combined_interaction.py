import cv2
import mediapipe as mp
import numpy as np
from collections import deque
from PIL import ImageFont, ImageDraw, Image

def put_chinese_text(img, text, pos, font_path="simsun.ttc", font_size=30, color=(0, 255, 0)):
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    font = ImageFont.truetype(font_path, font_size, encoding="utf-8")
    color_rgb = (color[2], color[1], color[0])
    draw.text(pos, text, font=font, fill=color_rgb)
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

class CombinedInteraction:
    def __init__(self):
        # Mediapipe 初始化
        self.mp = mp.solutions
        self.face_mesh = self.mp.face_mesh.FaceMesh(static_image_mode=False,
                                                    max_num_faces=1,
                                                    refine_landmarks=True,
                                                    min_detection_confidence=0.5,
                                                    min_tracking_confidence=0.5)
        self.hands = self.mp.hands.Hands(max_num_hands=1,
                                        min_detection_confidence=0.85,
                                        min_tracking_confidence=0.85)
        self.mp_draw = mp.solutions.drawing_utils

        # 面部动作参数
        self.prev_nose_y = deque(maxlen=10)
        self.prev_nose_x = deque(maxlen=10)
        self.nod_threshold = 30
        self.shake_threshold = 30
        self.nod_count = 0
        self.shake_count = 0
        self.no_gesture_count = 0
        self.confirm_threshold = 3
        self.recent_head_gestures = deque(maxlen=20)

        # 手势参数
        self.hand_x_history = deque(maxlen=10)
        self.recent_hand_gestures = deque(maxlen=5)

        # 新增：保存最近有效手势
        self.last_hand_gesture = "无手势"

    def detect_head_gesture(self, face_landmarks, w, h):
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

        detected_gesture = "无动作"
        if self.nod_count >= self.confirm_threshold:
            detected_gesture = "点头"
            self.shake_count = 0
            self.no_gesture_count = 0
        elif self.shake_count >= self.confirm_threshold:
            detected_gesture = "摇头"
            self.nod_count = 0
            self.no_gesture_count = 0
        elif self.no_gesture_count >= self.confirm_threshold:
            found_recent = False
            for past_gesture in reversed(self.recent_head_gestures):
                base_gesture = past_gesture.replace(" (最近有效)", "")
                if base_gesture != "无动作":
                    detected_gesture = base_gesture 
                    found_recent = True
                    break
            if not found_recent:
                detected_gesture = "无动作"

        # 保持队列干净，去掉后缀存储
        self.recent_head_gestures.append(detected_gesture.replace(" (最近有效)", ""))
        return detected_gesture

    def detect_gaze_direction(self, face_landmarks, w):
        left_eye = face_landmarks.landmark[33]
        right_eye = face_landmarks.landmark[263]
        eye_center_x = int((left_eye.x + right_eye.x) / 2 * w)
        if eye_center_x < w * 0.4:
            return "注视左侧"
        elif eye_center_x > w * 0.6:
            return "注视右侧"
        else:
            return "注视中央"

    def detect_hand_gesture(self, hand_landmarks, img_shape):
        h, w, _ = img_shape
        landmarks = [(int(lm.x * w), int(lm.y * h)) for lm in hand_landmarks.landmark]

        palm_x = landmarks[0][0]
        self.hand_x_history.append(palm_x)

        fingers = []
        # 大拇指判断：右手，拇指尖x>拇指第二节x表示伸出
        fingers.append(int(landmarks[4][0] > landmarks[3][0]))

        tips = [8, 12, 16, 20]
        joints = [6, 10, 14, 18]
        for tip, joint in zip(tips, joints):
            fingers.append(int(landmarks[tip][1] < landmarks[joint][1]))

        if sum(fingers) == 0:
            return "握拳"
        if fingers[0] == 1 and sum(fingers[1:]) == 0:
            return "竖起大拇指"
        if self.is_hand_shaking():
            return "摇手"
        return "未知手势"

    def is_hand_shaking(self):
        if len(self.hand_x_history) < 10:
            return False
        x_vals = list(self.hand_x_history)
        return max(x_vals) - min(x_vals) > 40

    def run(self):
        cap = cv2.VideoCapture(0)
        print("[多模态交互] 实时检测启动，按 ESC 或点击 × 退出窗口")

        while True:
            ret, frame = cap.read()
            if not ret:
                print("[多模态交互] 无法读取摄像头")
                break

            h, w = frame.shape[:2]
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            face_results = self.face_mesh.process(rgb)
            hand_results = self.hands.process(rgb)

            head_gesture = "无动作"
            gaze_direction = "未知"
            # 默认使用上次手势，避免手消失时闪变
            hand_gesture = self.last_hand_gesture

            # 处理面部
            if face_results.multi_face_landmarks:
                face_landmarks = face_results.multi_face_landmarks[0]
                head_gesture = self.detect_head_gesture(face_landmarks, w, h)
                gaze_direction = self.detect_gaze_direction(face_landmarks, w)
                self.mp_draw.draw_landmarks(frame, face_landmarks, self.mp.face_mesh.FACEMESH_CONTOURS)
            else:
                # 重置计数，防止动作残留
                self.nod_count = 0
                self.shake_count = 0
                self.no_gesture_count += 1

            # 处理手势
            if hand_results.multi_hand_landmarks:
                hand_landmarks = hand_results.multi_hand_landmarks[0]
                current_hand_gesture = self.detect_hand_gesture(hand_landmarks, frame.shape)
                self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp.hands.HAND_CONNECTIONS)
                self.last_hand_gesture = current_hand_gesture  # 更新最新手势
                hand_gesture = current_hand_gesture

            # 显示信息
            frame = put_chinese_text(frame, f"头部动作: {head_gesture}", (10, 30), font_size=30, color=(0, 255, 0))
            frame = put_chinese_text(frame, f"目光方向: {gaze_direction}", (10, 70), font_size=30, color=(0, 128, 255))
            frame = put_chinese_text(frame, f"手势: {hand_gesture}", (10, 110), font_size=30, color=(255, 128, 0))

            cv2.imshow("多模态视觉交互", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == 27 or cv2.getWindowProperty("多模态视觉交互", cv2.WND_PROP_VISIBLE) < 1:
                break

        cap.release()
        cv2.destroyAllWindows()
        return hand_gesture, head_gesture

if __name__ == "__main__":
    multi_modal = CombinedInteraction()
    gesture_result, vision_result = multi_modal.run()
