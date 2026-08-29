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