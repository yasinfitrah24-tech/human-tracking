import time

import cv2

from pose_detector import PoseDetector
from tracker import CentroidTracker
from decision import (classify_position, classify_distance,
                      classify_movement, classify_approach, calculate_speed)

# ---------- colours: one meaning per colour ----------
BOX   = (0, 200, 0)          # detection box, centroid
LABEL = (0, 200, 0)          # label background
TEXT  = (255, 255, 255)      # text on coloured background
TRAIL = (200, 100, 255)      # motion trail
PANEL = (255, 220, 100)      # info panel text

FONT = cv2.FONT_HERSHEY_SIMPLEX


def draw_label(frame, text, x, y):
    """Draw text on a filled background anchored above (x, y)."""
    (tw, th), _ = cv2.getTextSize(text, FONT, 0.5, 1)
    cv2.rectangle(frame, (x, y - th - 8), (x + tw + 8, y), LABEL, -1)
    cv2.putText(frame, text, (x + 4, y - 5), FONT, 0.5, TEXT, 1, cv2.LINE_AA)


def draw_panel(frame, lines):
    """Draw a semi-transparent info panel in the top-left corner."""
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (210, 20 + 22 * len(lines)), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.45, frame, 0.55, 0, frame)
    for i, line in enumerate(lines):
        cv2.putText(frame, line, (20, 35 + 22 * i), FONT, 0.5, PANEL, 1, cv2.LINE_AA)


detector = PoseDetector()
tracker = CentroidTracker(max_distance=200)
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Error: Cannot open webcam. Check if it's connected or used by another app.")
    exit()

prev_time = time.time()

try:
    while True:
        ret, frame = camera.read()
        if not ret:
            print("Warning: Failed to read frame. Stopping.")
            break

        frame_height, frame_width, _ = frame.shape
        centroids, heights, boxes = [], [], []

        # ---------- SENSE ----------
        if detector.detect(frame):
            box = detector.bounding_box(frame)
            if box:
                x1, y1, x2, y2 = box
                centroids.append(((x1 + x2) // 2, (y1 + y2) // 2))
                heights.append(y2 - y1)
                boxes.append(box)

        # ---------- TRACK ----------
        tracked = tracker.update(centroids, heights)

        # ---------- FPS ----------
        now = time.time()
        fps = 1 / (now - prev_time) if now > prev_time else 0
        prev_time = now

        # ---------- DRAW: trail ----------
        for points in tracker.history.values():
            for i in range(1, len(points)):
                cv2.line(frame, points[i - 1][:2], points[i][:2], TRAIL, 2)

        # ---------- DRAW: boxes ----------
        for (x1, y1, x2, y2) in boxes:
            cv2.rectangle(frame, (x1, y1), (x2, y2), BOX, 2)

        # ---------- DRAW: per-person label ----------
        for obj_id, (cx, cy) in tracked.items():
            cv2.circle(frame, (cx, cy), 4, BOX, -1)

            history = tracker.history.get(obj_id, [])
            movement = classify_movement(history)
            approach = classify_approach(history)
            speed = calculate_speed(history)
            label = f"ID {obj_id}  {movement}  {approach}  {speed:.1f}px/f"

            anchor_x, anchor_y = (boxes[0][0], boxes[0][1]) if boxes else (cx, cy)
            draw_label(frame, label, anchor_x, anchor_y)

        # ---------- DRAW: info panel ----------
        if boxes:
            bx1, by1, bx2, by2 = boxes[0]
            position = classify_position((bx1 + bx2) // 2, frame_width)
            distance = classify_distance(by2 - by1, frame_height)
        else:
            position = distance = "-"

        draw_panel(frame, [
            f"Position : {position}",
            f"Distance : {distance}",
            f"Entries  : {tracker.next_id}",
            f"FPS      : {fps:.1f}",
        ])

        cv2.imshow("Human Tracking", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

except Exception as e:
    print(f"Unexpected error: {e}")

finally:
    camera.release()
    cv2.destroyAllWindows()
    print("Camera released. Exit clean.")