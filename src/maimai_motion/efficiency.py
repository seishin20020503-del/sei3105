"""Movement-efficiency metrics between consecutive touch events.

For each pair of consecutive touches, we compare the straight-line
distance between them (the theoretical minimum) against the actual
path length the hand traced. The difference is "wasted" movement.
"""
from dataclasses import dataclass

from .geometry import Point, dist
from .touch_detection import TouchEvent


@dataclass
class SegmentEfficiency:
    from_event: TouchEvent
    to_event: TouchEvent
    straight_distance: float
    actual_distance: float

    @property
    def excess_distance(self) -> float:
        return self.actual_distance - self.straight_distance

    @property
    def efficiency_ratio(self) -> float | None:
        if self.straight_distance < 1e-6:
            return None
        return self.actual_distance / self.straight_distance


def compute_segment_efficiencies(
    times: list[float],
    positions: list[Point],
    events: list[TouchEvent],
) -> list[SegmentEfficiency]:
    segments = []
    for prev, cur in zip(events, events[1:]):
        start = prev.end_frame_pos
        end = cur.start_frame_pos
        actual = 0.0
        for i in range(start, end):
            actual += dist(positions[i], positions[i + 1])
        straight = dist(prev.position, cur.position)
        segments.append(SegmentEfficiency(prev, cur, straight, actual))
    return segments


def worst_segments(segments: list[SegmentEfficiency], top_n: int = 5) -> list[SegmentEfficiency]:
    return sorted(segments, key=lambda s: s.excess_distance, reverse=True)[:top_n]
