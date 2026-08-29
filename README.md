# Human Tracking

The first step toward a person-following robot: detect one person from a
webcam and decide **where** they are and **how far**. This is the
**sense → decide** half of a robot control loop — the **act** half needs
hardware and comes later.

Part of my path toward robotics and embodied AI.

## MVP v0.1 — scope

**In scope (this is "enough"):**
- Detect a single person (reusable `PoseDetector` class, MediaPipe pose)
- Compute the bounding-box center → horizontal position: `LEFT` / `CENTER` / `RIGHT`
- Compute the box height → distance: `NEAR` / `FAR`
- Overlay the decision as text + draw the center point for visual debugging

**Out of scope (deliberately excluded):**
- Multiple people
- Re-identification (recognizing the same person after they leave frame)
- Motor / robot control
- Recording, fancy UI, filters

## How the decision works

Positions use **ratios of the frame**, not fixed pixels, so it works at any resolution:

| Signal | Rule | Result |
|--------|------|--------|
| center x < 33% width | left third | `LEFT` |
| center x > 66% width | right third | `RIGHT` |
| otherwise | middle | `CENTER` |
| box height > 60% frame height | large box = close | `NEAR` |
| otherwise | | `FAR` |

Height (not width) is used for distance because body height stays stable while arm movements change width. The thresholds are tunable.

## Project structure

    human-tracking/
    ├── src/
    │   ├── pose_detector.py    # sense: reusable detector (detect / draw / bounding_box)
    │   └── human_tracker.py    # decide: position + distance classification
    ├── requirements.txt
    └── .gitignore

## Setup

    py -3.12 -m venv env
    .\env\Scripts\Activate.ps1
    pip install -r requirements.txt

## Run

    python src/human_tracker.py

Press `q` to quit.

## Roadmap

- **v0.1** — position + distance from a webcam *(current)*
- **v0.2** — smooth the signal over time (reduce jitter)
- **Later** — connect to hardware for actual following

## Tech

Python 3.12 · OpenCV · MediaPipe · NumPy
