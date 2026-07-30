from maimai_motion.touch_detection import detect_touch_events


def _linspace_positions(start, end, n):
    x0, y0 = start
    x1, y1 = end
    return [
        (x0 + (x1 - x0) * i / (n - 1), y0 + (y1 - y0) * i / (n - 1))
        for i in range(n)
    ]


def test_detects_two_dwell_regions():
    fps = 30
    dt = 1 / fps
    times = [i * dt for i in range(20)]

    move1 = _linspace_positions((0, 0), (100, 100), 5)
    hold1 = [(100, 100)] * 5
    move2 = _linspace_positions((100, 100), (200, 50), 5)
    hold2 = [(200, 50)] * 5
    positions = move1 + hold1 + move2 + hold2

    events = detect_touch_events(times, positions, speed_threshold=1e-6)

    assert len(events) == 2
    assert events[0].position == (100, 100)
    assert events[1].position == (200, 50)
    # smoothing blurs the exact boundary a little, but the dwell should
    # cover most of frames [5, 9] where the hand is stationary at (100, 100)
    assert 4 <= events[0].start_frame_pos <= 6
    assert events[0].end_frame_pos == 9


def test_no_dwell_returns_no_events_when_always_moving():
    times = [i / 30 for i in range(10)]
    positions = _linspace_positions((0, 0), (900, 900), 10)
    events = detect_touch_events(times, positions, speed_threshold=1.0)
    assert events == []


def test_short_input_returns_no_events():
    assert detect_touch_events([0.0], [(0.0, 0.0)], speed_threshold=1.0) == []
    assert detect_touch_events([], [], speed_threshold=1.0) == []


def test_min_dwell_frames_filters_brief_pauses():
    times = [i / 30 for i in range(6)]
    positions = [(0, 0), (0, 0), (10, 10), (20, 20), (30, 30), (30, 30)]
    events = detect_touch_events(times, positions, speed_threshold=1e-6, min_dwell_frames=3)
    # neither dwell region is 3+ frames long, so nothing should be reported
    assert events == []
