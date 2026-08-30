import math


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

def classify_movement(history, threshold=20, lookback=10):
    # butuh riwayat cukup panjang buat dibandingkan
    if len(history) < 2:
        return "STILL"

    # ambil posisi lama (beberapa frame ke belakang) dan posisi terbaru
    x_baru = history[-1][0]                    # [-1] = terakhir, [0] = ambil x
    x_lama = history[-min(lookback, len(history))][0]

    dx = x_baru - x_lama                       # selisih = arah gerak

    if dx > threshold:
        return "RIGHT"
    elif dx < -threshold:
        return "LEFT"
    else:
        return "STILL"
def classify_approach(history, threshold=15, lookback=10):
    if len(history) < 2:
        return "STILL"

    h_baru = history[-1][2]                              # [2] = tinggi box
    h_lama = history[-min(lookback, len(history))][2]

    dh = h_baru - h_lama                                 # selisih tinggi

    if dh > threshold:
        return "APPROACHING"      # box membesar = mendekat
    elif dh < -threshold:
        return "MOVING AWAY"      # box mengecil = menjauh
    else:
        return "STILL"
def calculate_speed(history, lookback=10):
    if len(history) < 2:
        return 0.0

    n = min(lookback, len(history))
    titik_baru = history[-1][:2]        # (x, y) — buang h
    titik_lama = history[-n][:2]

    jarak = math.dist(titik_lama, titik_baru)   # √(dx² + dy²) otomatis
    return jarak / n                             # pixel per frame