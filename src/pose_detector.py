import cv2
import mediapipe as mp

class PoseDetector:
    def __init__(self, min_confidence=0.7):
        # SETUP sekali — disimpan jadi milik object (self)
        self.mp_pose = mp.solutions.pose
        self.mp_draw = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(min_detection_confidence=min_confidence)
        self.hasil = None                      # nyimpen hasil deteksi terakhir

    def detect(self, frame):
        # PROSES satu frame → balikin True/False (ada orang?)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.hasil = self.pose.process(rgb)
        return self.hasil.pose_landmarks is not None

    def draw(self, frame):
        # GAMBAR kerangka (kalau ada)
        if self.hasil.pose_landmarks:
            self.mp_draw.draw_landmarks(
                frame, self.hasil.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
        return frame

    def bounding_box(self, frame):
        # BONUS: kotak dari landmark (min/max, #47) — None kalau nggak ada
        if not self.hasil.pose_landmarks:
            return None
        tinggi, lebar, _ = frame.shape
        xs = [lm.x * lebar for lm in self.hasil.pose_landmarks.landmark]
        ys = [lm.y * tinggi for lm in self.hasil.pose_landmarks.landmark]
        return int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))