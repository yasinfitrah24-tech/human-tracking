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

    def bounding_box(self, frame, min_visibility=0.5):
        if self.hasil is None or not self.hasil.pose_landmarks:
            return None
        tinggi, lebar, _ = frame.shape

        xs, ys = [], []
        for lm in self.hasil.pose_landmarks.landmark:
            if lm.visibility < min_visibility:     # buang landmark tebakan
                continue
            xs.append(lm.x * lebar)
            ys.append(lm.y * tinggi)

        if len(xs) < 2:                            # nggak cukup titik valid
            return None

        return int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))