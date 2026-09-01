# Human Tracking

The first step toward a person-following robot: detect a person from a webcam,
keep a stable ID across frames, and understand **where** they are, **how far**,
and **how they are moving**. This is the **sense → track → decide** part of a
robot control loop — the **act** part needs hardware and comes later.

Part of my path toward robotics and embodied AI.

![Demo](demo.gif)

*Tracking a single person: stable ID, movement direction, approach detection,
speed, and motion trail — running at ~25 FPS on CPU.*

## Features

- **Person detection** — MediaPipe pose landmarks, wrapped in a reusable detector class
- **Centroid tracking** — the same person keeps the same ID across frames, with tolerance for brief detection dropouts
- **Position** — `LEFT` / `CENTER` / `RIGHT` from the box center
- **Distance** — `NEAR` / `FAR` from the box height
- **Movement direction** — `LEFT` / `RIGHT` / `STILL` from horizontal displacement over time
- **Approach detection** — `APPROACHING` / `MOVING AWAY` from how the box height changes
- **Speed** — pixels per frame, from the magnitude of the displacement vector
- **Motion trail** — the last 30 positions drawn as a path
- **Entry counter** — how many tracks have entered the frame

Position and distance answer *where someone is now*. Direction, approach, and
speed answer *where they are heading* — which is what a following robot
actually needs in order to anticipate rather than react.

## Scope

**Feature set is frozen at v0.2.** The remaining work is stabilisation and
polish — bug fixes, display cleanup, refactoring, and a demo — not new
capability.

Ideas parked for later, deliberately not built:

- Multi-person tracking (requires a different detector than `mp.solutions.pose`)
- Re-identification, so a returning person keeps their original ID
- Smoothing the position signal further to reduce residual jitter
- Zone-based logic (entry/exit lines, dwell time per region)
- Hardware output — the **act** half of the loop

## How it works

Each frame runs three stages:

    SENSE    pose_detector.py    detect the person, compute a bounding box
    TRACK    tracker.py          match to the nearest known centroid, assign/keep an ID,
                                 store position history (sliding window of 30 frames)
    DECIDE   decision.py         classify position, distance, direction, approach, speed

Movement is derived from the stored history rather than a single frame. The
displacement between an older and a newer position, `(dx, dy)`, gives both the
direction of travel and — through its magnitude — the speed.

Thresholds use **ratios of the frame** rather than fixed pixels, so behaviour
holds at any resolution:

| Signal | Rule | Result |
|--------|------|--------|
| center x < 33% width | left third | `LEFT` |
| center x > 66% width | right third | `RIGHT` |
| box height > 60% frame height | large box = close | `NEAR` |
| dx over ~10 frames > 20px | moved horizontally | `LEFT` / `RIGHT` |
| box height grew > 15px | getting larger | `APPROACHING` |

Height (not width) drives distance because body height stays stable while arm
movements change width.

## Known limitations

Tested across distance, lighting, motion speed, framing, direction changes, and
re-entry. What holds and what breaks:

| Condition | Result |
|-----------|--------|
| Close and far range | Works — detection and ID stable |
| Low light | **Fails** — no detection. An RGB camera has no signal to work with; a learned model still needs visible input |
| Fast motion | Works — speed rises, trail stays connected |
| Diagonal motion | Works — direction and approach are read independently |
| Sudden direction change | No perceptible lag, despite comparing against a 10-frame-old position |
| Partial body (upper body only) | Works — landmarks below `visibility < 0.5` are excluded, so estimated joints no longer inflate the box |
| Leaving and re-entering frame | New ID assigned; the entry counter increments |
| Two people | Only one tracked — `mp.solutions.pose` detects a single person by design; the tracker itself handles multiple IDs |
| ID swap when two people cross | Untested — cannot occur with a single-person detector |

Two consequences worth being explicit about:

- **There is no re-identification.** An ID is a session-local label, not an
  identity. Someone who leaves and returns is counted as a new entry, so the
  counter measures *entries*, not *distinct people*.
- **The tracking threshold (`max_distance = 200`) is deliberately loose**
  because the pose bounding box is itself jittery — landmark noise moves the
  centroid more than the person does. A tighter threshold caused IDs to
  increment on almost every frame.

## Project structure

    human-tracking/
    ├── src/
    │   ├── pose_detector.py    # SENSE  — detection, visibility-filtered bounding box
    │   ├── tracker.py          # TRACK  — centroid matching, IDs, position history
    │   ├── decision.py         # DECIDE — position, distance, direction, approach, speed
    │   └── main.py             # capture loop, drawing, error handling
    ├── requirements.txt
    └── .gitignore

## Setup

    py -3.12 -m venv env
    .\env\Scripts\Activate.ps1
    pip install -r requirements.txt

## Run

    python src/main.py

Press `q` to quit.

## Roadmap

- **v0.1** — position and distance from a webcam
- **v0.2** — ID tracking, movement direction, approach, speed, trail, entry counter *(current)*
- **Later** — smooth the position signal further; connect to hardware for actual following

## Tech

Python 3.12 · OpenCV · MediaPipe · NumPy
