from maimai_motion.chart import Note
from maimai_motion.timing import match_notes_to_touches
from maimai_motion.touch_detection import TouchEvent


def _touch(t, x=0.0, y=0.0):
    return TouchEvent(time_sec=t, position=(x, y), start_frame_pos=0, end_frame_pos=0)


def test_matches_within_window_and_computes_delta():
    notes = [Note(time_sec=1.0, hand="left"), Note(time_sec=2.0, hand="left")]
    touches = [_touch(1.05), _touch(1.9)]
    matches = match_notes_to_touches(notes, touches, max_window_sec=0.5)
    assert len(matches) == 2
    m0 = next(m for m in matches if m.note.time_sec == 1.0)
    m1 = next(m for m in matches if m.note.time_sec == 2.0)
    assert abs(m0.delta_sec - 0.05) < 1e-9  # touched late
    assert abs(m1.delta_sec - (-0.1)) < 1e-9  # touched early


def test_notes_outside_window_are_unmatched():
    notes = [Note(time_sec=1.0, hand="left")]
    touches = [_touch(5.0)]
    matches = match_notes_to_touches(notes, touches, max_window_sec=0.5)
    assert matches == []


def test_each_touch_used_at_most_once():
    notes = [Note(time_sec=1.0), Note(time_sec=1.05)]
    touches = [_touch(1.02)]
    matches = match_notes_to_touches(notes, touches, max_window_sec=0.5)
    assert len(matches) == 1
