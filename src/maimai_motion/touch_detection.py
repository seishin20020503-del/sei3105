"""Detect 'touch' events: moments a hand is relatively still, inferred as
contact with the touch panel or a held note.
"""
from dataclasses import dataclass

from .geometry import Point, dist


@dataclass
class TouchEvent:
    time_sec: float
    position: Point
    start_frame_pos: int  # index into the trajectory arrays where the dwell started
    end_frame_pos: int  # index into the trajectory arrays where the dwell ended (inclusive)


def _smoothed_speeds(times: list[float], positions: list[Point], smoothing_window: int = 3) -> list[float]:
    n = len(times)
    raw = [0.0] * n
    for i in range(1, n):
        dt = times[i] - times[i - 1]
        raw[i] = dist(positions[i], positions[i - 1]) / dt if dt > 0 else 0.0
    if smoothing_window <= 1:
        return raw
    half = smoothing_window // 2
    smoothed = []
    for i in range(n):
        lo = max(0, i - half)
        hi = min(n, i + half + 1)
        smoothed.append(sum(raw[lo:hi]) / (hi - lo))
    return smoothed


def detect_touch_events(
    times: list[float],
    positions: list[Point],
    speed_threshold: float,
    min_dwell_frames: int = 1,
) -> list[TouchEvent]:
    """Find contiguous stretches where the hand's speed stays below
    ``speed_threshold`` and report one :class:`TouchEvent` per stretch,
    positioned at the mean of the dwell.
    """
    if len(times) < 2:
        return []
    speeds = _smoothed_speeds(times, positions)
    events: list[TouchEvent] = []
    n = len(times)
    i = 0
    while i < n:
        if speeds[i] <= speed_threshold:
            j = i
            while j < n and speeds[j] <= speed_threshold:
                j += 1
            if (j - i) >= min_dwell_frames:
                mid = (i + j - 1) // 2
                avg_x = sum(p[0] for p in positions[i:j]) / (j - i)
                avg_y = sum(p[1] for p in positions[i:j]) / (j - i)
                events.append(
                    TouchEvent(
                        time_sec=times[mid],
                        position=(avg_x, avg_y),
                        start_frame_pos=i,
                        end_frame_pos=j - 1,
                    )
                )
            i = j
        else:
            i += 1
    return events
