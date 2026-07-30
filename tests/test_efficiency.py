import math

from maimai_motion.efficiency import compute_segment_efficiencies, worst_segments
from maimai_motion.touch_detection import TouchEvent


def test_straight_line_movement_has_ratio_close_to_one():
    times = [0.0, 1.0, 2.0]
    positions = [(0.0, 0.0), (50.0, 0.0), (100.0, 0.0)]
    events = [
        TouchEvent(time_sec=0.0, position=(0.0, 0.0), start_frame_pos=0, end_frame_pos=0),
        TouchEvent(time_sec=2.0, position=(100.0, 0.0), start_frame_pos=2, end_frame_pos=2),
    ]
    segments = compute_segment_efficiencies(times, positions, events)
    assert len(segments) == 1
    seg = segments[0]
    assert math.isclose(seg.straight_distance, 100.0)
    assert math.isclose(seg.actual_distance, 100.0)
    assert math.isclose(seg.excess_distance, 0.0, abs_tol=1e-9)
    assert math.isclose(seg.efficiency_ratio, 1.0)


def test_detour_produces_excess_distance():
    # hand goes from (0,0) up to (0,50) and back down to (50,0) instead of
    # a direct diagonal path
    times = [0.0, 1.0, 2.0]
    positions = [(0.0, 0.0), (0.0, 50.0), (50.0, 0.0)]
    events = [
        TouchEvent(time_sec=0.0, position=(0.0, 0.0), start_frame_pos=0, end_frame_pos=0),
        TouchEvent(time_sec=2.0, position=(50.0, 0.0), start_frame_pos=2, end_frame_pos=2),
    ]
    segments = compute_segment_efficiencies(times, positions, events)
    seg = segments[0]
    straight = math.hypot(50.0, 0.0)
    actual = 50.0 + math.hypot(50.0, 50.0)
    assert math.isclose(seg.straight_distance, straight)
    assert math.isclose(seg.actual_distance, actual)
    assert seg.excess_distance > 0
    assert seg.efficiency_ratio > 1.0


def test_zero_straight_distance_gives_none_ratio():
    times = [0.0, 1.0]
    positions = [(5.0, 5.0), (5.0, 5.0)]
    events = [
        TouchEvent(time_sec=0.0, position=(5.0, 5.0), start_frame_pos=0, end_frame_pos=0),
        TouchEvent(time_sec=1.0, position=(5.0, 5.0), start_frame_pos=1, end_frame_pos=1),
    ]
    segments = compute_segment_efficiencies(times, positions, events)
    assert segments[0].efficiency_ratio is None


def test_worst_segments_sorts_by_excess_distance_desc():
    events = [
        TouchEvent(time_sec=float(i), position=(float(i), 0.0), start_frame_pos=i, end_frame_pos=i)
        for i in range(4)
    ]
    times = [0.0, 1.0, 2.0, 3.0]
    positions = [(0.0, 0.0), (1.0, 10.0), (2.0, 0.0), (3.0, 0.0)]
    segments = compute_segment_efficiencies(times, positions, events)
    ranked = worst_segments(segments, top_n=2)
    assert len(ranked) == 2
    assert ranked[0].excess_distance >= ranked[1].excess_distance
