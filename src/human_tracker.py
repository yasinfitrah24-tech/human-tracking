import cv2
from pose_detector import PoseDetector

def classify_position(center_x, frame_width):
    # decide: LEFT / CENTER / RIGHT from horizontal position
    if center_x < frame_width * 0.33:
        return "LEFT"
    elif center_x > frame_width * 0.66:
        return "RIGHT"
    else:
        return "CENTER"

def classify_distance(box_height, frame_height):
    # decide: NEAR / FAR from box height
    if box_height > frame_height * 0.6:
        return "NEAR"
    else:
        return "FAR"

detector = PoseDetector()
camera = cv2.VideoCapture(0)

while True:
    ret, frame = camera.read()
    if not ret:
        break

    frame_height, frame_width, _ = frame.shape

    if detector.detect(frame):                    # sense
        box = detector.bounding_box(frame)
        if box:
            x1, y1, x2, y2 = box
            center_x = (x1 + x2) // 2             # titik tengah x
            center_y = (y1 + y2) // 2             # titik tengah y
            box_height = y2 - y1                  # tinggi box

            position = classify_position(center_x, frame_width)    # decide
            distance = classify_distance(box_height, frame_height)  # decide

            # visual: box + titik tengah + teks keputusan
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.circle(frame, (center_x, center_y), 8, (0, 0, 255), -1)
            cv2.putText(frame, f"{position} - {distance}", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Human Tracking", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()