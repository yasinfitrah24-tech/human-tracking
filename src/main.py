import cv2
from pose_detector import PoseDetector
from tracker import CentroidTracker          # ← import tracker
from decision import classify_position, classify_distance   # ← import dari modul baru


detector = PoseDetector()
tracker = CentroidTracker(max_distance=200)    # ← memori antar-frame
camera = cv2.VideoCapture(0)
if not camera.isOpened():
    print("Error: Cannot open webcam. Check if it's connected or used by another app.")
    exit()

try:
    while True:
        ret, frame = camera.read()
        if not ret:
            break

        frame_height, frame_width, _ = frame.shape
        centroids = []                            # centroid deteksi frame ini
        boxes = []  

        if detector.detect(frame):                # SENSE
            box = detector.bounding_box(frame)
            if box:
                x1, y1, x2, y2 = box
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                centroids.append((center_x, center_y))
                boxes.append(box)
        tracked = tracker.update(centroids)       # TRACK: cocokkan + kasih ID
        # gambar tiap orang yang ke-track
        for obj_id, (cx, cy) in tracked.items():
            cv2.circle(frame, (cx, cy), 8, (0, 0, 255), -1)
            cv2.putText(frame, f"Person {obj_id}", (cx - 40, cy - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        # gambar jejak (trail) tiap orang
        for obj_id, points in tracker.history.items():
            for i in range(1, len(points)):
                cv2.line(frame, points[i-1], points[i], (255, 0, 255), 2)
        # gambar box + keputusan posisi/jarak
        for (x1, y1, x2, y2) in boxes:
            position = classify_position((x1 + x2) // 2, frame_width)   # DECIDE
            distance = classify_distance(y2 - y1, frame_height)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"{position} - {distance}", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Human Tracking", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

except Exception as e:
    print(f"Unexpected error: {e}")

finally:
    camera.release()
    cv2.destroyAllWindows()
    print("Camera released. Exit clean.")
