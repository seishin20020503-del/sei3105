"""Convert per-frame hand landmarks into a single reference-point trajectory."""
from .geometry import Point
from .hand_tracker import HandFrame

# MediaPipe Hands landmark indices, for reference:
#   0 = wrist, 4 = thumb tip, 8 = index tip, 12 = middle tip, 16 = ring tip, 20 = pinky tip
WRIST = 0
INDEX_TIP = 8


def reference_trajectory(
    frames: list[HandFrame],
    landmark_index: int = WRIST,
    width: int = 1,
    height: int = 1,
) -> tuple[list[float], list[Point]]:
    """Pull out one landmark's (x, y) position (in pixel space) over time."""
    times: list[float] = []
    positions: list[Point] = []
    for f in frames:
        x, y, _z = f.landmarks[landmark_index]
        times.append(f.time_sec)
        positions.append((x * width, y * height))
    return times, positions
